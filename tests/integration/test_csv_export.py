"""Integration tests for CSV transaction export."""

from datetime import date
from pathlib import Path

from paisaflow.application.services import AccountService, PersonService, TransactionService
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from paisaflow.infrastructure.export.csv_exporter import CsvExportService


def test_export_transactions_csv(tmp_path: Path):
    db_file = tmp_path / "export_test.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))

    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    person = person_svc.create_person(name="Deepak")
    acct = account_svc.create_account(
        name="Wallet",
        account_type=AccountType.CASH,
        owner_person_id=person.id,
        opening_balance=Money(50000),
    )

    with uow:
        cat = next(c for c in uow.categories.get_all() if c.name == "Food and Dining")

    txn_svc.record_expense(
        transaction_date=date(2026, 10, 25),
        description="Dinner with friends",
        amount=Money(120000),  # ₹1,200.00
        account_id=acct.id,
        person_id=person.id,
        category_id=cat.id,
        notes="Celebration dinner",
    )

    export_file = tmp_path / "transactions_export.csv"
    exporter = CsvExportService(uow)
    result = exporter.export_transactions(export_file)

    assert result.exists()
    content = result.read_text(encoding="utf-8")
    assert "Dinner with friends" in content
    assert "1,200.00" in content
    assert "Deepak" in content
    assert "Food and Dining" in content
    assert "Celebration dinner" in content
