"""Application use case services coordinating domain policies and data persistence."""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from paisaflow.application.dto import (
    AccountDto,
    BudgetDto,
    CategoryDto,
    CategorySpendingDto,
    DebtDto,
    GoalDto,
    OverviewSummaryDto,
    PersonDto,
    TransactionDto,
)
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
    generate_reference_no,
)
from paisaflow.domain.exceptions import (
    AccountArchivedError,
    CategoryArchivedError,
    EntityNotFoundError,
    IncompatibleCategoryError,
    InvalidDebtPaymentError,
    InvalidTransferError,
)
from paisaflow.domain.policies.ledger_policy import LedgerPolicy
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


def _format_timestamp(value: Optional[datetime]) -> str:
    """Render a stored UTC timestamp in local time for display in the UI.

    SQLite hands back naive datetimes, so anything without a tzinfo is treated as UTC
    (every writer stores ``datetime.now(timezone.utc)``).
    """
    if value is None:
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone().strftime("%d %b %Y, %H:%M")


class PersonService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def create_person(
        self, name: str, color_code: str = "#B8F28B", avatar_path: Optional[str] = None
    ) -> PersonDto:
        person = Person(
            id=None,
            name=name,
            color_code=color_code,
            avatar_path=avatar_path,
        )
        with self._uow as uow:
            uow.people.add(person)
            uow.commit()
            return self._to_dto(person)

    def update_person(
        self,
        person_id: int,
        name: str,
        color_code: str = "#B8F28B",
        avatar_path: Optional[str] = None,
        is_active: bool = True,
    ) -> PersonDto:
        with self._uow as uow:
            person = uow.people.get_by_id(person_id)
            if not person:
                raise EntityNotFoundError(f"Person with ID {person_id} not found.")
            person.name = name
            person.color_code = color_code
            person.avatar_path = avatar_path
            person.is_active = is_active
            uow.people.update(person)
            uow.commit()
            return self._to_dto(person)

    def get_people(self, include_inactive: bool = False) -> List[PersonDto]:
        with self._uow as uow:
            people = uow.people.get_all(include_inactive=include_inactive)
            return [self._to_dto(p) for p in people]

    def get_person_by_id(self, person_id: int) -> Optional[PersonDto]:
        with self._uow as uow:
            p = uow.people.get_by_id(person_id)
            return self._to_dto(p) if p else None

    @staticmethod
    def _to_dto(p: Person) -> PersonDto:
        return PersonDto(
            id=p.id or 0,
            name=p.name,
            color_code=p.color_code,
            avatar_path=p.avatar_path,
            is_active=p.is_active,
        )


class AccountService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def create_account(
        self,
        name: str,
        account_type: AccountType,
        owner_person_id: int,
        opening_balance: Optional[Money] = None,
        opening_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> AccountDto:
        initial_balance = opening_balance if opening_balance is not None else Money.zero()
        account = Account(
            id=None,
            name=name,
            account_type=account_type,
            owner_person_id=owner_person_id,
            opening_balance=initial_balance,
            opening_date=opening_date or date.today(),
            notes=notes,
        )
        with self._uow as uow:
            # Verify owner exists
            owner = uow.people.get_by_id(owner_person_id)
            if not owner:
                raise EntityNotFoundError(f"Owner person with ID {owner_person_id} not found.")
            uow.accounts.add(account)
            uow.commit()
            return self._to_dto(account, owner.name, initial_balance)

    def get_accounts(
        self, include_archived: bool = False, person_id: Optional[int] = None
    ) -> List[AccountDto]:
        with self._uow as uow:
            accounts = uow.accounts.get_all(include_archived=include_archived, person_id=person_id)
            dtos = []
            for acct in accounts:
                owner = uow.people.get_by_id(acct.owner_person_id)
                owner_name = owner.name if owner else "Unknown"
                entries = uow.transactions.get_entries_for_account(acct.id or 0)
                balance = LedgerPolicy.calculate_account_balance(acct, entries)
                dtos.append(self._to_dto(acct, owner_name, balance))
            return dtos

    def get_account_by_id(self, account_id: int) -> Optional[AccountDto]:
        with self._uow as uow:
            acct = uow.accounts.get_by_id(account_id)
            if not acct:
                return None
            owner = uow.people.get_by_id(acct.owner_person_id)
            owner_name = owner.name if owner else "Unknown"
            entries = uow.transactions.get_entries_for_account(acct.id or 0)
            balance = LedgerPolicy.calculate_account_balance(acct, entries)
            return self._to_dto(acct, owner_name, balance)

    def archive_account(self, account_id: int) -> None:
        with self._uow as uow:
            acct = uow.accounts.get_by_id(account_id)
            if not acct:
                raise EntityNotFoundError(f"Account with ID {account_id} not found.")
            acct.is_archived = True
            uow.accounts.update(acct)
            uow.commit()

    @staticmethod
    def _to_dto(acct: Account, owner_name: str, current_balance: Money) -> AccountDto:
        return AccountDto(
            id=acct.id or 0,
            name=acct.name,
            account_type=acct.account_type.value,
            account_type_display=acct.account_type.display_name,
            owner_person_id=acct.owner_person_id,
            owner_name=owner_name,
            opening_balance_formatted=acct.opening_balance.format(),
            balance_formatted=current_balance.format(),
            balance_paise=current_balance.paise,
            is_liability=acct.is_liability,
            is_archived=acct.is_archived,
            notes=acct.notes,
        )


class CategoryService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def get_categories(
        self, category_type: Optional[CategoryType] = None, include_archived: bool = False
    ) -> List[CategoryDto]:
        with self._uow as uow:
            cats = uow.categories.get_all(
                category_type=category_type, include_archived=include_archived
            )
            return [
                CategoryDto(
                    id=c.id or 0,
                    name=c.name,
                    category_type=c.category_type.value,
                    category_type_display=c.category_type.display_name,
                    icon_name=c.icon_name,
                    color_code=c.color_code,
                    is_archived=c.is_archived,
                )
                for c in cats
            ]

    def create_category(
        self,
        name: str,
        category_type: CategoryType,
        icon_name: str = "tag",
        color_code: str = "#82C9D4",
        parent_id: Optional[int] = None,
    ) -> CategoryDto:
        cat = Category(
            id=None,
            name=name,
            category_type=category_type,
            icon_name=icon_name,
            color_code=color_code,
            parent_id=parent_id,
        )
        with self._uow as uow:
            uow.categories.add(cat)
            uow.commit()
            return CategoryDto(
                id=cat.id or 0,
                name=cat.name,
                category_type=cat.category_type.value,
                category_type_display=cat.category_type.display_name,
                icon_name=cat.icon_name,
                color_code=cat.color_code,
                is_archived=cat.is_archived,
            )


class TransactionService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def record_income(
        self,
        transaction_date: date,
        description: str,
        amount: Money,
        account_id: int,
        person_id: int,
        category_id: int,
        payment_method: PaymentMethod = PaymentMethod.UPI,
        notes: Optional[str] = None,
    ) -> TransactionDto:
        with self._uow as uow:
            # Validate account and category
            acct = uow.accounts.get_by_id(account_id)
            if not acct:
                raise EntityNotFoundError(f"Account {account_id} not found.")
            if acct.is_archived:
                raise AccountArchivedError("Cannot post transactions to an archived account.")

            self._validate_person(uow, person_id)
            self._validate_category(uow, category_id, CategoryType.INCOME)

            txn = Transaction(
                id=None,
                reference_no=generate_reference_no(transaction_date),
                transaction_date=transaction_date,
                transaction_time=datetime.now(timezone.utc).time(),
                transaction_type=TransactionType.INCOME,
                description=description,
                amount=amount,
                person_id=person_id,
                category_id=category_id,
                payment_method=payment_method,
                notes=notes,
                entries=[
                    TransactionEntry(
                        id=None,
                        transaction_id=None,
                        account_id=account_id,
                        direction=EntryDirection.INFLOW,
                        amount=amount,
                    )
                ],
            )
            LedgerPolicy.validate_transaction_entries(txn)
            uow.transactions.add(txn)
            uow.commit()
            return self._to_dto(txn, uow)

    def record_expense(
        self,
        transaction_date: date,
        description: str,
        amount: Money,
        account_id: int,
        person_id: int,
        category_id: int,
        payment_method: PaymentMethod = PaymentMethod.UPI,
        notes: Optional[str] = None,
    ) -> TransactionDto:
        with self._uow as uow:
            acct = uow.accounts.get_by_id(account_id)
            if not acct:
                raise EntityNotFoundError(f"Account {account_id} not found.")
            if acct.is_archived:
                raise AccountArchivedError("Cannot post transactions to an archived account.")

            self._validate_person(uow, person_id)
            self._validate_category(uow, category_id, CategoryType.EXPENSE)

            txn = Transaction(
                id=None,
                reference_no=generate_reference_no(transaction_date),
                transaction_date=transaction_date,
                transaction_time=datetime.now(timezone.utc).time(),
                transaction_type=TransactionType.EXPENSE,
                description=description,
                amount=amount,
                person_id=person_id,
                category_id=category_id,
                payment_method=payment_method,
                notes=notes,
                entries=[
                    TransactionEntry(
                        id=None,
                        transaction_id=None,
                        account_id=account_id,
                        direction=EntryDirection.OUTFLOW,
                        amount=amount,
                    )
                ],
            )
            LedgerPolicy.validate_transaction_entries(txn)
            uow.transactions.add(txn)
            uow.commit()
            return self._to_dto(txn, uow)

    def record_transfer(
        self,
        transaction_date: date,
        description: str,
        amount: Money,
        source_account_id: int,
        dest_account_id: int,
        person_id: int,
        payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER,
        notes: Optional[str] = None,
    ) -> TransactionDto:
        if source_account_id == dest_account_id:
            raise InvalidTransferError("Source and destination accounts must be different.")

        with self._uow as uow:
            src = uow.accounts.get_by_id(source_account_id)
            dst = uow.accounts.get_by_id(dest_account_id)
            if not src or not dst:
                raise EntityNotFoundError("Source or destination account not found.")
            if src.is_archived or dst.is_archived:
                raise AccountArchivedError("Cannot transfer funds involving archived accounts.")
            self._validate_person(uow, person_id)

            txn = Transaction(
                id=None,
                reference_no=generate_reference_no(transaction_date),
                transaction_date=transaction_date,
                transaction_time=datetime.now(timezone.utc).time(),
                transaction_type=TransactionType.TRANSFER,
                description=description,
                amount=amount,
                person_id=person_id,
                category_id=None,
                payment_method=payment_method,
                notes=notes,
                entries=[
                    TransactionEntry(
                        id=None,
                        transaction_id=None,
                        account_id=source_account_id,
                        direction=EntryDirection.OUTFLOW,
                        amount=amount,
                    ),
                    TransactionEntry(
                        id=None,
                        transaction_id=None,
                        account_id=dest_account_id,
                        direction=EntryDirection.INFLOW,
                        amount=amount,
                    ),
                ],
            )
            LedgerPolicy.validate_transaction_entries(txn)
            uow.transactions.add(txn)
            uow.commit()
            return self._to_dto(txn, uow)

    @staticmethod
    def _validate_person(uow: SqlAlchemyUnitOfWork, person_id: int) -> None:
        """Reject transactions attributed to a person that does not exist."""
        if not uow.people.get_by_id(person_id):
            raise EntityNotFoundError(f"Person {person_id} not found.")

    @staticmethod
    def _validate_category(
        uow: SqlAlchemyUnitOfWork, category_id: int, expected_type: CategoryType
    ) -> None:
        """Ensure the category exists, is active, and matches the transaction type.

        Posting an expense against an income category (or vice versa) would silently
        corrupt category breakdowns, budget actuals, and reports, so it is rejected.
        """
        cat = uow.categories.get_by_id(category_id)
        if not cat:
            raise EntityNotFoundError(f"Category {category_id} not found.")
        if cat.is_archived:
            raise CategoryArchivedError(
                f"Category '{cat.name}' is archived and cannot receive new transactions."
            )
        if cat.category_type != expected_type:
            raise IncompatibleCategoryError(
                f"Category '{cat.name}' is a {cat.category_type.value} category and cannot be "
                f"used for a {expected_type.value} transaction."
            )

    def void_transaction(self, transaction_id: int) -> None:
        with self._uow as uow:
            txn = uow.transactions.get_by_id(transaction_id)
            if not txn:
                raise EntityNotFoundError(f"Transaction {transaction_id} not found.")
            uow.transactions.update_status(transaction_id, TransactionStatus.VOIDED)
            uow.commit()

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
    ) -> Tuple[List[TransactionDto], int]:
        with self._uow as uow:
            txns, total = uow.transactions.query_transactions(
                date_from=date_from,
                date_to=date_to,
                person_id=person_id,
                account_id=account_id,
                category_id=category_id,
                txn_type=txn_type,
                search_text=search_text,
                status=status,
                limit=limit,
                offset=offset,
                include_voided=include_voided,
            )
            return [self._to_dto(t, uow) for t in txns], total

    @staticmethod
    def _to_dto(t: Transaction, uow: SqlAlchemyUnitOfWork) -> TransactionDto:
        person = uow.people.get_by_id(t.person_id)
        person_name = person.name if person else "Unknown"
        cat_name = ""
        if t.category_id:
            cat = uow.categories.get_by_id(t.category_id)
            cat_name = cat.name if cat else ""

        affected = []
        for e in t.entries:
            acct = uow.accounts.get_by_id(e.account_id)
            acct_name = acct.name if acct else f"Account #{e.account_id}"
            affected.append(f"{acct_name} ({e.direction.value})")

        return TransactionDto(
            id=t.id or 0,
            reference_no=t.reference_no,
            transaction_date=t.transaction_date.isoformat(),
            transaction_time=t.transaction_time.strftime("%H:%M:%S"),
            transaction_type=t.transaction_type.value,
            transaction_type_display=t.transaction_type.display_name,
            description=t.description,
            amount_formatted=t.amount.format(),
            amount_paise=t.amount.paise,
            person_id=t.person_id,
            person_name=person_name,
            category_id=t.category_id,
            category_name=cat_name,
            payment_method=t.payment_method.value,
            payment_method_display=t.payment_method.display_name,
            status=t.status.value,
            notes=t.notes,
            affected_accounts=", ".join(affected),
            created_at=_format_timestamp(t.created_at),
            updated_at=_format_timestamp(t.updated_at),
            voided_at=(
                _format_timestamp(t.updated_at) if t.status == TransactionStatus.VOIDED else ""
            ),
        )


class BudgetService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def create_budget(
        self,
        name: str,
        category_id: Optional[int],
        person_id: Optional[int],
        period_type: BudgetPeriod,
        period_start: date,
        period_end: date,
        limit_amount: Money,
    ) -> BudgetDto:
        budget = Budget(
            id=None,
            name=name,
            category_id=category_id,
            person_id=person_id,
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            limit_amount=limit_amount,
        )
        with self._uow as uow:
            uow.budgets.add(budget)
            uow.commit()
            return self._to_dto(budget, uow)

    def get_budgets(
        self, is_active: Optional[bool] = True, person_id: Optional[int] = None
    ) -> List[BudgetDto]:
        with self._uow as uow:
            budgets = uow.budgets.get_all(is_active=is_active, person_id=person_id)
            return [self._to_dto(b, uow) for b in budgets]

    @staticmethod
    def _to_dto(budget: Budget, uow: SqlAlchemyUnitOfWork) -> BudgetDto:
        # Calculate actual spending within budget period
        txns, _ = uow.transactions.query_transactions(
            date_from=budget.period_start,
            date_to=budget.period_end,
            person_id=budget.person_id,
            category_id=budget.category_id,
            txn_type=TransactionType.EXPENSE,
            status=TransactionStatus.COMPLETED,
            limit=100000,
        )
        total_spent_paise = sum(t.amount.paise for t in txns)
        actual_spent = Money(total_spent_paise)

        pct, remaining, status = budget.calculate_utilization(actual_spent)

        cat_name = "All Categories"
        if budget.category_id:
            c = uow.categories.get_by_id(budget.category_id)
            cat_name = c.name if c else "Unknown"

        person_name = "Household (All)"
        if budget.person_id:
            p = uow.people.get_by_id(budget.person_id)
            person_name = p.name if p else "Unknown"

        return BudgetDto(
            id=budget.id or 0,
            name=budget.name,
            category_id=budget.category_id,
            category_name=cat_name,
            person_id=budget.person_id,
            person_name=person_name,
            period_type=budget.period_type.value,
            period_start=budget.period_start.isoformat(),
            period_end=budget.period_end.isoformat(),
            limit_formatted=budget.limit_amount.format(),
            spent_formatted=actual_spent.format(),
            remaining_formatted=remaining.format(),
            utilization_percentage=float(pct),
            status_level=status.value,
            is_active=budget.is_active,
        )


class GoalService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def create_goal(
        self,
        name: str,
        target_amount: Money,
        person_id: int,
        target_date: Optional[date] = None,
        linked_account_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> GoalDto:
        goal = SavingsGoal(
            id=None,
            name=name,
            target_amount=target_amount,
            current_amount=Money(0),
            person_id=person_id,
            target_date=target_date,
            linked_account_id=linked_account_id,
            notes=notes,
        )
        with self._uow as uow:
            uow.goals.add(goal)
            uow.commit()
            return self._to_dto(goal, uow)

    def contribute_to_goal(
        self, goal_id: int, amount: Money, date_: date, notes: Optional[str] = None
    ) -> GoalDto:
        contrib = GoalContribution(
            id=None,
            goal_id=goal_id,
            amount=amount,
            date=date_,
            notes=notes,
        )
        with self._uow as uow:
            goal = uow.goals.get_by_id(goal_id)
            if not goal:
                raise EntityNotFoundError(f"Goal {goal_id} not found.")
            uow.goals.add_contribution(contrib)
            uow.commit()
            updated_goal = uow.goals.get_by_id(goal_id)
            return self._to_dto(updated_goal or goal, uow)

    def get_goals(self, person_id: Optional[int] = None) -> List[GoalDto]:
        with self._uow as uow:
            goals = uow.goals.get_all(person_id=person_id)
            return [self._to_dto(g, uow) for g in goals]

    @staticmethod
    def _to_dto(g: SavingsGoal, uow: SqlAlchemyUnitOfWork) -> GoalDto:
        person = uow.people.get_by_id(g.person_id)
        person_name = person.name if person else "Unknown"
        return GoalDto(
            id=g.id or 0,
            name=g.name,
            target_formatted=g.target_amount.format(),
            current_formatted=g.current_amount.format(),
            remaining_formatted=g.remaining_amount.format(),
            progress_percentage=float(g.progress_percentage),
            person_id=g.person_id,
            person_name=person_name,
            target_date=g.target_date.isoformat() if g.target_date else None,
            is_achieved=g.is_achieved,
            notes=g.notes,
        )


class DebtService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def record_debt(
        self,
        debt_type: DebtType,
        person_id: int,
        counterparty_name: str,
        principal_amount: Money,
        due_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> DebtDto:
        debt = Debt(
            id=None,
            debt_type=debt_type,
            person_id=person_id,
            counterparty_name=counterparty_name,
            principal_amount=principal_amount,
            remaining_amount=principal_amount,
            due_date=due_date,
            notes=notes,
        )
        with self._uow as uow:
            uow.debts.add(debt)
            uow.commit()
            return self._to_dto(debt, uow)

    def record_payment(
        self,
        debt_id: int,
        amount: Money,
        payment_date: date,
        account_id: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> DebtDto:
        if amount.paise <= 0:
            raise InvalidDebtPaymentError("Repayment amount must be strictly positive.")

        payment = DebtPayment(
            id=None,
            debt_id=debt_id,
            amount=amount,
            payment_date=payment_date,
            account_id=account_id,
            notes=notes,
        )
        with self._uow as uow:
            debt = uow.debts.get_by_id(debt_id)
            if not debt:
                raise EntityNotFoundError(f"Debt {debt_id} not found.")
            if debt.is_settled:
                raise InvalidDebtPaymentError(
                    f"Debt {debt_id} is already fully settled; no further repayment can be recorded."
                )
            if amount.paise > debt.remaining_amount.paise:
                raise InvalidDebtPaymentError(
                    "Repayment of "
                    f"{amount.format()} exceeds the outstanding balance of "
                    f"{debt.remaining_amount.format()}."
                )
            if account_id is not None and not uow.accounts.get_by_id(account_id):
                raise EntityNotFoundError(f"Account {account_id} not found.")
            uow.debts.add_payment(payment)
            uow.commit()
            updated_debt = uow.debts.get_by_id(debt_id)
            return self._to_dto(updated_debt or debt, uow)

    def get_debts(
        self, is_settled: Optional[bool] = None, person_id: Optional[int] = None
    ) -> List[DebtDto]:
        with self._uow as uow:
            debts = uow.debts.get_all(is_settled=is_settled, person_id=person_id)
            return [self._to_dto(d, uow) for d in debts]

    @staticmethod
    def _to_dto(d: Debt, uow: SqlAlchemyUnitOfWork) -> DebtDto:
        p = uow.people.get_by_id(d.person_id)
        person_name = p.name if p else "Unknown"
        return DebtDto(
            id=d.id or 0,
            debt_type=d.debt_type.value,
            debt_type_display=d.debt_type.display_name,
            person_id=d.person_id,
            person_name=person_name,
            counterparty_name=d.counterparty_name,
            principal_formatted=d.principal_amount.format(),
            remaining_formatted=d.remaining_amount.format(),
            due_date=d.due_date.isoformat() if d.due_date else None,
            is_settled=d.is_settled,
            is_liability=d.debt_type.is_liability,
            notes=d.notes,
        )


class OverviewService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def get_overview_summary(
        self, person_id: Optional[int] = None, target_date: Optional[date] = None
    ) -> OverviewSummaryDto:
        curr_date = target_date or date.today()
        month_start = curr_date.replace(day=1)
        # Month end
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1)

        with self._uow as uow:
            # 1. Calculate Account Balances
            accounts = uow.accounts.get_all(include_archived=False, person_id=person_id)
            total_assets_paise = 0
            total_liabilities_paise = 0

            for acct in accounts:
                entries = uow.transactions.get_entries_for_account(acct.id or 0)
                bal = LedgerPolicy.calculate_account_balance(acct, entries)
                if acct.is_liability:
                    total_liabilities_paise += bal.paise
                else:
                    total_assets_paise += bal.paise

            # Include debts
            debts = uow.debts.get_all(is_settled=False, person_id=person_id)
            for d in debts:
                if d.debt_type == DebtType.LENT:
                    total_assets_paise += d.remaining_amount.paise
                elif d.debt_type == DebtType.BORROWED:
                    total_liabilities_paise += d.remaining_amount.paise

            net_worth_paise = total_assets_paise - total_liabilities_paise

            # 2. Month Income and Expenses
            month_income_txns, _ = uow.transactions.query_transactions(
                date_from=month_start,
                date_to=month_end,
                person_id=person_id,
                txn_type=TransactionType.INCOME,
                status=TransactionStatus.COMPLETED,
                limit=100000,
            )
            income_month_paise = sum(t.amount.paise for t in month_income_txns)

            month_expense_txns, _ = uow.transactions.query_transactions(
                date_from=month_start,
                date_to=month_end,
                person_id=person_id,
                txn_type=TransactionType.EXPENSE,
                status=TransactionStatus.COMPLETED,
                limit=100000,
            )
            expenses_month_paise = sum(t.amount.paise for t in month_expense_txns)
            net_cash_flow_paise = income_month_paise - expenses_month_paise

            # 3. Category Breakdown for Month Expenses
            category_totals: dict[int, int] = {}
            for t in month_expense_txns:
                cid = t.category_id or 0
                category_totals[cid] = category_totals.get(cid, 0) + t.amount.paise

            cat_breakdown: List[CategorySpendingDto] = []
            for cid, total_paise in sorted(
                category_totals.items(), key=lambda x: x[1], reverse=True
            ):
                cat = uow.categories.get_by_id(cid) if cid != 0 else None
                name = cat.name if cat else "Uncategorized"
                color = cat.color_code if cat else "#82C9D4"
                pct = (
                    (Decimal(total_paise) / Decimal(expenses_month_paise) * 100).quantize(
                        Decimal("0.1")
                    )
                    if expenses_month_paise > 0
                    else Decimal(0)
                )
                cat_breakdown.append(
                    CategorySpendingDto(
                        category_name=name,
                        color_code=color,
                        amount_paise=total_paise,
                        amount_formatted=Money(total_paise).format(),
                        percentage=float(pct),
                    )
                )

            # 4. Recent Transactions (last 10). Deleted records live in the ledger's
            # History tab only, so they must not resurface on the dashboard.
            recent_txns, _ = uow.transactions.query_transactions(
                person_id=person_id,
                status=TransactionStatus.COMPLETED,
                limit=10,
                offset=0,
            )
            recent_dtos = [TransactionService._to_dto(t, uow) for t in recent_txns]

            # 5. Overall Budget utilization
            budgets = uow.budgets.get_all(is_active=True, person_id=person_id)
            total_budget_limit = sum(b.limit_amount.paise for b in budgets)
            budget_util_pct = (
                float(Decimal(expenses_month_paise) / Decimal(total_budget_limit) * 100)
                if total_budget_limit > 0
                else 0.0
            )

            return OverviewSummaryDto(
                total_assets_formatted=Money(total_assets_paise).format(),
                total_assets_paise=total_assets_paise,
                total_liabilities_formatted=Money(total_liabilities_paise).format(),
                total_liabilities_paise=total_liabilities_paise,
                net_worth_formatted=Money(net_worth_paise).format(),
                net_worth_paise=net_worth_paise,
                income_month_formatted=Money(income_month_paise).format(),
                income_month_paise=income_month_paise,
                expenses_month_formatted=Money(expenses_month_paise).format(),
                expenses_month_paise=expenses_month_paise,
                net_cash_flow_formatted=Money(net_cash_flow_paise).format(),
                net_cash_flow_paise=net_cash_flow_paise,
                budget_utilization_percentage=round(budget_util_pct, 1),
                recent_transactions=recent_dtos,
                category_spending=cat_breakdown,
            )
