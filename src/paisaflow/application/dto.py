"""Data Transfer Objects (DTOs) for application layer boundaries and presentation models."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class PersonDto:
    id: int
    name: str
    color_code: str
    avatar_path: Optional[str]
    is_active: bool


@dataclass(frozen=True)
class AccountDto:
    id: int
    name: str
    account_type: str
    account_type_display: str
    owner_person_id: int
    owner_name: str
    opening_balance_formatted: str
    balance_formatted: str
    balance_paise: int
    is_liability: bool
    is_archived: bool
    notes: Optional[str]


@dataclass(frozen=True)
class CategoryDto:
    id: int
    name: str
    category_type: str
    category_type_display: str
    icon_name: str
    color_code: str
    is_archived: bool


@dataclass(frozen=True)
class TransactionDto:
    id: int
    reference_no: str
    transaction_date: str
    transaction_time: str
    transaction_type: str
    transaction_type_display: str
    description: str
    amount_formatted: str
    amount_paise: int
    person_id: int
    person_name: str
    category_id: Optional[int]
    category_name: str
    payment_method: str
    payment_method_display: str
    status: str
    notes: Optional[str]
    affected_accounts: str
    created_at: str = ""
    updated_at: str = ""
    voided_at: str = ""


@dataclass(frozen=True)
class BudgetDto:
    id: int
    name: str
    category_id: Optional[int]
    category_name: str
    person_id: Optional[int]
    person_name: str
    period_type: str
    period_start: str
    period_end: str
    limit_formatted: str
    spent_formatted: str
    remaining_formatted: str
    utilization_percentage: float
    status_level: str  # 'healthy', 'warning', 'critical', 'exceeded'
    is_active: bool


@dataclass(frozen=True)
class GoalDto:
    id: int
    name: str
    target_formatted: str
    current_formatted: str
    remaining_formatted: str
    progress_percentage: float
    person_id: int
    person_name: str
    target_date: Optional[str]
    is_achieved: bool
    notes: Optional[str]


@dataclass(frozen=True)
class DebtDto:
    id: int
    debt_type: str
    debt_type_display: str
    person_id: int
    person_name: str
    counterparty_name: str
    principal_formatted: str
    remaining_formatted: str
    due_date: Optional[str]
    is_settled: bool
    is_liability: bool
    notes: Optional[str]


@dataclass(frozen=True)
class CategorySpendingDto:
    category_name: str
    color_code: str
    amount_paise: int
    amount_formatted: str
    percentage: float


@dataclass(frozen=True)
class OverviewSummaryDto:
    total_assets_formatted: str
    total_assets_paise: int
    total_liabilities_formatted: str
    total_liabilities_paise: int
    net_worth_formatted: str
    net_worth_paise: int
    income_month_formatted: str
    income_month_paise: int
    expenses_month_formatted: str
    expenses_month_paise: int
    net_cash_flow_formatted: str
    net_cash_flow_paise: int
    budget_utilization_percentage: float
    recent_transactions: List[TransactionDto]
    category_spending: List[CategorySpendingDto]
