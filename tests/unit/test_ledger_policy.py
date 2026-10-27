"""Unit tests for LedgerPolicy rules."""

from datetime import date, time

import pytest

from paisaflow.domain.entities.account import Account, AccountType
from paisaflow.domain.entities.transaction import (
    EntryDirection,
    Transaction,
    TransactionEntry,
    TransactionType,
)
from paisaflow.domain.exceptions import (
    InvalidTransactionError,
    InvalidTransferError,
)
from paisaflow.domain.policies.ledger_policy import LedgerPolicy
from paisaflow.domain.value_objects.money import Money


def test_calculate_asset_account_balance():
    # Asset account with opening balance ₹1,000
    account = Account(
        id=1,
        name="Main Bank",
        account_type=AccountType.BANK,
        owner_person_id=1,
        opening_balance=Money(100000),
    )

    entries = [
        # Inflow (Salary): +₹500
        TransactionEntry(
            id=1,
            transaction_id=10,
            account_id=1,
            direction=EntryDirection.INFLOW,
            amount=Money(50000),
        ),
        # Outflow (Groceries): -₹200
        TransactionEntry(
            id=2,
            transaction_id=11,
            account_id=1,
            direction=EntryDirection.OUTFLOW,
            amount=Money(20000),
        ),
        # Outflow (Fuel): -₹150
        TransactionEntry(
            id=3,
            transaction_id=12,
            account_id=1,
            direction=EntryDirection.OUTFLOW,
            amount=Money(15000),
        ),
        # Entry for unrelated account (should be ignored)
        TransactionEntry(
            id=4,
            transaction_id=13,
            account_id=2,
            direction=EntryDirection.INFLOW,
            amount=Money(99900),
        ),
    ]

    balance = LedgerPolicy.calculate_account_balance(account, entries)
    # 1000 + 500 - 200 - 150 = 1150 => 115000 paise
    assert balance.paise == 115000


def test_calculate_liability_credit_card_balance():
    # Credit Card account with 0 opening balance
    card = Account(
        id=2,
        name="HDFC Card",
        account_type=AccountType.CREDIT_CARD,
        owner_person_id=1,
        opening_balance=Money(0),
    )

    entries = [
        # Outflow (Purchase charge): liability increases by ₹300
        TransactionEntry(
            id=1,
            transaction_id=20,
            account_id=2,
            direction=EntryDirection.OUTFLOW,
            amount=Money(30000),
        ),
        # Outflow (Purchase charge): liability increases by ₹150
        TransactionEntry(
            id=2,
            transaction_id=21,
            account_id=2,
            direction=EntryDirection.OUTFLOW,
            amount=Money(15000),
        ),
        # Inflow (Payment from bank): liability decreases by ₹200
        TransactionEntry(
            id=3,
            transaction_id=22,
            account_id=2,
            direction=EntryDirection.INFLOW,
            amount=Money(20000),
        ),
    ]

    balance = LedgerPolicy.calculate_account_balance(card, entries)
    # 0 + 300 + 150 - 200 = 250 => 25000 paise owed
    assert balance.paise == 25000


def test_validate_income_transaction():
    txn = Transaction(
        id=1,
        reference_no="TXN-INCOME-1",
        transaction_date=date.today(),
        transaction_time=time(10, 0),
        transaction_type=TransactionType.INCOME,
        description="Salary",
        amount=Money(5000000),
        person_id=1,
        category_id=1,
        entries=[
            TransactionEntry(
                id=1,
                transaction_id=1,
                account_id=1,
                direction=EntryDirection.INFLOW,
                amount=Money(5000000),
            )
        ],
    )
    # Should pass without error
    LedgerPolicy.validate_transaction_entries(txn)


def test_validate_income_rejects_outflow_or_unbalanced():
    with pytest.raises(InvalidTransactionError, match="must be an inflow"):
        txn = Transaction(
            id=1,
            reference_no="TXN-INCOME-BAD",
            transaction_date=date.today(),
            transaction_time=time(10, 0),
            transaction_type=TransactionType.INCOME,
            description="Bad Salary",
            amount=Money(5000000),
            person_id=1,
            entries=[
                TransactionEntry(
                    id=1,
                    transaction_id=1,
                    account_id=1,
                    direction=EntryDirection.OUTFLOW,
                    amount=Money(5000000),
                )
            ],
        )
        LedgerPolicy.validate_transaction_entries(txn)


def test_validate_transfer_transaction():
    txn = Transaction(
        id=2,
        reference_no="TXN-TRANSFER-1",
        transaction_date=date.today(),
        transaction_time=time(12, 0),
        transaction_type=TransactionType.TRANSFER,
        description="Bank to Cash ATM",
        amount=Money(500000),  # ₹5,000
        person_id=1,
        entries=[
            TransactionEntry(
                id=1,
                transaction_id=2,
                account_id=1,
                direction=EntryDirection.OUTFLOW,
                amount=Money(500000),
            ),
            TransactionEntry(
                id=2,
                transaction_id=2,
                account_id=2,
                direction=EntryDirection.INFLOW,
                amount=Money(500000),
            ),
        ],
    )
    LedgerPolicy.validate_transaction_entries(txn)


def test_validate_transfer_rejects_same_account():
    with pytest.raises(InvalidTransferError, match="same account"):
        txn = Transaction(
            id=3,
            reference_no="TXN-TRANSFER-SAME",
            transaction_date=date.today(),
            transaction_time=time(12, 0),
            transaction_type=TransactionType.TRANSFER,
            description="Self transfer",
            amount=Money(10000),
            person_id=1,
            entries=[
                TransactionEntry(
                    id=1,
                    transaction_id=3,
                    account_id=1,
                    direction=EntryDirection.OUTFLOW,
                    amount=Money(10000),
                ),
                TransactionEntry(
                    id=2,
                    transaction_id=3,
                    account_id=1,
                    direction=EntryDirection.INFLOW,
                    amount=Money(10000),
                ),
            ],
        )
        LedgerPolicy.validate_transaction_entries(txn)
