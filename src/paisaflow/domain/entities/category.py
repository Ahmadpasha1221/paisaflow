"""Category entity for classification of income and expenses."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

    @property
    def display_name(self) -> str:
        return "Income" if self == CategoryType.INCOME else "Expense"


@dataclass
class Category:
    id: Optional[int]
    name: str
    category_type: CategoryType
    parent_id: Optional[int] = None
    icon_name: str = "tag"
    color_code: str = "#82C9D4"
    is_archived: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Category name cannot be empty")
        self.name = self.name.strip()
        if isinstance(self.category_type, str):
            self.category_type = CategoryType(self.category_type)


# Standard defaults for initial setup
DEFAULT_INCOME_CATEGORIES = [
    ("Salary", "briefcase", "#B8F28B"),
    ("Freelance Income", "laptop", "#82C9D4"),
    ("Business Income", "trending-up", "#A5D6A7"),
    ("Other Income", "plus-circle", "#C9F8A6"),
]

DEFAULT_EXPENSE_CATEGORIES = [
    ("Groceries", "shopping-cart", "#80CBC4"),
    ("Food and Dining", "utensils", "#FFAB91"),
    ("Housing and Rent", "home", "#90CAF9"),
    ("Utilities", "zap", "#FFE082"),
    ("Transport and Fuel", "car", "#B39DDB"),
    ("Shopping", "shopping-bag", "#F48FB1"),
    ("Healthcare", "activity", "#EF9A9A"),
    ("Education", "book-open", "#81D4FA"),
    ("Entertainment", "film", "#CE93D8"),
    ("Subscriptions", "repeat", "#80DEEA"),
    ("Family", "users", "#A5D6A7"),
    ("EMI and Interest", "percent", "#FFCC80"),
    ("Other Expenses", "more-horizontal", "#B0BEC5"),
]
