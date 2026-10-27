"""BudgetViewModel managing budgets and spending limits."""

from datetime import date
from typing import List, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import BudgetDto
from paisaflow.application.services import BudgetService
from paisaflow.domain.entities.budget import BudgetPeriod
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class BudgetViewModel(QObject):
    budgetsChanged = Signal()
    operationSuccess = Signal(str)
    operationError = Signal(str)

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._budget_service = BudgetService(uow)
        self._budgets: List[BudgetDto] = []
        self._person_filter: Optional[int] = None
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._person_filter = person_id if person_id > 0 else None
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._budgets = self._budget_service.get_budgets(
            is_active=True, person_id=self._person_filter
        )
        self.budgetsChanged.emit()

    @Property(list, notify=budgetsChanged)
    def budgets(self) -> list:
        return [
            {
                "id": b.id,
                "name": b.name,
                "categoryName": b.category_name,
                "personName": b.person_name,
                "periodType": b.period_type,
                "periodStart": b.period_start,
                "periodEnd": b.period_end,
                "limit": b.limit_formatted,
                "spent": b.spent_formatted,
                "remaining": b.remaining_formatted,
                "utilization": b.utilization_percentage,
                "statusLevel": b.status_level,
                "isActive": b.is_active,
            }
            for b in self._budgets
        ]

    @Slot(str, int, int, str, str, str, str, result=bool)
    def createBudget(
        self,
        name: str,
        category_id: int,
        person_id: int,
        period_type_str: str,
        start_date_str: str,
        end_date_str: str,
        limit_str: str,
    ) -> bool:
        try:
            if not name.strip():
                self.operationError.emit("Budget name cannot be empty.")
                return False

            limit_money = Money.from_str(limit_str)
            if limit_money.paise <= 0:
                self.operationError.emit("Budget limit must be greater than zero.")
                return False

            period_type = BudgetPeriod(period_type_str.lower())
            p_start = (
                date.fromisoformat(start_date_str)
                if start_date_str
                else date.today().replace(day=1)
            )
            if end_date_str:
                p_end = date.fromisoformat(end_date_str)
            else:
                # Default to end of current month
                if p_start.month == 12:
                    p_end = date(p_start.year, 12, 31)
                else:
                    next_month = date(p_start.year, p_start.month + 1, 1)
                    p_end = date.fromordinal(next_month.toordinal() - 1)

            cat_id = category_id if category_id > 0 else None
            p_id = person_id if person_id > 0 else None

            self._budget_service.create_budget(
                name=name.strip(),
                category_id=cat_id,
                person_id=p_id,
                period_type=period_type,
                period_start=p_start,
                period_end=p_end,
                limit_amount=limit_money,
            )
            self.operationSuccess.emit(f"Budget '{name}' created successfully.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False
