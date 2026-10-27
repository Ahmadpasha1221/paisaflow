"""Unit tests explicitly testing Financial Domain Invariants specified in Section 12."""

from datetime import date
from decimal import Decimal

from paisaflow.domain.entities.account import Account, AccountType
from paisaflow.domain.entities.budget import Budget, BudgetPeriod, BudgetStatusLevel
from paisaflow.domain.entities.debt import Debt, DebtType
from paisaflow.domain.entities.goal import SavingsGoal
from paisaflow.domain.entities.transaction import EntryDirection, TransactionEntry
from paisaflow.domain.policies.ledger_policy import LedgerPolicy
from paisaflow.domain.value_objects.money import Money


def test_invariant_1_internal_transfer_does_not_change_total_assets():
    """INV-1: An internal transfer does not change total assets."""
    bank = Account(
        id=1,
        name="Bank",
        account_type=AccountType.BANK,
        owner_person_id=1,
        opening_balance=Money(100000),
    )
    cash = Account(
        id=2,
        name="Cash",
        account_type=AccountType.CASH,
        owner_person_id=1,
        opening_balance=Money(20000),
    )

    initial_assets = bank.opening_balance + cash.opening_balance
    assert initial_assets.paise == 120000

    # Transfer ₹300 from bank to cash
    transfer_amount = Money(30000)
    bank_entry = TransactionEntry(
        id=1,
        transaction_id=9,
        account_id=1,
        direction=EntryDirection.OUTFLOW,
        amount=transfer_amount,
    )
    cash_entry = TransactionEntry(
        id=2,
        transaction_id=9,
        account_id=2,
        direction=EntryDirection.INFLOW,
        amount=transfer_amount,
    )

    new_bank_bal = LedgerPolicy.calculate_account_balance(bank, [bank_entry])
    new_cash_bal = LedgerPolicy.calculate_account_balance(cash, [cash_entry])

    final_assets = new_bank_bal + new_cash_bal
    assert final_assets == initial_assets
    assert new_bank_bal.paise == 70000
    assert new_cash_bal.paise == 50000


def test_invariant_2_budget_utilization_thresholds():
    """INV-2: Budget utilization thresholds trigger at 75%, 90%, and 100%."""
    budget = Budget(
        id=1,
        name="Groceries Budget",
        category_id=1,
        person_id=1,
        period_type=BudgetPeriod.MONTHLY,
        period_start=date(2026, 10, 1),
        period_end=date(2026, 10, 31),
        limit_amount=Money(1000000),  # ₹10,000
    )

    # 50% spent -> Healthy
    pct, remaining, status = budget.calculate_utilization(Money(500000))
    assert pct == Decimal("50.0")
    assert remaining == Money(500000)
    assert status == BudgetStatusLevel.HEALTHY

    # 75% spent -> Warning
    pct, remaining, status = budget.calculate_utilization(Money(750000))
    assert pct == Decimal("75.0")
    assert status == BudgetStatusLevel.WARNING

    # 92% spent -> Critical
    pct, remaining, status = budget.calculate_utilization(Money(920000))
    assert pct == Decimal("92.0")
    assert status == BudgetStatusLevel.CRITICAL

    # 105% spent -> Exceeded
    pct, remaining, status = budget.calculate_utilization(Money(1050000))
    assert pct == Decimal("105.0")
    assert remaining == Money(-50000)
    assert status == BudgetStatusLevel.EXCEEDED


def test_invariant_3_debt_types_and_classification():
    """INV-3: Money lent is receivable (asset); money borrowed is payable (liability). Neither is income/expense."""
    lent = Debt(
        id=1,
        debt_type=DebtType.LENT,
        person_id=1,
        counterparty_name="Ramesh",
        principal_amount=Money(500000),
        remaining_amount=Money(500000),
    )
    assert not lent.debt_type.is_liability

    borrowed = Debt(
        id=2,
        debt_type=DebtType.BORROWED,
        person_id=1,
        counterparty_name="Bank Personal Loan",
        principal_amount=Money(10000000),
        remaining_amount=Money(10000000),
    )
    assert borrowed.debt_type.is_liability


def test_invariant_4_savings_goal_progress():
    """INV-4: Savings goal tracks progress percentage cleanly."""
    goal = SavingsGoal(
        id=1,
        name="Emergency Fund",
        target_amount=Money(10000000),  # ₹1,00,000
        current_amount=Money(2500000),  # ₹25,000
        person_id=1,
    )
    assert goal.progress_percentage == Decimal("25.0")
    assert goal.remaining_amount == Money(7500000)
