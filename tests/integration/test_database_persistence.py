"""Integration tests for database persistence, atomic operations, and ledger consistency."""

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine

from paisaflow.application.services import AccountService, PersonService, TransactionService
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.entities.transaction import PaymentMethod, TransactionType
from paisaflow.domain.exceptions import InvalidTransferError
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def test_db(tmp_path: Path) -> tuple[Engine, SqlAlchemyUnitOfWork]:
    db_file = tmp_path / "test_paisaflow.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    uow = SqlAlchemyUnitOfWork(session_factory)
    return engine, uow


def test_seed_categories_created_on_init(test_db):
    _, uow = test_db
    with uow:
        cats = uow.categories.get_all()
        # Verify default categories are seeded
        cat_names = [c.name for c in cats]
        assert "Salary" in cat_names
        assert "Groceries" in cat_names
        assert "Food and Dining" in cat_names


def test_create_person_and_account(test_db):
    _, uow = test_db
    person_svc = PersonService(uow)
    account_svc = AccountService(uow)

    person = person_svc.create_person(name="Aarav Sharma", color_code="#B8F28B")
    assert person.id > 0
    assert person.name == "Aarav Sharma"

    acct = account_svc.create_account(
        name="HDFC Savings",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(500000),  # ₹5,000 opening balance
    )
    assert acct.id > 0
    assert acct.balance_paise == 500000
    assert acct.balance_formatted == "₹5,000.00"


def test_atomic_income_and_expense_lifecycle(test_db):
    _, uow = test_db
    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    # 1. Setup Person & Account
    person = person_svc.create_person(name="Priya Patel")
    acct = account_svc.create_account(
        name="SBI Account",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(100000),  # ₹1,000
    )

    # Find salary category
    with uow:
        salary_cat = next(c for c in uow.categories.get_all() if c.name == "Salary")
        grocery_cat = next(c for c in uow.categories.get_all() if c.name == "Groceries")

    # 2. Record Income ₹25,000
    income_txn = txn_svc.record_income(
        transaction_date=date(2026, 10, 15),
        description="Monthly Salary",
        amount=Money(2500000),
        account_id=acct.id,
        person_id=person.id,
        category_id=salary_cat.id,
        payment_method=PaymentMethod.BANK_TRANSFER,
    )
    assert income_txn.amount_paise == 2500000

    # Verify updated account balance: 1,000 + 25,000 = 26,000
    updated_acct = account_svc.get_account_by_id(acct.id)
    assert updated_acct.balance_paise == 2600000
    assert updated_acct.balance_formatted == "₹26,000.00"

    # 3. Record Expense ₹3,500
    expense_txn = txn_svc.record_expense(
        transaction_date=date(2026, 10, 16),
        description="Weekly Groceries",
        amount=Money(350000),
        account_id=acct.id,
        person_id=person.id,
        category_id=grocery_cat.id,
        payment_method=PaymentMethod.UPI,
    )
    assert expense_txn.amount_paise == 350000

    # Verify updated account balance: 26,000 - 3,500 = 22,500
    updated_acct = account_svc.get_account_by_id(acct.id)
    assert updated_acct.balance_paise == 2250000
    assert updated_acct.balance_formatted == "₹22,500.00"


def test_atomic_transfer_between_accounts(test_db):
    _, uow = test_db
    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    person = person_svc.create_person(name="Vikram")
    bank = account_svc.create_account(
        name="Main Bank",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(5000000),  # ₹50,000
    )
    cash = account_svc.create_account(
        name="Wallet Cash",
        account_type=AccountType.CASH,
        owner_person_id=person.id,
        opening_balance=Money(200000),  # ₹2,000
    )

    # Transfer ₹5,000 from Bank to Cash
    transfer_txn = txn_svc.record_transfer(
        transaction_date=date(2026, 10, 20),
        description="ATM Withdrawal",
        amount=Money(500000),
        source_account_id=bank.id,
        dest_account_id=cash.id,
        person_id=person.id,
    )
    assert transfer_txn.transaction_type == TransactionType.TRANSFER.value

    bank_refreshed = account_svc.get_account_by_id(bank.id)
    cash_refreshed = account_svc.get_account_by_id(cash.id)

    # Bank: 50,000 - 5,000 = 45,000
    assert bank_refreshed.balance_paise == 4500000
    # Cash: 2,000 + 5,000 = 7,000
    assert cash_refreshed.balance_paise == 700000
    # Total combined assets remained invariant: 52,000
    assert bank_refreshed.balance_paise + cash_refreshed.balance_paise == 5200000


def test_transfer_fails_on_same_account(test_db):
    _, uow = test_db
    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    person = person_svc.create_person(name="Test User")
    bank = account_svc.create_account(
        name="Bank",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(100000),
    )

    with pytest.raises(InvalidTransferError, match="must be different"):
        txn_svc.record_transfer(
            transaction_date=date.today(),
            description="Invalid Self Transfer",
            amount=Money(10000),
            source_account_id=bank.id,
            dest_account_id=bank.id,
            person_id=person.id,
        )


def test_void_transaction_reverses_balance(test_db):
    _, uow = test_db
    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    person = person_svc.create_person(name="Ananya")
    acct = account_svc.create_account(
        name="ICICI Bank",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(1000000),  # ₹10,000
    )
    with uow:
        cat = next(c for c in uow.categories.get_all() if c.name == "Utilities")

    # Expense ₹1,500
    txn = txn_svc.record_expense(
        transaction_date=date.today(),
        description="Electricity Bill",
        amount=Money(150000),
        account_id=acct.id,
        person_id=person.id,
        category_id=cat.id,
    )
    assert account_svc.get_account_by_id(acct.id).balance_paise == 850000

    # Void the transaction
    txn_svc.void_transaction(txn.id)

    # Balance must be exactly restored to ₹10,000!
    assert account_svc.get_account_by_id(acct.id).balance_paise == 1000000


def test_persistence_survives_db_reopen(tmp_path: Path):
    db_file = tmp_path / "persistent_test.db"
    engine1 = create_db_engine(db_path=db_file)
    initialize_database(engine1)
    uow1 = SqlAlchemyUnitOfWork(create_session_factory(engine1))

    person_svc1 = PersonService(uow1)
    account_svc1 = AccountService(uow1)
    txn_svc1 = TransactionService(uow1)

    person = person_svc1.create_person(name="Kiran Rao")
    acct = account_svc1.create_account(
        name="Axis Bank",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(2000000),  # ₹20,000
    )
    with uow1:
        cat = next(c for c in uow1.categories.get_all() if c.name == "Shopping")

    txn_svc1.record_expense(
        transaction_date=date(2026, 10, 1),
        description="Festive Clothes",
        amount=Money(400000),
        account_id=acct.id,
        person_id=person.id,
        category_id=cat.id,
    )

    # Close connection completely
    engine1.dispose()

    # Reopen database afresh with new engine
    engine2 = create_db_engine(db_path=db_file)
    uow2 = SqlAlchemyUnitOfWork(create_session_factory(engine2))

    account_svc2 = AccountService(uow2)
    txn_svc2 = TransactionService(uow2)

    acct_reopened = account_svc2.get_account_by_id(acct.id)
    assert acct_reopened is not None
    assert acct_reopened.name == "Axis Bank"
    # 20,000 - 4,000 = 16,000
    assert acct_reopened.balance_paise == 1600000
    assert acct_reopened.balance_formatted == "₹16,000.00"

    txns, total = txn_svc2.query_transactions()
    assert total == 1
    assert txns[0].description == "Festive Clothes"
