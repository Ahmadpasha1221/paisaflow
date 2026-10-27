"""AppViewModel providing global application state, navigation, and household context."""

from typing import List

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.services import PersonService
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class AppViewModel(QObject):
    activePageChanged = Signal()
    householdContextChanged = Signal()
    peopleListChanged = Signal()
    dataRefreshed = Signal()
    toastRequested = Signal(str, bool)  # message, is_error
    dialogRequested = Signal(str)  # dialog_type: 'transaction', 'account', 'person', etc.
    restoreRequested = Signal(str, str)  # backup path, backup display name
    transactionDeleteRequested = Signal(int, str)  # transaction id, description

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._person_service = PersonService(uow)

        self._active_page = "overview"
        self._selected_person_id = 0  # 0 represents Household (All)
        self._selected_person_name = "Household (All)"
        self._people_cache: List[dict] = []
        self.refreshPeople()

    @Property(str, notify=activePageChanged)
    def activePage(self) -> str:
        return self._active_page

    @Slot(str)
    def navigateTo(self, page_name: str) -> None:
        if self._active_page != page_name:
            self._active_page = page_name
            self.activePageChanged.emit()

    @Property(int, notify=householdContextChanged)
    def selectedPersonId(self) -> int:
        return self._selected_person_id

    @Property(str, notify=householdContextChanged)
    def selectedPersonName(self) -> str:
        return self._selected_person_name

    @Slot(int, str)
    def setHouseholdContext(self, person_id: int, person_name: str) -> None:
        if self._selected_person_id != person_id:
            self._selected_person_id = person_id
            self._selected_person_name = person_name
            self.householdContextChanged.emit()
            self.dataRefreshed.emit()

    @Property(list, notify=peopleListChanged)
    def people(self) -> list:
        return self._people_cache

    @Slot()
    def refreshPeople(self) -> None:
        dtos = self._person_service.get_people(include_inactive=False)
        self._people_cache = [{"id": p.id, "name": p.name, "colorCode": p.color_code} for p in dtos]
        # Ensure selected person name is up to date
        if self._selected_person_id == 0:
            self._selected_person_name = "Household (All)"
        else:
            match = next((p for p in dtos if p.id == self._selected_person_id), None)
            if match:
                self._selected_person_name = match.name
            else:
                self._selected_person_id = 0
                self._selected_person_name = "Household (All)"

        self.peopleListChanged.emit()

    @Slot(str)
    def openDialog(self, dialog_type: str) -> None:
        self.dialogRequested.emit(dialog_type)

    @Slot(str, str)
    def requestRestore(self, backup_path: str, backup_name: str) -> None:
        """Ask the shell to open the restore confirmation for a specific backup snapshot."""
        self.restoreRequested.emit(backup_path, backup_name)

    @Slot(int, str)
    def requestTransactionDelete(self, transaction_id: int, description: str) -> None:
        """Ask the shell to confirm deleting a transaction before it is voided."""
        self.transactionDeleteRequested.emit(transaction_id, description)

    @Slot(str, bool)
    def showToast(self, message: str, is_error: bool = False) -> None:
        self.toastRequested.emit(message, is_error)

    @Slot()
    def notifyDataChanged(self) -> None:
        """Triggered whenever any financial entity is added, updated, or voided."""
        self.refreshPeople()
        self.dataRefreshed.emit()
