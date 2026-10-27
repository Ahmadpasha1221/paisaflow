"""Regression tests for financial input guards in the application services.

Covers defects found during the release audit:
  * transactions posted against a mismatched or archived category
  * transactions attributed to a non-existent person
  * debt repayments that overpay, target a settled debt, or are non-positive
"""

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import Engine

from paisaflow.application.services import (
    AccountService,
    DebtService,
    PersonService,
    TransactionService,
)
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.entities.debt import DebtType
from paisaflow.domain.exceptions import (
    CategoryArchivedError,
    EntityNotFoundError,
    IncompatibleCategoryError,
    InvalidDebtPaymentError,
)
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


@pytest.fixture
def test_db(tmp_path: Path) -> tuple[Engine, SqlAlchemyUnitOfWork]:
    db_file = tmp_path / "guards.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    return engine, SqlAlchemyUnitOfWork(session_factory)


def _setup_person_and_account(uow: SqlAlchemyUnitOfWork):
    person = PersonService(uow).create_person(name="Audit User")
    acct = AccountService(uow).create_account(
        name="Audit Bank",
        account_type=AccountType.BANK,
        owner_person_id=person.id,
        opening_balance=Money(1000000),
    )
    return person, acct


def _category_id(uow: SqlAlchemyUnitOfWork, name: str) -> int:
    with uow:
        return next(c for c in uow.categories.get_all() if c.name == name).id


def test_expense_rejected_for_income_category(test_db):
    _, uow = test_db
    person, acct = _setup_person_and_account(uow)
    salary_cat_id = _category_id(uow, "Salary")  # an INCOME category

    with pytest.raises(IncompatibleCategoryError, match="income category"):
        TransactionService(uow).record_expense(
            transaction_date=date(2026, 10, 20),
            description="Should be rejected",
            amount=Money(50000),
            account_id=acct.id,
            person_id=person.id,
            category_id=salary_cat_id,
        )

    # The rejected transaction must not have affected the ledger.
    assert AccountService(uow).get_account_by_id(acct.id).balance_paise == 1000000


def test_income_rejected_for_expense_category(test_db):
    _, uow = test_db
    person, acct = _setup_person_and_account(uow)
    groceries_cat_id = _category_id(uow, "Groceries")  # an EXPENSE category

    with pytest.raises(IncompatibleCategoryError, match="expense category"):
        TransactionService(uow).record_income(
            transaction_date=date(2026, 10, 20),
            description="Should be rejected",
            amount=Money(50000),
            account_id=acct.id,
            person_id=person.id,
            category_id=groceries_cat_id,
        )

    assert AccountService(uow).get_account_by_id(acct.id).balance_paise == 1000000


def test_transaction_rejected_for_archived_category(test_db):
    _, uow = test_db
    person, acct = _setup_person_and_account(uow)

    with uow:
        cat = next(c for c in uow.categories.get_all() if c.name == "Groceries")
        cat.is_archived = True
        uow.categories.update(cat)
        uow.commit()
        archived_cat_id = cat.id

    with pytest.raises(CategoryArchivedError, match="archived"):
        TransactionService(uow).record_expense(
            transaction_date=date(2026, 10, 20),
            description="Archived category",
            amount=Money(50000),
            account_id=acct.id,
            person_id=person.id,
            category_id=archived_cat_id,
        )


def test_transaction_rejected_for_missing_person(test_db):
    _, uow = test_db
    _, acct = _setup_person_and_account(uow)
    groceries_cat_id = _category_id(uow, "Groceries")

    with pytest.raises(EntityNotFoundError, match="Person"):
        TransactionService(uow).record_expense(
            transaction_date=date(2026, 10, 20),
            description="Ghost person",
            amount=Money(50000),
            account_id=acct.id,
            person_id=999999,
            category_id=groceries_cat_id,
        )


def test_transfer_rejected_for_missing_person(test_db):
    _, uow = test_db
    _, acct = _setup_person_and_account(uow)
    other = AccountService(uow).create_account(
        name="Second Bank",
        account_type=AccountType.BANK,
        owner_person_id=PersonService(uow).get_people()[0].id,
        opening_balance=Money(0),
    )

    with pytest.raises(EntityNotFoundError, match="Person"):
        TransactionService(uow).record_transfer(
            transaction_date=date(2026, 10, 20),
            description="Ghost transfer",
            amount=Money(10000),
            source_account_id=acct.id,
            dest_account_id=other.id,
            person_id=999999,
        )


def test_debt_overpayment_rejected_and_balance_preserved(test_db):
    _, uow = test_db
    person, _ = _setup_person_and_account(uow)
    debt_svc = DebtService(uow)

    debt = debt_svc.record_debt(
        debt_type=DebtType.BORROWED,
        person_id=person.id,
        counterparty_name="Friend",
        principal_amount=Money(100000),  # ₹1,000
    )

    with pytest.raises(InvalidDebtPaymentError, match="exceeds the outstanding balance"):
        debt_svc.record_payment(
            debt_id=debt.id,
            amount=Money(150000),  # ₹1,500 against ₹1,000 outstanding
            payment_date=date(2026, 10, 20),
        )

    # The overpayment must not have silently reduced the balance to zero.
    untouched = next(d for d in debt_svc.get_debts() if d.id == debt.id)
    assert untouched.remaining_formatted == "₹1,000.00"
    assert untouched.is_settled is False


def test_debt_payment_on_settled_debt_rejected(test_db):
    _, uow = test_db
    person, _ = _setup_person_and_account(uow)
    debt_svc = DebtService(uow)

    debt = debt_svc.record_debt(
        debt_type=DebtType.LENT,
        person_id=person.id,
        counterparty_name="Cousin",
        principal_amount=Money(50000),
    )
    settled = debt_svc.record_payment(
        debt_id=debt.id, amount=Money(50000), payment_date=date(2026, 10, 20)
    )
    assert settled.is_settled is True

    with pytest.raises(InvalidDebtPaymentError, match="already fully settled"):
        debt_svc.record_payment(debt_id=debt.id, amount=Money(100), payment_date=date(2026, 10, 21))


def test_debt_payment_non_positive_rejected(test_db):
    _, uow = test_db
    person, _ = _setup_person_and_account(uow)
    debt_svc = DebtService(uow)

    debt = debt_svc.record_debt(
        debt_type=DebtType.LENT,
        person_id=person.id,
        counterparty_name="Neighbour",
        principal_amount=Money(50000),
    )

    with pytest.raises(InvalidDebtPaymentError, match="strictly positive"):
        debt_svc.record_payment(debt_id=debt.id, amount=Money(0), payment_date=date(2026, 10, 20))


def test_debt_partial_repayments_reconcile_exactly(test_db):
    _, uow = test_db
    person, _ = _setup_person_and_account(uow)
    debt_svc = DebtService(uow)

    debt = debt_svc.record_debt(
        debt_type=DebtType.BORROWED,
        person_id=person.id,
        counterparty_name="Bank",
        principal_amount=Money(300000),  # ₹3,000
    )
    after_first = debt_svc.record_payment(
        debt_id=debt.id, amount=Money(120000), payment_date=date(2026, 10, 20)
    )
    assert after_first.remaining_formatted == "₹1,800.00"
    assert after_first.is_settled is False

    after_second = debt_svc.record_payment(
        debt_id=debt.id, amount=Money(180000), payment_date=date(2026, 10, 21)
    )
    assert after_second.remaining_formatted == "₹0.00"
    assert after_second.is_settled is True
