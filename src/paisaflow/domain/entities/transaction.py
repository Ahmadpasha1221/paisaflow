"""Transaction and TransactionEntry entities representing financial events and ledger legs."""

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from enum import Enum
from typing import List, Optional

from paisaflow.domain.value_objects.money import Money


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    REFUND = "refund"

    @property
    def display_name(self) -> str:
        match self:
            case TransactionType.INCOME:
                return "Income"
            case TransactionType.EXPENSE:
                return "Expense"
            case TransactionType.TRANSFER:
                return "Transfer"
            case TransactionType.ADJUSTMENT:
                return "Adjustment"
            case TransactionType.REFUND:
                return "Refund"


class PaymentMethod(str, Enum):
    CASH = "cash"
    UPI = "upi"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"

    @property
    def display_name(self) -> str:
        match self:
            case PaymentMethod.CASH:
                return "Cash"
            case PaymentMethod.UPI:
                return "UPI"
            case PaymentMethod.DEBIT_CARD:
                return "Debit Card"
            case PaymentMethod.CREDIT_CARD:
                return "Credit Card"
            case PaymentMethod.BANK_TRANSFER:
                return "Bank Transfer"
            case PaymentMethod.OTHER:
                return "Other"


class TransactionStatus(str, Enum):
    COMPLETED = "completed"
    VOIDED = "voided"
    RECONCILED = "reconciled"


class EntryDirection(str, Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"


@dataclass
class TransactionEntry:
    """Individual debit/credit balance movement affecting a single account."""

    id: Optional[int]
    transaction_id: Optional[int]
    account_id: int
    direction: EntryDirection
    amount: Money
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if isinstance(self.direction, str):
            self.direction = EntryDirection(self.direction)
        if self.amount.paise <= 0:
            raise ValueError(f"Entry amount must be positive, got {self.amount.paise}")


def generate_reference_no(txn_date: date) -> str:
    """Generate human-readable unique reference like TXN-20261027-A1B2."""
    date_str = txn_date.strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"TXN-{date_str}-{short_uuid}"


@dataclass
class Transaction:
    """Economic financial event with one or more ledger entries."""

    id: Optional[int]
    reference_no: str
    transaction_date: date
    transaction_time: time
    transaction_type: TransactionType
    description: str
    amount: Money
    person_id: int
    category_id: Optional[int] = None
    payment_method: PaymentMethod = PaymentMethod.UPI
    status: TransactionStatus = TransactionStatus.COMPLETED
    related_transaction_id: Optional[int] = None
    notes: Optional[str] = None
    entries: List[TransactionEntry] = field(default_factory=list)
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.description or not self.description.strip():
            raise ValueError("Transaction description cannot be empty")
        self.description = self.description.strip()
        if isinstance(self.transaction_type, str):
            self.transaction_type = TransactionType(self.transaction_type)
        if isinstance(self.payment_method, str):
            self.payment_method = PaymentMethod(self.payment_method)
        if isinstance(self.status, str):
            self.status = TransactionStatus(self.status)
        if self.amount.paise <= 0:
            raise ValueError("Transaction amount must be strictly positive")
        if not self.reference_no:
            self.reference_no = generate_reference_no(self.transaction_date)
