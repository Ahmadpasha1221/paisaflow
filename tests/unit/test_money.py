"""Unit tests for Money value object."""

from decimal import Decimal

import pytest

from paisaflow.domain.exceptions import InvalidMonetaryValueError
from paisaflow.domain.value_objects.money import Money


def test_money_paise_initialization():
    m = Money(15025)
    assert m.paise == 15025
    assert m.currency.code == "INR"


def test_money_rejects_binary_floats():
    with pytest.raises(InvalidMonetaryValueError, match="Binary float"):
        Money(10.5)  # type: ignore


def test_money_from_rupees():
    m = Money.from_rupees(500)
    assert m.paise == 50000


def test_money_from_decimal():
    d = Decimal("123.456")  # rounds to 123.46 -> 12346 paise
    m = Money.from_decimal(d)
    assert m.paise == 12346

    d2 = Decimal("123.454")  # rounds to 123.45 -> 12345 paise
    m2 = Money.from_decimal(d2)
    assert m2.paise == 12345


def test_money_from_str():
    assert Money.from_str("1234.50").paise == 123450
    assert Money.from_str("₹ 1,200.00").paise == 120000
    assert Money.from_str("-50.25").paise == -5025
    assert Money.from_str("").paise == 0
    assert Money.from_str("0").paise == 0

    with pytest.raises(InvalidMonetaryValueError):
        Money.from_str("not-a-number")


def test_money_indian_numbering_formatting():
    # Small numbers
    assert Money(0).format() == "₹0.00"
    assert Money(50).format() == "₹0.50"
    assert Money(50000).format() == "₹500.00"
    assert Money(123450).format() == "₹1,234.50"

    # Lakhs and Crores
    # 1 Lakh = 1,00,000.00
    assert Money(10000000).format() == "₹1,00,000.00"
    # 12 Lakh 34 Thousand 567 Rupee 89 Paise
    assert Money(123456789).format() == "₹12,34,567.89"
    # 1 Crore = 1,00,00,000.00
    assert Money(1000000000).format() == "₹1,00,00,000.00"

    # Negative numbers
    assert Money(-50000).format() == "-₹500.00"
    assert Money(-123456789).format() == "-₹12,34,567.89"

    # Without symbol
    assert Money(123450).format(include_symbol=False) == "1,234.50"


def test_money_arithmetic():
    m1 = Money(10000)  # ₹100
    m2 = Money(4550)  # ₹45.50

    # Addition
    assert (m1 + m2).paise == 14550

    # Subtraction
    assert (m1 - m2).paise == 5450

    # Scalar multiplication
    assert (m1 * 3).paise == 30000
    assert (m1 * Decimal("1.18")).paise == 11800  # 18% GST

    # Division
    assert (m1 / 2).paise == 5000
    assert (m1 / Decimal("3")).paise == 3333

    # Negation & Absolute
    assert (-m1).paise == -10000
    assert abs(-m1).paise == 10000


def test_money_comparisons():
    m1 = Money(10000)
    m2 = Money(20000)
    m3 = Money(10000)

    assert m1 < m2
    assert m1 <= m2
    assert m2 > m1
    assert m2 >= m1
    assert m1 == m3
    assert m1 != m2
