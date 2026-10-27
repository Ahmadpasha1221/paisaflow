"""Application bootstrap coordinating database initialization, ViewModels, and QML engine."""

import os
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from paisaflow.application.services import AccountService, PersonService
from paisaflow.domain.entities.account import AccountType
from paisaflow.domain.value_objects.money import Money
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from paisaflow.presentation.viewmodels.account_viewmodel import AccountViewModel
from paisaflow.presentation.viewmodels.app_viewmodel import AppViewModel
from paisaflow.presentation.viewmodels.budget_viewmodel import BudgetViewModel
from paisaflow.presentation.viewmodels.debt_viewmodel import DebtViewModel
from paisaflow.presentation.viewmodels.goal_viewmodel import GoalViewModel
from paisaflow.presentation.viewmodels.overview_viewmodel import OverviewViewModel
from paisaflow.presentation.viewmodels.person_viewmodel import PersonViewModel
from paisaflow.presentation.viewmodels.reports_viewmodel import ReportsViewModel
from paisaflow.presentation.viewmodels.settings_viewmodel import SettingsViewModel
from paisaflow.presentation.viewmodels.theme_engine import ThemeEngine
from paisaflow.presentation.viewmodels.transaction_viewmodel import TransactionViewModel


def ensure_initial_seed(uow: SqlAlchemyUnitOfWork) -> None:
    """Ensure at least one default person and account exist for a clean first launch."""
    person_svc = PersonService(uow)
    account_svc = AccountService(uow)

    people = person_svc.get_people()
    if not people:
        person = person_svc.create_person(name="Primary Account", color_code="#B8F28B")
        account_svc.create_account(
            name="Cash Wallet",
            account_type=AccountType.CASH,
            owner_person_id=person.id,
            opening_balance=Money(0),
            notes="Default cash wallet",
        )


def run_app() -> int:
    """Launch the PaisaFlow desktop application."""
    # Ensure High DPI scaling is enabled
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QGuiApplication(sys.argv)
    app.setApplicationName("PaisaFlow")
    app.setOrganizationName("PaisaFlow")

    # 1. Initialize Database & Migrations
    engine = create_db_engine()
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    uow = SqlAlchemyUnitOfWork(session_factory)

    # 2. Seed initial profile if brand new
    ensure_initial_seed(uow)

    # 3. Instantiate ViewModels
    theme_engine = ThemeEngine(uow)
    app_vm = AppViewModel(uow)
    overview_vm = OverviewViewModel(uow)
    transaction_vm = TransactionViewModel(uow)
    account_vm = AccountViewModel(uow)
    person_vm = PersonViewModel(uow)
    budget_vm = BudgetViewModel(uow)
    goal_vm = GoalViewModel(uow)
    debt_vm = DebtViewModel(uow)
    reports_vm = ReportsViewModel(uow)
    settings_vm = SettingsViewModel(uow, engine)

    # 4. Initialize QML Engine
    qml_engine = QQmlApplicationEngine()

    # Expose Context Properties
    context = qml_engine.rootContext()
    context.setContextProperty("themeEngine", theme_engine)
    context.setContextProperty("appVM", app_vm)
    context.setContextProperty("overviewVM", overview_vm)
    context.setContextProperty("transactionVM", transaction_vm)
    context.setContextProperty("accountVM", account_vm)
    context.setContextProperty("personVM", person_vm)
    context.setContextProperty("budgetVM", budget_vm)
    context.setContextProperty("goalVM", goal_vm)
    context.setContextProperty("debtVM", debt_vm)
    context.setContextProperty("reportsVM", reports_vm)
    context.setContextProperty("settingsVM", settings_vm)

    qml_path = Path(__file__).parent / "presentation" / "qml" / "App.qml"
    qml_engine.load(str(qml_path))

    if not qml_engine.rootObjects():
        print(f"Failed to load QML from {qml_path}", file=sys.stderr)
        return -1

    return app.exec()
