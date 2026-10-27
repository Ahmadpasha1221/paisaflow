"""Tests for deleting a transaction into History and the aggregates that follow it."""

from datetime import date

import pytest

from paisaflow.application.services import AccountService, PersonService, TransactionService
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.entities.transaction import PaymentMethod, TransactionStatus
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from paisaflow.presentation.viewmodels.overview_viewmodel import OverviewViewModel
from paisaflow.presentation.viewmodels.reports_viewmodel import ReportsViewModel
from paisaflow.presentation.viewmodels.transaction_viewmodel import TransactionViewModel


@pytest.fixture
def ledger(tmp_path):
    """A household with two members, one cash account and two expense records."""
    engine = create_db_engine(db_path=tmp_path / "history.db")
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))

    person_svc = PersonService(uow)
    account_svc = AccountService(uow)
    txn_svc = TransactionService(uow)

    aarav = person_svc.create_person(name="Aarav", color_code="#B8F28B")
    priya = person_svc.create_person(name="Priya", color_code="#82C9D4")
    account = account_svc.create_account(
        name="Household Cash",
        account_type=AccountType.CASH,
        owner_person_id=aarav.id,
        opening_balance=Money(1000000),
    )
    with uow:
        groceries = next(c for c in uow.categories.get_all() if c.name == "Groceries")

    wrong = txn_svc.record_expense(
        transaction_date=date.today(),
        description="Wrong entry",
        amount=Money(10000),
        account_id=account.id,
        person_id=aarav.id,
        category_id=groceries.id,
        payment_method=PaymentMethod.CASH,
    )
    keep = txn_svc.record_expense(
        transaction_date=date.today(),
        description="Real entry",
        amount=Money(20000),
        account_id=account.id,
        person_id=priya.id,
        category_id=groceries.id,
        payment_method=PaymentMethod.UPI,
    )

    return {
        "uow": uow,
        "account": account,
        "wrong": wrong,
        "keep": keep,
        "account_svc": account_svc,
    }


def test_delete_moves_the_transaction_out_of_the_ledger_and_into_history(ledger):
    txn_vm = TransactionViewModel(ledger["uow"])
    assert txn_vm.activeCount == 2
    assert txn_vm.historyCount == 0
    assert txn_vm.viewMode == "active"

    assert txn_vm.voidTransaction(ledger["wrong"].id) is True

    # The live ledger drops it immediately...
    assert txn_vm.activeCount == 1
    assert [t["description"] for t in txn_vm.transactions] == ["Real entry"]

    # ...and the History tab keeps the full record for audit.
    assert txn_vm.historyCount == 1
    txn_vm.setViewMode("history")
    assert [t["status"] for t in txn_vm.transactions] == ["voided"]
    assert txn_vm.transactions[0]["description"] == "Wrong entry"
    assert txn_vm.transactions[0]["voidedAt"] != ""

    txn_vm.setViewMode("active")
    assert [t["description"] for t in txn_vm.transactions] == ["Real entry"]


def test_deleting_a_transaction_refreshes_every_reporting_aggregate(ledger):
    uow = ledger["uow"]
    txn_vm = TransactionViewModel(uow)
    overview_vm = OverviewViewModel(uow)
    reports_vm = ReportsViewModel(uow)

    assert overview_vm.expensesMonth == "₹300.00"
    assert len(reports_vm.categoryShares) == 1
    assert reports_vm.categoryShares[0]["amount"] == "₹300.00"
    assert len(reports_vm.personSpending) == 2

    txn_vm.voidTransaction(ledger["wrong"].id)
    overview_vm.refresh()
    reports_vm.refresh()

    # Dashboard, account balance and reports all recompute without a restart.
    assert overview_vm.expensesMonth == "₹200.00"
    assert overview_vm.totalAssets == "₹9,800.00"
    assert ledger["account_svc"].get_account_by_id(ledger["account"].id).balance_paise == 980000

    current_month = reports_vm.monthlyTrends[-1]
    assert current_month["expenses"] == "₹200.00"
    assert reports_vm.categoryShares[0]["amount"] == "₹200.00"
    assert reports_vm.totalExpenses == "₹200.00"
    assert [(p["label"], p["amount"]) for p in reports_vm.personSpending] == [("Priya", "₹200.00")]

    # The deleted record must not resurface on the dashboard.
    assert [t["description"] for t in overview_vm.recentTransactions] == ["Real entry"]


def test_voided_transactions_are_excluded_from_queries_by_default(ledger):
    uow = ledger["uow"]
    txn_svc = TransactionService(uow)
    txn_svc.void_transaction(ledger["wrong"].id)

    active, active_total = txn_svc.query_transactions(include_voided=False)
    assert active_total == 1
    assert [t.description for t in active] == ["Real entry"]

    history, history_total = txn_svc.query_transactions(status=TransactionStatus.VOIDED)
    assert history_total == 1
    assert history[0].description == "Wrong entry"
