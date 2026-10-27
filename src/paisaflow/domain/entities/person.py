"""Person entity representing an individual or household member."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class Person:
    id: Optional[int]
    name: str
    color_code: str = "#B8F28B"
    avatar_path: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Person name cannot be empty")
        self.name = self.name.strip()
