"""Integration tests for SQLite backup and safe restore operations."""

from datetime import date
from pathlib import Path

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
