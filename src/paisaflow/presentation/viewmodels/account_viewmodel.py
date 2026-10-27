"""AccountViewModel managing account listing, creation, and archiving."""

from datetime import date
from typing import List, Optional

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import AccountDto
from paisaflow.application.services import AccountService, PersonService
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class AccountViewModel(QObject):
    accountsChanged = Signal()
    operationSuccess = Signal(str)
    operationError = Signal(str)

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._account_service = AccountService(uow)
        self._person_service = PersonService(uow)
        self._accounts: List[AccountDto] = []
        self._person_filter: Optional[int] = None
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._person_filter = person_id if person_id > 0 else None
        self.refresh()

    @Slot()
    def refresh(self) -> None:
        self._accounts = self._account_service.get_accounts(
            include_archived=False, person_id=self._person_filter
        )
        self.accountsChanged.emit()

    @Property(list, notify=accountsChanged)
    def accounts(self) -> list:
        return [
            {
                "id": a.id,
                "name": a.name,
                "accountType": a.account_type,
                "accountTypeDisplay": a.account_type_display,
                "ownerPersonId": a.owner_person_id,
                "ownerName": a.owner_name,
                "balance": a.balance_formatted,
                "balancePaise": a.balance_paise,
                "openingBalance": a.opening_balance_formatted,
                "isLiability": a.is_liability,
                "isArchived": a.is_archived,
                "notes": a.notes or "",
            }
            for a in self._accounts
        ]

    @Property(int, notify=accountsChanged)
    def totalAssetsCount(self) -> int:
        return sum(1 for a in self._accounts if not a.is_liability)

    @Property(int, notify=accountsChanged)
    def totalLiabilitiesCount(self) -> int:
        return sum(1 for a in self._accounts if a.is_liability)

    @Slot(str, str, int, str, str)
    def createAccount(
        self,
        name: str,
        account_type_str: str,
        owner_person_id: int,
        opening_balance_str: str,
        notes: str,
    ) -> bool:
        try:
            if not name.strip():
                self.operationError.emit("Account name cannot be empty.")
                return False

            acct_type = AccountType(account_type_str.lower())
            opening_bal = (
                Money.from_str(opening_balance_str) if opening_balance_str else Money.zero()
            )

            self._account_service.create_account(
                name=name,
                account_type=acct_type,
                owner_person_id=owner_person_id,
                opening_balance=opening_bal,
                opening_date=date.today(),
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Account '{name}' created successfully.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int)
    def archiveAccount(self, account_id: int) -> bool:
        try:
            self._account_service.archive_account(account_id)
            self.operationSuccess.emit("Account archived successfully.")
            self.refresh()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False
