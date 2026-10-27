"""Ledger policy rules governing balance calculations and transaction balancing."""

from typing import Iterable

from paisaflow.domain.entities.account import Account
from paisaflow.domain.entities.transaction import (
    EntryDirection,
    Transaction,
    TransactionEntry,
    TransactionStatus,
    TransactionType,
)
from paisaflow.domain.exceptions import (
    InvalidTransactionError,
    InvalidTransferError,
    UnbalancedLedgerError,
)
from paisaflow.domain.value_objects.money import Money


class LedgerPolicy:
    """Core domain rules for calculating balances and verifying ledger entries."""

    @staticmethod
    def calculate_account_balance(account: Account, entries: Iterable[TransactionEntry]) -> Money:
        """Calculate the exact current balance of an account from opening balance and active entries.

        Asset Account:
            balance = opening_balance + inflows - outflows
        Liability Account (Credit Card):
            balance = opening_balance + outflows (charges) - inflows (payments)
            (Positive balance indicates amount owed to credit provider)
        """
        net_paise = account.opening_balance.paise

        for entry in entries:
            if entry.account_id != account.id:
                continue

            if account.is_liability:
                # Liability increases with outflow (spending), decreases with inflow (payment)
                if entry.direction == EntryDirection.OUTFLOW:
                    net_paise += entry.amount.paise
                elif entry.direction == EntryDirection.INFLOW:
                    net_paise -= entry.amount.paise
            else:
                # Asset increases with inflow, decreases with outflow
                if entry.direction == EntryDirection.INFLOW:
                    net_paise += entry.amount.paise
                elif entry.direction == EntryDirection.OUTFLOW:
                    net_paise -= entry.amount.paise

        return Money(net_paise, account.currency)

    @staticmethod
    def validate_transaction_entries(txn: Transaction) -> None:
        """Verify that transaction entries conform to domain invariants."""
        if txn.status == TransactionStatus.VOIDED:
            return

        match txn.transaction_type:
            case TransactionType.INCOME:
                if len(txn.entries) != 1:
                    raise InvalidTransactionError(
                        "Income transaction must have exactly one entry (inflow)."
                    )
                entry = txn.entries[0]
                if entry.direction != EntryDirection.INFLOW:
                    raise InvalidTransactionError("Income entry must be an inflow.")
                if entry.amount != txn.amount:
                    raise UnbalancedLedgerError(
                        f"Entry amount {entry.amount} does not match transaction amount {txn.amount}"
                    )

            case TransactionType.EXPENSE:
                if len(txn.entries) != 1:
                    raise InvalidTransactionError(
                        "Standard expense must have exactly one entry (outflow)."
                    )
                entry = txn.entries[0]
                if entry.direction != EntryDirection.OUTFLOW:
                    raise InvalidTransactionError("Expense entry must be an outflow.")
                if entry.amount != txn.amount:
                    raise UnbalancedLedgerError(
                        f"Entry amount {entry.amount} does not match transaction amount {txn.amount}"
                    )

            case TransactionType.TRANSFER:
                if len(txn.entries) != 2:
                    raise InvalidTransferError(
                        "Transfer must have exactly two entries (outflow and inflow)."
                    )
                outflow_entry = next(
                    (e for e in txn.entries if e.direction == EntryDirection.OUTFLOW), None
                )
                inflow_entry = next(
                    (e for e in txn.entries if e.direction == EntryDirection.INFLOW), None
                )
                if not outflow_entry or not inflow_entry:
                    raise InvalidTransferError(
                        "Transfer must contain both an outflow and an inflow leg."
                    )
                if outflow_entry.account_id == inflow_entry.account_id:
                    raise InvalidTransferError("Cannot transfer funds to the same account.")
                if outflow_entry.amount != txn.amount or inflow_entry.amount != txn.amount:
                    raise UnbalancedLedgerError(
                        "Both transfer legs must match the transaction total."
                    )

            case TransactionType.REFUND:
                if len(txn.entries) != 1:
                    raise InvalidTransactionError(
                        "Refund transaction must have exactly one entry (inflow)."
                    )
                entry = txn.entries[0]
                if entry.direction != EntryDirection.INFLOW:
                    raise InvalidTransactionError(
                        "Refund entry must be an inflow into the refunded account."
                    )
                if entry.amount != txn.amount:
                    raise UnbalancedLedgerError(
                        "Refund entry amount must match transaction amount."
                    )

            case TransactionType.ADJUSTMENT:
                if not txn.entries:
                    raise InvalidTransactionError(
                        "Adjustment transaction must have at least one entry."
                    )
