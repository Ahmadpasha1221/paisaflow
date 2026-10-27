"""Regression test: entity timestamps must be generated per instance, not at import time.

A plain ``datetime.now(...)`` dataclass default is evaluated once when the module is
imported, so every object created during a run would share a single bogus timestamp.
Timestamps must come from a ``default_factory`` instead.
"""

import dataclasses

import pytest

from paisaflow.domain.entities.account import Account
from paisaflow.domain.entities.budget import Budget
from paisaflow.domain.entities.category import Category
from paisaflow.domain.entities.debt import Debt, DebtPayment
from paisaflow.domain.entities.goal import GoalContribution, SavingsGoal
from paisaflow.domain.entities.person import Person
from paisaflow.domain.entities.transaction import Transaction, TransactionEntry

TIMESTAMPED_ENTITIES = [
    Person,
    Account,
    Category,
    Transaction,
    TransactionEntry,
    Budget,
    SavingsGoal,
    GoalContribution,
    Debt,
    DebtPayment,
]


@pytest.mark.parametrize("entity", TIMESTAMPED_ENTITIES)
def test_created_at_uses_default_factory(entity):
    fields = {f.name: f for f in dataclasses.fields(entity)}
    assert "created_at" in fields, f"{entity.__name__} has no created_at field"

    created_at = fields["created_at"]
    assert created_at.default is dataclasses.MISSING, (
        f"{entity.__name__}.created_at is a static default evaluated at import time"
    )
    assert created_at.default_factory is not dataclasses.MISSING, (
        f"{entity.__name__}.created_at must use default_factory"
    )


@pytest.mark.parametrize("entity", TIMESTAMPED_ENTITIES)
def test_updated_at_uses_default_factory(entity):
    fields = {f.name: f for f in dataclasses.fields(entity)}
    if "updated_at" not in fields:
        pytest.skip(f"{entity.__name__} has no updated_at field")

    updated_at = fields["updated_at"]
    assert updated_at.default is dataclasses.MISSING, (
        f"{entity.__name__}.updated_at is a static default evaluated at import time"
    )
    assert updated_at.default_factory is not dataclasses.MISSING, (
        f"{entity.__name__}.updated_at must use default_factory"
    )
