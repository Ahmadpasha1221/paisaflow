"""GoalViewModel managing savings goals and contributions."""

from datetime import date
from typing import List, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import GoalDto
from paisaflow.application.services import GoalService
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class GoalViewModel(QObject):
    goalsChanged = Signal()
    operationSuccess = Signal(str)
    operationError = Signal(str)

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._goal_service = GoalService(uow)
        self._goals: List[GoalDto] = []
        self._person_filter: Optional[int] = None
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._person_filter = person_id if person_id > 0 else None
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._goals = self._goal_service.get_goals(person_id=self._person_filter)
        self.goalsChanged.emit()

    @Property(list, notify=goalsChanged)
    def goals(self) -> list:
        return [
            {
                "id": g.id,
                "name": g.name,
                "target": g.target_formatted,
                "current": g.current_formatted,
                "remaining": g.remaining_formatted,
                "progress": g.progress_percentage,
                "personName": g.person_name,
                "targetDate": g.target_date or "No date",
                "isAchieved": g.is_achieved,
                "notes": g.notes or "",
            }
            for g in self._goals
        ]

    @Slot(str, str, int, str, str, result=bool)
    def createGoal(
        self,
        name: str,
        target_amount_str: str,
        person_id: int,
        target_date_str: str,
        notes: str,
    ) -> bool:
        try:
            if not name.strip():
                self.operationError.emit("Goal name cannot be empty.")
                return False

            target_money = Money.from_str(target_amount_str)
            if target_money.paise <= 0:
                self.operationError.emit("Target amount must be greater than zero.")
                return False

            t_date = date.fromisoformat(target_date_str) if target_date_str else None

            self._goal_service.create_goal(
                name=name.strip(),
                target_amount=target_money,
                person_id=person_id,
                target_date=t_date,
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Savings goal '{name}' created successfully.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int, str, str, result=bool)
    def contribute(self, goal_id: int, amount_str: str, notes: str) -> bool:
        try:
            money = Money.from_str(amount_str)
            if money.paise <= 0:
                self.operationError.emit("Contribution amount must be greater than zero.")
                return False

            self._goal_service.contribute_to_goal(
                goal_id=goal_id,
                amount=money,
                date_=date.today(),
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Contributed {money.format()} toward savings goal.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False
