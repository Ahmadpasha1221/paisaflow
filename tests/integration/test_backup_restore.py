"""Integration tests for SQLite backup and safe restore operations."""

import sqlite3
from datetime import date
from pathlib import Path

import pytest

from paisaflow.application.services import AccountService, PersonService, TransactionService
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.backup.backup_service import BackupService
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


def test_backup_and_restore_cycle(tmp_path: Path):
    live_db = tmp_path / "live.db"
    backup_dir = tmp_path / "backups"

    engine = create_db_engine(db_path=live_db)
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))

    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    person = person_svc.create_person(name="Sunil")
    acct = account_svc.create_account(
        name="Emergency Savings",
        account_type=AccountType.SAVINGS,
        owner_person_id=person.id,
        opening_balance=Money(10000000),  # ₹1,00,000
    )

    backup_svc = BackupService(engine=engine, backup_dir=backup_dir)

    # Create backup snapshot
    backup_file = backup_svc.create_backup()
    assert backup_file.exists()
    assert backup_svc.validate_backup(backup_file) is True

    # Now add another transaction to the live database
    with uow:
        cat = next(c for c in uow.categories.get_all() if c.name == "Groceries")

    txn_svc.record_expense(
        transaction_date=date.today(),
        description="Big Bazaar",
        amount=Money(500000),  # ₹5,000
        account_id=acct.id,
        person_id=person.id,
        category_id=cat.id,
    )
    # Balance in live DB is now ₹95,000
    assert account_svc.get_account_by_id(acct.id).balance_paise == 9500000

    # Perform restore from the backup snapshot
    backup_svc.restore_backup(backup_file, target_db_path=live_db)

    # Reopen restored database
    restored_engine = create_db_engine(db_path=live_db)
    restored_uow = SqlAlchemyUnitOfWork(create_session_factory(restored_engine))
    restored_acct_svc = AccountService(restored_uow)

    # Account balance in restored database should be back to ₹1,00,000 (pre-expense snapshot)
    restored_acct = restored_acct_svc.get_account_by_id(acct.id)
    assert restored_acct.balance_paise == 10000000


def test_restore_safety_copy_includes_wal_data_and_clears_sidecars(tmp_path: Path):
    """Restore must snapshot pending WAL data and drop stale SQLite sidecars."""
    live_db = tmp_path / "live.db"
    engine = create_db_engine(db_path=live_db)
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))

    person = PersonService(uow).create_person(name="WAL User")
    acct = AccountService(uow).create_account(
        name="Wallet",
        account_type=AccountType.CASH,
        owner_person_id=person.id,
        opening_balance=Money(1000000),
    )
    with uow:
        cat = next(c for c in uow.categories.get_all() if c.name == "Groceries")

    txn_svc = TransactionService(uow)
    txn_svc.record_expense(
        date(2026, 10, 1), "Before backup", Money(100000), acct.id, person.id, cat.id
    )

    backup_svc = BackupService(engine=engine, backup_dir=tmp_path / "backups")
    backup_file = backup_svc.create_backup()

    # A later transaction that is deliberately absent from the backup snapshot.
    txn_svc.record_expense(
        date(2026, 10, 2), "After backup", Money(50000), acct.id, person.id, cat.id
    )

    backup_svc.restore_backup(backup_file, target_db_path=live_db)

    # The safety copy must capture the newest committed transaction (WAL included).
    safety_copies = list(tmp_path.glob("live.db.recovery_*"))
    assert len(safety_copies) == 1
    with sqlite3.connect(safety_copies[0]) as conn:
        preserved = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert preserved == 2

    # Stale sidecars from the replaced database must not survive the restore.
    assert not (tmp_path / "live.db-wal").exists()
    assert not (tmp_path / "live.db-shm").exists()

    # The restored database contains exactly the backup snapshot.
    with sqlite3.connect(live_db) as conn:
        restored_count = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert restored_count == 1


def test_validate_backup_rejects_incomplete_schema(tmp_path: Path):
    """An unrelated SQLite file must not be accepted as a restorable backup."""
    unrelated = tmp_path / "unrelated.db"
    with sqlite3.connect(unrelated) as conn:
        conn.execute("CREATE TABLE transactions (id INTEGER PRIMARY KEY)")

    backup_svc = BackupService(engine=create_db_engine(db_path=tmp_path / "other.db"))

    with pytest.raises(ValueError, match="missing tables"):
        backup_svc.validate_backup(unrelated)
