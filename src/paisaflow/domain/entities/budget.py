"""Budget entity representing category or person spending limits over a period."""

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from enum import Enum
from typing import Optional

from paisaflow.domain.value_objects.money import Money


class BudgetPeriod(str, Enum):
    MONTHLY = "monthly"
    WEEKLY = "weekly"


class BudgetStatusLevel(str, Enum):
    HEALTHY = "healthy"  # < 75%
    WARNING = "warning"  # 75% - 89%
    CRITICAL = "critical"  # 90% - 99%
    EXCEEDED = "exceeded"  # >= 100%


@dataclass
class Budget:
    id: Optional[int]
    name: str
    category_id: Optional[int]  # If None, global expense budget
    person_id: Optional[int]  # If None, household-wide
    period_type: BudgetPeriod
    period_start: date
    period_end: date
    limit_amount: Money
    alert_threshold_75: bool = True
    alert_threshold_90: bool = True
    alert_threshold_100: bool = True
    is_active: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Budget name cannot be empty")
        self.name = self.name.strip()
        if isinstance(self.period_type, str):
            self.period_type = BudgetPeriod(self.period_type)
        if self.limit_amount.paise <= 0:
            raise ValueError("Budget limit must be strictly positive")
        if self.period_start > self.period_end:
            raise ValueError("Budget period start must be before or equal to period end")

    def calculate_utilization(
        self, actual_spent: Money
    ) -> tuple[Decimal, Money, BudgetStatusLevel]:
        """Given actual spent Money, return (percentage, remaining_money, status_level)."""
        limit_paise = self.limit_amount.paise
        spent_paise = actual_spent.paise
        remaining_paise = limit_paise - spent_paise

        pct = (Decimal(spent_paise) / Decimal(limit_paise) * 100).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP
        )
        remaining = Money(remaining_paise)

        if pct >= 100:
            status = BudgetStatusLevel.EXCEEDED
        elif pct >= 90:
            status = BudgetStatusLevel.CRITICAL
        elif pct >= 75:
            status = BudgetStatusLevel.WARNING
        else:
            status = BudgetStatusLevel.HEALTHY

        return pct, remaining, status
