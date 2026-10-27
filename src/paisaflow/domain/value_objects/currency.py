"""Currency value object."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Currency:
    code: str = "INR"
    symbol: str = "₹"
    name: str = "Indian Rupee"
    minor_unit_factor: int = 100  # 1 INR = 100 Paise
    decimals: int = 2


DEFAULT_CURRENCY = Currency()
