"""Unit of Work pattern managing transaction boundary and repository access."""

from typing import Optional

from sqlalchemy.orm import Session, sessionmaker

from paisaflow.infrastructure.database.repositories import (
    AccountRepository,
    BudgetRepository,
    CategoryRepository,
    DebtRepository,
    GoalRepository,
    PersonRepository,
    SettingsRepository,
    TransactionRepository,
)


class SqlAlchemyUnitOfWork:
    """Manages transactional scope and provides atomic commit/rollback across all repositories."""

    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory
        self.session: Optional[Session] = None

        self.people: PersonRepository
        self.accounts: AccountRepository
        self.categories: CategoryRepository
        self.transactions: TransactionRepository
        self.budgets: BudgetRepository
        self.goals: GoalRepository
        self.debts: DebtRepository
        self.settings: SettingsRepository

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        self.people = PersonRepository(self.session)
        self.accounts = AccountRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.transactions = TransactionRepository(self.session)
        self.budgets = BudgetRepository(self.session)
        self.goals = GoalRepository(self.session)
        self.debts = DebtRepository(self.session)
        self.settings = SettingsRepository(self.session)
        return self

    def commit(self) -> None:
        if self.session:
            self.session.commit()

    def rollback(self) -> None:
        if self.session:
            self.session.rollback()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        if self.session:
            if exc_type is not None:
                self.rollback()
            self.session.close()
            self.session = None
