"""Debt and DebtPayment entities for tracking money lent or borrowed."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from paisaflow.domain.value_objects.money import Money


class DebtType(str, Enum):
    LENT = "lent"  # Asset: Someone owes user money (Receivable)
    BORROWED = "borrowed"  # Liability: User owes someone money (Payable)

    @property
    def display_name(self) -> str:
        return "Money Lent (Owed to You)" if self == DebtType.LENT else "Money Borrowed (You Owe)"

    @property
    def is_liability(self) -> bool:
        return self == DebtType.BORROWED


@dataclass
class DebtPayment:
    id: Optional[int]
    debt_id: int
    amount: Money
    payment_date: date
    account_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if self.amount.paise <= 0:
            raise ValueError("Payment amount must be positive")


@dataclass
class Debt:
    id: Optional[int]
    debt_type: DebtType
    person_id: int
    counterparty_name: str
    principal_amount: Money
    remaining_amount: Money
    due_date: Optional[date] = None
    is_settled: bool = False
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.counterparty_name or not self.counterparty_name.strip():
            raise ValueError("Counterparty name cannot be empty")
        self.counterparty_name = self.counterparty_name.strip()
        if isinstance(self.debt_type, str):
            self.debt_type = DebtType(self.debt_type)
        if self.principal_amount.paise <= 0:
            raise ValueError("Principal amount must be strictly positive")
