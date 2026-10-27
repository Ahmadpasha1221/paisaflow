"""Account entity representing an asset or liability storage of value."""

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from paisaflow.domain.value_objects.currency import DEFAULT_CURRENCY, Currency
from paisaflow.domain.value_objects.money import Money


class AccountType(str, Enum):
    CASH = "cash"
    BANK = "bank"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    OTHER = "other"

    @property
    def is_liability(self) -> bool:
        return self == AccountType.CREDIT_CARD

    @property
    def display_name(self) -> str:
        match self:
            case AccountType.CASH:
                return "Cash Wallet"
            case AccountType.BANK:
                return "Bank Account"
            case AccountType.SAVINGS:
                return "Savings Account"
            case AccountType.CREDIT_CARD:
                return "Credit Card"
            case AccountType.OTHER:
                return "Other Account"


@dataclass
class Account:
    id: Optional[int]
    name: str
    account_type: AccountType
    owner_person_id: int
    currency: Currency = DEFAULT_CURRENCY
    opening_balance: Money = Money(0)
    opening_date: date = date.today()
    is_archived: bool = False
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Account name cannot be empty")
        self.name = self.name.strip()
        if isinstance(self.account_type, str):
            self.account_type = AccountType(self.account_type)

    @property
    def is_liability(self) -> bool:
        return self.account_type.is_liability
