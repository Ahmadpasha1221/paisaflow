"""ReportsViewModel providing trend analysis, monthly income vs expenses, and category breakdown."""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.domain.entities.transaction import TransactionStatus, TransactionType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class ReportsViewModel(QObject):
    reportsChanged = Signal()

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._person_filter: Optional[int] = None
        self._monthly_trends: List[dict] = []
        self._category_shares: List[dict] = []
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._person_filter = person_id if person_id > 0 else None
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        today = date.today()
        trends = []

        with self._uow as uow:
            # Generate trends for the last 6 calendar months
            for i in range(5, -1, -1):
                # Calculate month year
                m_num = today.month - i
                y_num = today.year
                while m_num <= 0:
                    m_num += 12
                    y_num -= 1

                m_start = date(y_num, m_num, 1)
                if m_num == 12:
                    m_end = date(y_num + 1, 1, 1)
                else:
                    m_end = date(y_num, m_num + 1, 1)

                month_name = m_start.strftime("%b %Y")

                income_txns, _ = uow.transactions.query_transactions(
                    date_from=m_start,
                    date_to=m_end,
                    person_id=self._person_filter,
                    txn_type=TransactionType.INCOME,
                    status=TransactionStatus.COMPLETED,
                    limit=100000,
                )
                inc_paise = sum(t.amount.paise for t in income_txns)

                expense_txns, _ = uow.transactions.query_transactions(
                    date_from=m_start,
                    date_to=m_end,
                    person_id=self._person_filter,
                    txn_type=TransactionType.EXPENSE,
                    status=TransactionStatus.COMPLETED,
                    limit=100000,
                )
                exp_paise = sum(t.amount.paise for t in expense_txns)
                net_paise = inc_paise - exp_paise

                trends.append(
                    {
                        "month": month_name,
                        "income": Money(inc_paise).format(),
                        "incomePaise": inc_paise,
                        "expenses": Money(exp_paise).format(),
                        "expensesPaise": exp_paise,
                        "net": Money(net_paise).format(),
                        "netPaise": net_paise,
                    }
                )

            # Lifetime category spending
            all_expenses, _ = uow.transactions.query_transactions(
                person_id=self._person_filter,
                txn_type=TransactionType.EXPENSE,
                status=TransactionStatus.COMPLETED,
                limit=100000,
            )
            total_exp_paise = sum(t.amount.paise for t in all_expenses)
            cat_map: dict[int, int] = {}
            for t in all_expenses:
                cid = t.category_id or 0
                cat_map[cid] = cat_map.get(cid, 0) + t.amount.paise

            cat_shares = []
            for cid, amt in sorted(cat_map.items(), key=lambda x: x[1], reverse=True):
                cat = uow.categories.get_by_id(cid) if cid != 0 else None
                c_name = cat.name if cat else "Uncategorized"
                c_color = cat.color_code if cat else "#82C9D4"
                pct = (
                    (Decimal(amt) / Decimal(total_exp_paise) * 100).quantize(Decimal("0.1"))
                    if total_exp_paise > 0
                    else Decimal(0)
                )
                cat_shares.append(
                    {
                        "category": c_name,
                        "color": c_color,
                        "amount": Money(amt).format(),
                        "amountPaise": amt,
                        "percentage": float(pct),
                    }
                )

        self._monthly_trends = trends
        self._category_shares = cat_shares
        self.reportsChanged.emit()

    @Property(list, notify=reportsChanged)
    def monthlyTrends(self) -> list:
        return self._monthly_trends

    @Property(list, notify=reportsChanged)
    def categoryShares(self) -> list:
        return self._category_shares
