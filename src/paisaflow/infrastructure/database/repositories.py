"""Database repositories implementing data access and domain mapping."""

from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from paisaflow.domain.entities.account import Account, AccountType
from paisaflow.domain.entities.budget import Budget, BudgetPeriod
from paisaflow.domain.entities.category import Category, CategoryType
from paisaflow.domain.entities.debt import Debt, DebtPayment, DebtType
from paisaflow.domain.entities.goal import GoalContribution, SavingsGoal
from paisaflow.domain.entities.person import Person
from paisaflow.domain.entities.transaction import (
    EntryDirection,
    PaymentMethod,
    Transaction,
    TransactionEntry,
    TransactionStatus,
    TransactionType,
)
from paisaflow.domain.value_objects.currency import DEFAULT_CURRENCY
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.models import (
    AccountModel,
    AppSettingModel,
    BudgetModel,
    CategoryModel,
    DebtModel,
    DebtPaymentModel,
    GoalContributionModel,
    PersonModel,
    SavingsGoalModel,
    TransactionEntryModel,
    TransactionModel,
)


class PersonRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, person_id: int) -> Optional[Person]:
        model = self._session.get(PersonModel, person_id)
        return self._to_entity(model) if model else None

    def get_all(self, include_inactive: bool = False) -> List[Person]:
        stmt = select(PersonModel)
        if not include_inactive:
            stmt = stmt.where(PersonModel.is_active.is_(True))
        stmt = stmt.order_by(PersonModel.name)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def add(self, person: Person) -> Person:
        model = PersonModel(
            name=person.name,
            color_code=person.color_code,
            avatar_path=person.avatar_path,
            is_active=person.is_active,
        )
        self._session.add(model)
        self._session.flush()
        person.id = model.id
        return person

    def update(self, person: Person) -> None:
        model = self._session.get(PersonModel, person.id)
        if model:
            model.name = person.name
            model.color_code = person.color_code
            model.avatar_path = person.avatar_path
            model.is_active = person.is_active

    @staticmethod
    def _to_entity(m: PersonModel) -> Person:
        return Person(
            id=m.id,
            name=m.name,
            color_code=m.color_code,
            avatar_path=m.avatar_path,
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class AccountRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, account_id: int) -> Optional[Account]:
        model = self._session.get(AccountModel, account_id)
        return self._to_entity(model) if model else None

    def get_all(
        self, include_archived: bool = False, person_id: Optional[int] = None
    ) -> List[Account]:
        stmt = select(AccountModel)
        if not include_archived:
            stmt = stmt.where(AccountModel.is_archived.is_(False))
        if person_id is not None:
            stmt = stmt.where(AccountModel.owner_person_id == person_id)
        stmt = stmt.order_by(AccountModel.name)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def add(self, account: Account) -> Account:
        model = AccountModel(
            name=account.name,
            account_type=account.account_type.value,
            owner_person_id=account.owner_person_id,
            currency=account.currency.code,
            opening_balance_paise=account.opening_balance.paise,
            opening_date=account.opening_date,
            is_archived=account.is_archived,
            notes=account.notes,
        )
        self._session.add(model)
        self._session.flush()
        account.id = model.id
        return account

    def update(self, account: Account) -> None:
        model = self._session.get(AccountModel, account.id)
        if model:
            model.name = account.name
            model.account_type = account.account_type.value
            model.owner_person_id = account.owner_person_id
            model.opening_balance_paise = account.opening_balance.paise
            model.opening_date = account.opening_date
            model.is_archived = account.is_archived
            model.notes = account.notes

    @staticmethod
    def _to_entity(m: AccountModel) -> Account:
        return Account(
            id=m.id,
            name=m.name,
            account_type=AccountType(m.account_type),
            owner_person_id=m.owner_person_id,
            currency=DEFAULT_CURRENCY,
            opening_balance=Money(m.opening_balance_paise),
            opening_date=m.opening_date,
            is_archived=m.is_archived,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class CategoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, category_id: int) -> Optional[Category]:
        model = self._session.get(CategoryModel, category_id)
        return self._to_entity(model) if model else None

    def get_all(
        self, category_type: Optional[CategoryType] = None, include_archived: bool = False
    ) -> List[Category]:
        stmt = select(CategoryModel)
        if not include_archived:
            stmt = stmt.where(CategoryModel.is_archived.is_(False))
        if category_type is not None:
            stmt = stmt.where(CategoryModel.category_type == category_type.value)
        stmt = stmt.order_by(CategoryModel.name)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def add(self, category: Category) -> Category:
        model = CategoryModel(
            name=category.name,
            category_type=category.category_type.value,
            parent_id=category.parent_id,
            icon_name=category.icon_name,
            color_code=category.color_code,
            is_archived=category.is_archived,
        )
        self._session.add(model)
        self._session.flush()
        category.id = model.id
        return category

    def update(self, category: Category) -> None:
        model = self._session.get(CategoryModel, category.id)
        if model:
            model.name = category.name
            model.category_type = category.category_type.value
            model.parent_id = category.parent_id
            model.icon_name = category.icon_name
            model.color_code = category.color_code
            model.is_archived = category.is_archived

    @staticmethod
    def _to_entity(m: CategoryModel) -> Category:
        return Category(
            id=m.id,
            name=m.name,
            category_type=CategoryType(m.category_type),
            parent_id=m.parent_id,
            icon_name=m.icon_name,
            color_code=m.color_code,
            is_archived=m.is_archived,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class TransactionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, txn_id: int) -> Optional[Transaction]:
        model = self._session.get(TransactionModel, txn_id)
        return self._to_entity(model) if model else None

    def get_by_reference(self, reference_no: str) -> Optional[Transaction]:
        stmt = select(TransactionModel).where(TransactionModel.reference_no == reference_no)
        model = self._session.scalars(stmt).first()
        return self._to_entity(model) if model else None

    def add(self, txn: Transaction) -> Transaction:
        model = TransactionModel(
            reference_no=txn.reference_no,
            transaction_date=txn.transaction_date,
            transaction_time=txn.transaction_time,
            transaction_type=txn.transaction_type.value,
            description=txn.description,
            amount_paise=txn.amount.paise,
            person_id=txn.person_id,
            category_id=txn.category_id,
            payment_method=txn.payment_method.value,
            status=txn.status.value,
            related_transaction_id=txn.related_transaction_id,
            notes=txn.notes,
        )
        self._session.add(model)
        self._session.flush()
        txn.id = model.id

        # Insert entries
        for entry in txn.entries:
            e_model = TransactionEntryModel(
                transaction_id=model.id,
                account_id=entry.account_id,
                direction=entry.direction.value,
                amount_paise=entry.amount.paise,
            )
            self._session.add(e_model)
            self._session.flush()
            entry.id = e_model.id
            entry.transaction_id = model.id

        return txn

    def update_status(self, txn_id: int, status: TransactionStatus) -> None:
        model = self._session.get(TransactionModel, txn_id)
        if model:
            model.status = status.value

    def get_entries_for_account(
        self, account_id: int, include_voided: bool = False
    ) -> List[TransactionEntry]:
        stmt = (
            select(TransactionEntryModel)
            .join(TransactionModel, TransactionEntryModel.transaction_id == TransactionModel.id)
            .where(TransactionEntryModel.account_id == account_id)
        )
        if not include_voided:
            stmt = stmt.where(TransactionModel.status != TransactionStatus.VOIDED.value)
        stmt = stmt.order_by(TransactionModel.transaction_date, TransactionModel.transaction_time)

        models = self._session.scalars(stmt).all()
        return [
            TransactionEntry(
                id=m.id,
                transaction_id=m.transaction_id,
                account_id=m.account_id,
                direction=EntryDirection(m.direction),
                amount=Money(m.amount_paise),
                created_at=m.created_at,
            )
            for m in models
        ]

    def query_transactions(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        person_id: Optional[int] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        txn_type: Optional[TransactionType] = None,
        search_text: Optional[str] = None,
        status: Optional[TransactionStatus] = None,
        limit: int = 50,
        offset: int = 0,
        include_voided: bool = True,
    ) -> Tuple[List[Transaction], int]:
        """Query transactions with filtering and pagination. Returns (transactions, total_count).

        ``include_voided=False`` is what the live ledger, dashboards and budgets use:
        deleted transactions are kept for the audit trail but must stop counting towards
        balances and reports immediately.
        """
        stmt = select(TransactionModel)

        if account_id is not None:
            stmt = stmt.join(TransactionEntryModel, TransactionModel.entries).where(
                TransactionEntryModel.account_id == account_id
            )

        if date_from is not None:
            stmt = stmt.where(TransactionModel.transaction_date >= date_from)
        if date_to is not None:
            stmt = stmt.where(TransactionModel.transaction_date <= date_to)
        if person_id is not None:
            stmt = stmt.where(TransactionModel.person_id == person_id)
        if category_id is not None:
            stmt = stmt.where(TransactionModel.category_id == category_id)
        if txn_type is not None:
            stmt = stmt.where(TransactionModel.transaction_type == txn_type.value)
        if status is not None:
            stmt = stmt.where(TransactionModel.status == status.value)
        if not include_voided:
            stmt = stmt.where(TransactionModel.status != TransactionStatus.VOIDED.value)
        if search_text and search_text.strip():
            pattern = f"%{search_text.strip()}%"
            stmt = stmt.where(
                or_(
                    TransactionModel.description.ilike(pattern),
                    TransactionModel.reference_no.ilike(pattern),
                    TransactionModel.notes.ilike(pattern),
                )
            )

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = self._session.scalar(count_stmt) or 0

        # Order and paginate
        stmt = stmt.order_by(
            TransactionModel.transaction_date.desc(), TransactionModel.transaction_time.desc()
        )
        stmt = stmt.limit(limit).offset(offset)

        models = self._session.scalars(stmt).all()
        transactions = [self._to_entity(m) for m in models]
        return transactions, total_count

    @staticmethod
    def _to_entity(m: TransactionModel) -> Transaction:
        entries = [
            TransactionEntry(
                id=e.id,
                transaction_id=e.transaction_id,
                account_id=e.account_id,
                direction=EntryDirection(e.direction),
                amount=Money(e.amount_paise),
                created_at=e.created_at,
            )
            for e in m.entries
        ]
        return Transaction(
            id=m.id,
            reference_no=m.reference_no,
            transaction_date=m.transaction_date,
            transaction_time=m.transaction_time,
            transaction_type=TransactionType(m.transaction_type),
            description=m.description,
            amount=Money(m.amount_paise),
            person_id=m.person_id,
            category_id=m.category_id,
            payment_method=PaymentMethod(m.payment_method),
            status=TransactionStatus(m.status),
            related_transaction_id=m.related_transaction_id,
            notes=m.notes,
            entries=entries,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class BudgetRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, budget_id: int) -> Optional[Budget]:
        model = self._session.get(BudgetModel, budget_id)
        return self._to_entity(model) if model else None

    def get_all(
        self, is_active: Optional[bool] = True, person_id: Optional[int] = None
    ) -> List[Budget]:
        stmt = select(BudgetModel)
        if is_active is not None:
            stmt = stmt.where(BudgetModel.is_active == is_active)
        if person_id is not None:
            stmt = stmt.where(
                or_(BudgetModel.person_id == person_id, BudgetModel.person_id.is_(None))
            )
        stmt = stmt.order_by(BudgetModel.name)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def add(self, budget: Budget) -> Budget:
        model = BudgetModel(
            name=budget.name,
            category_id=budget.category_id,
            person_id=budget.person_id,
            period_type=budget.period_type.value,
            period_start=budget.period_start,
            period_end=budget.period_end,
            limit_amount_paise=budget.limit_amount.paise,
            alert_threshold_75=budget.alert_threshold_75,
            alert_threshold_90=budget.alert_threshold_90,
            alert_threshold_100=budget.alert_threshold_100,
            is_active=budget.is_active,
        )
        self._session.add(model)
        self._session.flush()
        budget.id = model.id
        return budget

    def update(self, budget: Budget) -> None:
        model = self._session.get(BudgetModel, budget.id)
        if model:
            model.name = budget.name
            model.category_id = budget.category_id
            model.person_id = budget.person_id
            model.period_type = budget.period_type.value
            model.period_start = budget.period_start
            model.period_end = budget.period_end
            model.limit_amount_paise = budget.limit_amount.paise
            model.alert_threshold_75 = budget.alert_threshold_75
            model.alert_threshold_90 = budget.alert_threshold_90
            model.alert_threshold_100 = budget.alert_threshold_100
            model.is_active = budget.is_active

    @staticmethod
    def _to_entity(m: BudgetModel) -> Budget:
        return Budget(
            id=m.id,
            name=m.name,
            category_id=m.category_id,
            person_id=m.person_id,
            period_type=BudgetPeriod(m.period_type),
            period_start=m.period_start,
            period_end=m.period_end,
            limit_amount=Money(m.limit_amount_paise),
            alert_threshold_75=m.alert_threshold_75,
            alert_threshold_90=m.alert_threshold_90,
            alert_threshold_100=m.alert_threshold_100,
            is_active=m.is_active,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class GoalRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, goal_id: int) -> Optional[SavingsGoal]:
        model = self._session.get(SavingsGoalModel, goal_id)
        return self._to_entity(model) if model else None

    def get_all(self, person_id: Optional[int] = None) -> List[SavingsGoal]:
        stmt = select(SavingsGoalModel)
        if person_id is not None:
            stmt = stmt.where(SavingsGoalModel.person_id == person_id)
        stmt = stmt.order_by(SavingsGoalModel.name)
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def add(self, goal: SavingsGoal) -> SavingsGoal:
        model = SavingsGoalModel(
            name=goal.name,
            target_amount_paise=goal.target_amount.paise,
            current_amount_paise=goal.current_amount.paise,
            person_id=goal.person_id,
            target_date=goal.target_date,
            linked_account_id=goal.linked_account_id,
            is_achieved=goal.is_achieved,
            notes=goal.notes,
        )
        self._session.add(model)
        self._session.flush()
        goal.id = model.id
        return goal

    def update(self, goal: SavingsGoal) -> None:
        model = self._session.get(SavingsGoalModel, goal.id)
        if model:
            model.name = goal.name
            model.target_amount_paise = goal.target_amount.paise
            model.current_amount_paise = goal.current_amount.paise
            model.person_id = goal.person_id
            model.target_date = goal.target_date
            model.linked_account_id = goal.linked_account_id
            model.is_achieved = goal.is_achieved
            model.notes = goal.notes

    def add_contribution(self, contrib: GoalContribution) -> GoalContribution:
        model = GoalContributionModel(
            goal_id=contrib.goal_id,
            amount_paise=contrib.amount.paise,
            date=contrib.date,
            notes=contrib.notes,
        )
        self._session.add(model)
        self._session.flush()
        contrib.id = model.id

        # Update goal current amount
        goal_model = self._session.get(SavingsGoalModel, contrib.goal_id)
        if goal_model:
            goal_model.current_amount_paise += contrib.amount.paise
            if goal_model.current_amount_paise >= goal_model.target_amount_paise:
                goal_model.is_achieved = True
        return contrib

    @staticmethod
    def _to_entity(m: SavingsGoalModel) -> SavingsGoal:
        return SavingsGoal(
            id=m.id,
            name=m.name,
            target_amount=Money(m.target_amount_paise),
            current_amount=Money(m.current_amount_paise),
            person_id=m.person_id,
            target_date=m.target_date,
            linked_account_id=m.linked_account_id,
            is_achieved=m.is_achieved,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class DebtRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, debt_id: int) -> Optional[Debt]:
        model = self._session.get(DebtModel, debt_id)
        return self._to_entity(model) if model else None

    def get_all(
        self, is_settled: Optional[bool] = None, person_id: Optional[int] = None
    ) -> List[Debt]:
        stmt = select(DebtModel)
        if is_settled is not None:
            stmt = stmt.where(DebtModel.is_settled == is_settled)
        if person_id is not None:
            stmt = stmt.where(DebtModel.person_id == person_id)
        stmt = stmt.order_by(DebtModel.created_at.desc())
        models = self._session.scalars(stmt).all()
        return [self._to_entity(m) for m in models]

    def add(self, debt: Debt) -> Debt:
        model = DebtModel(
            debt_type=debt.debt_type.value,
            person_id=debt.person_id,
            counterparty_name=debt.counterparty_name,
            principal_amount_paise=debt.principal_amount.paise,
            remaining_amount_paise=debt.remaining_amount.paise,
            due_date=debt.due_date,
            is_settled=debt.is_settled,
            notes=debt.notes,
        )
        self._session.add(model)
        self._session.flush()
        debt.id = model.id
        return debt

    def update(self, debt: Debt) -> None:
        model = self._session.get(DebtModel, debt.id)
        if model:
            model.debt_type = debt.debt_type.value
            model.person_id = debt.person_id
            model.counterparty_name = debt.counterparty_name
            model.principal_amount_paise = debt.principal_amount.paise
            model.remaining_amount_paise = debt.remaining_amount.paise
            model.due_date = debt.due_date
            model.is_settled = debt.is_settled
            model.notes = debt.notes

    def add_payment(self, payment: DebtPayment) -> DebtPayment:
        model = DebtPaymentModel(
            debt_id=payment.debt_id,
            amount_paise=payment.amount.paise,
            payment_date=payment.payment_date,
            account_id=payment.account_id,
            notes=payment.notes,
        )
        self._session.add(model)
        self._session.flush()
        payment.id = model.id

        debt_model = self._session.get(DebtModel, payment.debt_id)
        if debt_model:
            debt_model.remaining_amount_paise = max(
                0, debt_model.remaining_amount_paise - payment.amount.paise
            )
            if debt_model.remaining_amount_paise == 0:
                debt_model.is_settled = True
        return payment

    @staticmethod
    def _to_entity(m: DebtModel) -> Debt:
        return Debt(
            id=m.id,
            debt_type=DebtType(m.debt_type),
            person_id=m.person_id,
            counterparty_name=m.counterparty_name,
            principal_amount=Money(m.principal_amount_paise),
            remaining_amount=Money(m.remaining_amount_paise),
            due_date=m.due_date,
            is_settled=m.is_settled,
            notes=m.notes,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )


class SettingsRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        model = self._session.get(AppSettingModel, key)
        return model.value if model else default

    def set(self, key: str, value: str) -> None:
        model = self._session.get(AppSettingModel, key)
        if model:
            model.value = value
        else:
            self._session.add(AppSettingModel(key=key, value=value))
