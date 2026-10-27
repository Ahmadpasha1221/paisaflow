"""PersonViewModel managing people profiles in household finance."""

from typing import List

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import PersonDto
from paisaflow.application.services import PersonService
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class PersonViewModel(QObject):
    peopleChanged = Signal()
    operationSuccess = Signal(str)
    operationError = Signal(str)

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._person_service = PersonService(uow)
        self._people: List[PersonDto] = []
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._people = self._person_service.get_people(include_inactive=False)
        self.peopleChanged.emit()

    @Property(list, notify=peopleChanged)
    def people(self) -> list:
        return [
            {
                "id": p.id,
                "name": p.name,
                "colorCode": p.color_code,
                "avatarPath": p.avatar_path or "",
                "isActive": p.is_active,
            }
            for p in self._people
        ]

    @Slot(str, str, result=bool)
    def createPerson(self, name: str, color_code: str = "#B8F28B") -> bool:
        try:
            if not name.strip():
                self.operationError.emit("Name cannot be empty.")
                return False

            self._person_service.create_person(
                name=name.strip(),
                color_code=color_code if color_code else "#B8F28B",
            )
            self.operationSuccess.emit(f"Person '{name}' added successfully.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int, str, str, result=bool)
    def updatePerson(self, person_id: int, name: str, color_code: str) -> bool:
        try:
            self._person_service.update_person(
                person_id=person_id,
                name=name.strip(),
                color_code=color_code,
            )
            self.operationSuccess.emit(f"Person '{name}' updated successfully.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False
