"""SavingsGoal and GoalContribution entities for tracking asset accumulation targets."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from paisaflow.domain.value_objects.money import Money


@dataclass
class GoalContribution:
    id: Optional[int]
    goal_id: int
    amount: Money
    date: date
    notes: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if self.amount.paise <= 0:
            raise ValueError("Contribution amount must be positive")


@dataclass
class SavingsGoal:
    id: Optional[int]
    name: str
    target_amount: Money
    current_amount: Money
    person_id: int
    target_date: Optional[date] = None
    linked_account_id: Optional[int] = None
    is_achieved: bool = False
    notes: Optional[str] = None
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Goal name cannot be empty")
        self.name = self.name.strip()
        if self.target_amount.paise <= 0:
            raise ValueError("Goal target amount must be strictly positive")

    @property
    def progress_percentage(self) -> Decimal:
        if self.target_amount.paise == 0:
            return Decimal("100.0")
        pct = (
            Decimal(self.current_amount.paise) / Decimal(self.target_amount.paise) * 100
        ).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        return min(pct, Decimal("100.0"))

    @property
    def remaining_amount(self) -> Money:
        diff = self.target_amount.paise - self.current_amount.paise
        return Money(max(0, diff))
