"""Money value object representing exact monetary amounts in minor units (Paise for INR).

No binary floats are ever permitted as authoritative monetary representation.
"""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Self

from paisaflow.domain.exceptions import InvalidMonetaryValueError
from paisaflow.domain.value_objects.currency import DEFAULT_CURRENCY, Currency


class Money:
    """Immutable representation of monetary value in integer minor units (Paise)."""

    __slots__ = ("_paise", "_currency")

    def __init__(self, paise: int, currency: Currency = DEFAULT_CURRENCY) -> None:
        if isinstance(paise, float):
            raise InvalidMonetaryValueError(
                f"Binary float {paise} cannot be used to initialize Money. Use int or Money.from_decimal()."
            )
        if not isinstance(paise, int):
            raise InvalidMonetaryValueError(f"Paise must be an integer, got {type(paise).__name__}")

        object.__setattr__(self, "_paise", paise)
        object.__setattr__(self, "_currency", currency)

    @property
    def paise(self) -> int:
        """Raw integer amount in minor units (paise)."""
        return self._paise

    @property
    def currency(self) -> Currency:
        """Currency of the money."""
        return self._currency

    @classmethod
    def zero(cls, currency: Currency = DEFAULT_CURRENCY) -> Self:
        return cls(0, currency)

    @classmethod
    def from_rupees(cls, rupees: int, currency: Currency = DEFAULT_CURRENCY) -> Self:
        """Create Money from whole rupee integer."""
        if not isinstance(rupees, int):
            raise InvalidMonetaryValueError(
                "Rupees must be an integer. For fractional amounts, use from_decimal/from_str."
            )
        return cls(rupees * currency.minor_unit_factor, currency)

    @classmethod
    def from_decimal(cls, amount: Decimal, currency: Currency = DEFAULT_CURRENCY) -> Self:
        """Convert a Decimal value into exact minor units using ROUND_HALF_UP."""
        if not isinstance(amount, Decimal):
            raise InvalidMonetaryValueError(f"Expected Decimal, got {type(amount).__name__}")
        factor = Decimal(currency.minor_unit_factor)
        paise_decimal = (amount * factor).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return cls(int(paise_decimal), currency)

    @classmethod
    def from_str(cls, text: str, currency: Currency = DEFAULT_CURRENCY) -> Self:
        """Parse user input string like '1234.50', '₹ 1,200', '-50.25' into Money."""
        if not text:
            return cls.zero(currency)

        # Remove currency symbol, commas, and whitespace
        clean = text.replace(currency.symbol, "").replace(",", "").strip()
        if not clean:
            return cls.zero(currency)

        try:
            d = Decimal(clean)
            return cls.from_decimal(d, currency)
        except InvalidOperation as e:
            raise InvalidMonetaryValueError(f"Invalid monetary string '{text}': {e}") from e

    def to_decimal(self) -> Decimal:
        """Return Decimal representation in major units (e.g. rupees)."""
        return Decimal(self._paise) / Decimal(self._currency.minor_unit_factor)

    def format(self, include_symbol: bool = True) -> str:
        """Format to Indian Numbering System string (e.g. ₹1,23,456.78)."""
        abs_paise = abs(self._paise)
        major = abs_paise // self._currency.minor_unit_factor
        minor = abs_paise % self._currency.minor_unit_factor

        # Indian Numbering Grouping:
        # Last 3 digits, then groups of 2 digits
        s = str(major)
        if len(s) <= 3:
            grouped = s
        else:
            last3 = s[-3:]
            remaining = s[:-3]
            pairs = []
            while len(remaining) > 2:
                pairs.append(remaining[-2:])
                remaining = remaining[:-2]
            if remaining:
                pairs.append(remaining)
            pairs.reverse()
            grouped = ",".join(pairs) + "," + last3

        formatted = f"{grouped}.{minor:02d}"
        if self._paise < 0:
            formatted = f"-{formatted}"

        if include_symbol:
            if self._paise < 0:
                return f"-{self._currency.symbol}{formatted[1:]}"
            return f"{self._currency.symbol}{formatted}"
        return formatted

    # Arithmetic
    def __add__(self, other: Self) -> Self:
        if not isinstance(other, Money) or self._currency != other._currency:
            raise InvalidMonetaryValueError("Cannot add different currencies or non-Money types.")
        return Money(self._paise + other._paise, self._currency)

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, Money) or self._currency != other._currency:
            raise InvalidMonetaryValueError(
                "Cannot subtract different currencies or non-Money types."
            )
        return Money(self._paise - other._paise, self._currency)

    def __mul__(self, scalar: int | Decimal) -> Self:
        if isinstance(scalar, int):
            return Money(self._paise * scalar, self._currency)
        if isinstance(scalar, Decimal):
            new_paise = (Decimal(self._paise) * scalar).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            return Money(int(new_paise), self._currency)
        raise InvalidMonetaryValueError(
            f"Can only multiply Money by int or Decimal, got {type(scalar).__name__}"
        )

    def __truediv__(self, divisor: int | Decimal) -> Self:
        if isinstance(divisor, (int, Decimal)):
            if divisor == 0:
                raise ZeroDivisionError("Cannot divide Money by zero.")
            dec_div = Decimal(divisor) if isinstance(divisor, int) else divisor
            new_paise = (Decimal(self._paise) / dec_div).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
            return Money(int(new_paise), self._currency)
        raise InvalidMonetaryValueError("Can only divide Money by int or Decimal.")

    def __neg__(self) -> Self:
        return Money(-self._paise, self._currency)

    def __abs__(self) -> Self:
        return Money(abs(self._paise), self._currency)

    # Comparisons
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return False
        return self._paise == other._paise and self._currency == other._currency

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, Money) or self._currency != other._currency:
            raise InvalidMonetaryValueError(
                "Cannot compare different currencies or non-Money types."
            )
        return self._paise < other._paise

    def __le__(self, other: Self) -> bool:
        return self < other or self == other

    def __gt__(self, other: Self) -> bool:
        return not self <= other

    def __ge__(self, other: Self) -> bool:
        return not self < other

    def __bool__(self) -> bool:
        return self._paise != 0

    def __repr__(self) -> str:
        return f"Money({self._paise} paise, {self._currency.code})"

    def __str__(self) -> str:
        return self.format()

    def __hash__(self) -> int:
        return hash((self._paise, self._currency.code))
