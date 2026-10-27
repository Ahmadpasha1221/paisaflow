"""TransactionViewModel managing transaction listing, search, filtering, and record entry."""

from datetime import date
from typing import List

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.application.dto import TransactionDto
from paisaflow.application.services import (
    AccountService,
    CategoryService,
    PersonService,
    TransactionService,
)
from paisaflow.domain.entities.category import CategoryType
from paisaflow.domain.entities.transaction import (
    PaymentMethod,
    TransactionStatus,
    TransactionType,
)
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class TransactionViewModel(QObject):
    transactionsChanged = Signal()
    dataChanged = Signal()  # any ledger mutation; the shell refreshes every other view model
    operationSuccess = Signal(str)
    operationError = Signal(str)

    ACTIVE_MODE = "active"
    HISTORY_MODE = "history"

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        self._txn_service = TransactionService(uow)
        self._account_service = AccountService(uow)
        self._category_service = CategoryService(uow)
        self._person_service = PersonService(uow)

        self._transactions: List[TransactionDto] = []
        self._total_count: int = 0
        self._active_count: int = 0
        self._history_count: int = 0
        self._view_mode: str = self.ACTIVE_MODE
        self._current_page: int = 0
        self._page_size: int = 25
        self._search_text: str = ""
        self._type_filter: str = "all"
        self._person_filter: int = 0
        self._category_filter: int = 0
        self._account_filter: int = 0

        self.refresh()

    def _filter_kwargs(self) -> dict:
        """Shared filters for the tab counters and the paged query."""
        txn_type = None
        if self._type_filter != "all":
            try:
                txn_type = TransactionType(self._type_filter)
            except ValueError:
                pass

        return {
            "person_id": self._person_filter if self._person_filter > 0 else None,
            "category_id": self._category_filter if self._category_filter > 0 else None,
            "account_id": self._account_filter if self._account_filter > 0 else None,
            "txn_type": txn_type,
            "search_text": self._search_text,
        }

    @Slot()
    def refresh(self) -> None:
        filters = self._filter_kwargs()

        # Counters for both ledger tabs come from the same filters, so the tabs always
        # agree with what the list underneath them shows.
        _, self._active_count = self._txn_service.query_transactions(
            **filters, include_voided=False, limit=1, offset=0
        )
        _, self._history_count = self._txn_service.query_transactions(
            **filters, status=TransactionStatus.VOIDED, limit=1, offset=0
        )
        self._total_count = (
            self._history_count if self._view_mode == self.HISTORY_MODE else self._active_count
        )

        # Deleting the only record on the last page must not leave an empty page behind.
        self._current_page = max(0, min(self._current_page, max(0, self.totalPages - 1)))

        self._transactions, _ = self._txn_service.query_transactions(
            **filters,
            status=TransactionStatus.VOIDED if self._view_mode == self.HISTORY_MODE else None,
            include_voided=self._view_mode == self.HISTORY_MODE,
            limit=self._page_size,
            offset=self._current_page * self._page_size,
        )
        self.transactionsChanged.emit()

    @Property(list, notify=transactionsChanged)
    def transactions(self) -> list:
        return [
            {
                "id": t.id,
                "referenceNo": t.reference_no,
                "date": t.transaction_date,
                "time": t.transaction_time,
                "type": t.transaction_type,
                "typeDisplay": t.transaction_type_display,
                "description": t.description,
                "amount": t.amount_formatted,
                "amountPaise": t.amount_paise,
                "personId": t.person_id,
                "personName": t.person_name,
                "categoryId": t.category_id or 0,
                "categoryName": t.category_name,
                "paymentMethod": t.payment_method_display,
                "status": t.status,
                "affectedAccounts": t.affected_accounts,
                "notes": t.notes or "",
                "createdAt": t.created_at,
                "updatedAt": t.updated_at,
                "voidedAt": t.voided_at,
            }
            for t in self._transactions
        ]

    @Property(int, notify=transactionsChanged)
    def totalCount(self) -> int:
        return self._total_count

    @Property(int, notify=transactionsChanged)
    def activeCount(self) -> int:
        return self._active_count

    @Property(int, notify=transactionsChanged)
    def historyCount(self) -> int:
        return self._history_count

    @Property(str, notify=transactionsChanged)
    def viewMode(self) -> str:
        return self._view_mode

    @Slot(str)
    def setViewMode(self, mode: str) -> None:
        """Switch the ledger between live records ('active') and deleted ones ('history')."""
        normalized = self.HISTORY_MODE if mode.lower() == self.HISTORY_MODE else self.ACTIVE_MODE
        if normalized != self._view_mode:
            self._view_mode = normalized
            self._current_page = 0
            self.refresh()

    @Property(int, notify=transactionsChanged)
    def currentPage(self) -> int:
        return self._current_page

    @Property(int, notify=transactionsChanged)
    def totalPages(self) -> int:
        if self._total_count == 0:
            return 1
        return (self._total_count + self._page_size - 1) // self._page_size

    @Slot(int)
    def setPage(self, page_index: int) -> None:
        max_page = max(0, self.totalPages - 1)
        clamped = max(0, min(page_index, max_page))
        if self._current_page != clamped:
            self._current_page = clamped
            self.refresh()

    @Slot(str)
    def setSearchText(self, text: str) -> None:
        self._search_text = text.strip()
        self._current_page = 0
        self.refresh()

    @Slot(str)
    def setTypeFilter(self, filter_type: str) -> None:
        self._type_filter = filter_type.lower()
        self._current_page = 0
        self.refresh()

    @Slot(int)
    def setPersonFilter(self, person_id: int) -> None:
        self._person_filter = person_id
        self._current_page = 0
        self.refresh()

    @Slot(int)
    def setAccountFilter(self, account_id: int) -> None:
        self._account_filter = account_id
        self._current_page = 0
        self.refresh()

    @Slot(int)
    def setCategoryFilter(self, category_id: int) -> None:
        self._category_filter = category_id
        self._current_page = 0
        self.refresh()

    # Form Option Feeds
    @Property(list, notify=transactionsChanged)
    def accountOptions(self) -> list:
        accts = self._account_service.get_accounts(include_archived=False)
        return [{"id": a.id, "name": f"{a.name} ({a.balance_formatted})"} for a in accts]

    @Property(list, notify=transactionsChanged)
    def incomeCategoryOptions(self) -> list:
        cats = self._category_service.get_categories(category_type=CategoryType.INCOME)
        return [{"id": c.id, "name": c.name} for c in cats]

    @Property(list, notify=transactionsChanged)
    def expenseCategoryOptions(self) -> list:
        cats = self._category_service.get_categories(category_type=CategoryType.EXPENSE)
        return [{"id": c.id, "name": c.name} for c in cats]

    # Transaction Actions
    @Slot(str, str, str, int, int, int, str, str, result=bool)
    def addIncome(
        self,
        date_str: str,
        description: str,
        amount_str: str,
        account_id: int,
        person_id: int,
        category_id: int,
        payment_method: str,
        notes: str,
    ) -> bool:
        try:
            money = Money.from_str(amount_str)
            if money.paise <= 0:
                self.operationError.emit("Amount must be greater than zero.")
                return False
            txn_date = date.fromisoformat(date_str) if date_str else date.today()
            method = PaymentMethod(payment_method.lower()) if payment_method else PaymentMethod.UPI

            self._txn_service.record_income(
                transaction_date=txn_date,
                description=description,
                amount=money,
                account_id=account_id,
                person_id=person_id,
                category_id=category_id,
                payment_method=method,
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Recorded income of {money.format()}.")
            self.refresh()
            self.dataChanged.emit()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(str, str, str, int, int, int, str, str, result=bool)
    def addExpense(
        self,
        date_str: str,
        description: str,
        amount_str: str,
        account_id: int,
        person_id: int,
        category_id: int,
        payment_method: str,
        notes: str,
    ) -> bool:
        try:
            money = Money.from_str(amount_str)
            if money.paise <= 0:
                self.operationError.emit("Amount must be greater than zero.")
                return False
            txn_date = date.fromisoformat(date_str) if date_str else date.today()
            method = PaymentMethod(payment_method.lower()) if payment_method else PaymentMethod.UPI

            self._txn_service.record_expense(
                transaction_date=txn_date,
                description=description,
                amount=money,
                account_id=account_id,
                person_id=person_id,
                category_id=category_id,
                payment_method=method,
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Recorded expense of {money.format()}.")
            self.refresh()
            self.dataChanged.emit()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(str, str, str, int, int, int, str, str, result=bool)
    def addTransfer(
        self,
        date_str: str,
        description: str,
        amount_str: str,
        source_account_id: int,
        dest_account_id: int,
        person_id: int,
        payment_method: str,
        notes: str,
    ) -> bool:
        try:
            money = Money.from_str(amount_str)
            if money.paise <= 0:
                self.operationError.emit("Amount must be greater than zero.")
                return False
            if source_account_id == dest_account_id:
                self.operationError.emit("Source and destination accounts must be different.")
                return False

            txn_date = date.fromisoformat(date_str) if date_str else date.today()
            method = (
                PaymentMethod(payment_method.lower())
                if payment_method
                else PaymentMethod.BANK_TRANSFER
            )

            self._txn_service.record_transfer(
                transaction_date=txn_date,
                description=description,
                amount=money,
                source_account_id=source_account_id,
                dest_account_id=dest_account_id,
                person_id=person_id,
                payment_method=method,
                notes=notes if notes else None,
            )
            self.operationSuccess.emit(f"Transferred {money.format()} between accounts.")
            self.refresh()
            self.dataChanged.emit()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False

    @Slot(int, result=bool)
    def voidTransaction(self, transaction_id: int) -> bool:
        """Delete a transaction by voiding it: it leaves the ledger and moves to History."""
        try:
            self._txn_service.void_transaction(transaction_id)
            self.operationSuccess.emit("Transaction deleted and moved to History.")
            self.refresh()
            self.dataChanged.emit()
            return True
        except Exception as e:
            self.operationError.emit(str(e))
            return False
