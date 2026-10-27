"""DebtViewModel managing debts (money lent and borrowed) and repayments."""

from datetime import date
from typing import List, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import DebtDto
from paisaflow.application.services import DebtService
from paisaflow.domain.entities.debt import DebtType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class DebtViewModel(QObject):
    debtsChanged = Signal()
    operationSuccess = Signal(str)
    operationError = Signal(str)

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._debt_service = DebtService(uow)
        self._debts: List[DebtDto] = []
        self._person_filter: Optional[int] = None
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._person_filter = person_id if person_id > 0 else None
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._debts = self._debt_service.get_debts(is_settled=None, person_id=self._person_filter)
        self.debtsChanged.emit()

    @Property(list, notify=debtsChanged)
    def debts(self) -> list:
        return [
            {
                "id": d.id,
                "debtType": d.debt_type,
                "debtTypeDisplay": d.debt_type_display,
                "personName": d.person_name,
                "counterparty": d.counterparty_name,
                "principal": d.principal_formatted,
                "remaining": d.remaining_formatted,
                "dueDate": d.due_date or "No due date",
                "isSettled": d.is_settled,
                "isLiability": d.is_liability,
                "notes": d.notes or "",
            }
            for d in self._debts
        ]

    @Slot(str, int, str, str, str, str)
    def recordDebt(
        self,
        debt_type_str: str,
        person_id: int,
        counterparty: str,
        principal_str: str,
        due_date_str: str,
        notes: str,
    ) -> bool:
        try:
            if not counterparty.strip():
                self.operationError.emit("Counterparty name cannot be empty.")
                return False

            principal_money = Money.from_str(principal_str)
            if principal_money.paise <= 0:
                self.operationError.emit("Principal amount must be greater than zero.")
                return False

            dtype = DebtType(debt_type_str.lower())
            d_date = date.fromisoformat(due_date_str) if due_date_str else None

            self._debt_service.record_debt(
                debt_type=dtype,
                person_id=person_id,
                counterparty_name=counterparty.strip(),
                principal_amount=principal_money,
                due_date=d_date,
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Recorded debt with {counterparty}.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int, str, str)
    def recordPayment(self, debt_id: int, amount_str: str, notes: str) -> bool:
        try:
            money = Money.from_str(amount_str)
            if money.paise <= 0:
                self.operationError.emit("Payment amount must be greater than zero.")
                return False

            self._debt_service.record_payment(
                debt_id=debt_id,
                amount=money,
                payment_date=date.today(),
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Recorded repayment of {money.format()}.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False
