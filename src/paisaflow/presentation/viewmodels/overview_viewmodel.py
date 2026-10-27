"""OverviewViewModel providing high-level financial metrics and charts data."""

from typing import Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import OverviewSummaryDto
from paisaflow.application.services import OverviewService
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class OverviewViewModel(QObject):
    overviewChanged = Signal()

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._overview_service = OverviewService(uow)
        self._summary: Optional[OverviewSummaryDto] = None
        self._current_person_id: Optional[int] = None
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._current_person_id = person_id if person_id > 0 else None
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._summary = self._overview_service.get_overview_summary(
            person_id=self._current_person_id
        )
        self.overviewChanged.emit()

    @Property(bool, notify=overviewChanged)
    def hasData(self) -> bool:
        if not self._summary:
            return False
        return (
            self._summary.total_assets_paise != 0
            or self._summary.total_liabilities_paise != 0
            or len(self._summary.recent_transactions) > 0
        )

    @Property(str, notify=overviewChanged)
    def totalAssets(self) -> str:
        return self._summary.total_assets_formatted if self._summary else "₹0.00"

    @Property(str, notify=overviewChanged)
    def totalLiabilities(self) -> str:
        return self._summary.total_liabilities_formatted if self._summary else "₹0.00"

    @Property(str, notify=overviewChanged)
    def netWorth(self) -> str:
        return self._summary.net_worth_formatted if self._summary else "₹0.00"

    @Property(int, notify=overviewChanged)
    def netWorthPaise(self) -> int:
        return self._summary.net_worth_paise if self._summary else 0

    @Property(str, notify=overviewChanged)
    def incomeMonth(self) -> str:
        return self._summary.income_month_formatted if self._summary else "₹0.00"

    @Property(str, notify=overviewChanged)
    def expensesMonth(self) -> str:
        return self._summary.expenses_month_formatted if self._summary else "₹0.00"

    @Property(str, notify=overviewChanged)
    def netCashFlow(self) -> str:
        return self._summary.net_cash_flow_formatted if self._summary else "₹0.00"

    @Property(int, notify=overviewChanged)
    def netCashFlowPaise(self) -> int:
        return self._summary.net_cash_flow_paise if self._summary else 0

    @Property(float, notify=overviewChanged)
    def budgetUtilization(self) -> float:
        return self._summary.budget_utilization_percentage if self._summary else 0.0

    @Property(list, notify=overviewChanged)
    def recentTransactions(self) -> list:
        if not self._summary:
            return []
        return [
            {
                "id": t.id,
                "referenceNo": t.reference_no,
                "date": t.transaction_date,
                "type": t.transaction_type,
                "typeDisplay": t.transaction_type_display,
                "description": t.description,
                "amount": t.amount_formatted,
                "amountPaise": t.amount_paise,
                "personName": t.person_name,
                "categoryName": t.category_name,
                "paymentMethod": t.payment_method_display,
                "status": t.status,
            }
            for t in self._summary.recent_transactions
        ]

    @Property(list, notify=overviewChanged)
    def categorySpending(self) -> list:
        if not self._summary:
            return []
        return [
            {
                "label": c.category_name,
                "color": c.color_code,
                "amount": c.amount_formatted,
                "amountPaise": c.amount_paise,
                "percentage": c.percentage,
            }
            for c in self._summary.category_spending
        ]
