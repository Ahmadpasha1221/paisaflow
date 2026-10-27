"""UI and QML integration tests verifying QML loading and component bindings."""

import os
from pathlib import Path

import pytest
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from paisaflow.bootstrap import ensure_initial_seed
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


@pytest.fixture(scope="session")
def qapp():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    app = QGuiApplication.instance()
    if not app:
        app = QGuiApplication([])
    return app


def test_qml_app_loads_cleanly(qapp, tmp_path: Path):
    db_file = tmp_path / "ui_test.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    session_factory = create_session_factory(engine)
    uow = SqlAlchemyUnitOfWork(session_factory)
    ensure_initial_seed(uow)

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

    qml_engine = QQmlApplicationEngine()
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

    qml_path = Path("src/paisaflow/presentation/qml/App.qml").resolve()
    assert qml_path.exists()

    qml_engine.load(str(qml_path))

    # Verify that rootObjects loaded without fatal errors
    root_objects = qml_engine.rootObjects()
    assert len(root_objects) > 0, "Failed to load App.qml root window"

    window = root_objects[0]
    assert window.property("title").startswith("PaisaFlow")


def test_theme_toggle_signal(tmp_path: Path):
    db_file = tmp_path / "theme_test.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))

    theme_engine = ThemeEngine(uow)
    assert theme_engine.isDark is True
    assert theme_engine.appBackground == "#17251F"

    # Toggle to light
    theme_engine.toggleTheme()
    assert theme_engine.isDark is False
    assert theme_engine.appBackground == "#F5F6F2"
    assert theme_engine.primaryAccent == "#426D35"

    # Toggle back to dark
    theme_engine.toggleTheme()
    assert theme_engine.isDark is True
    assert theme_engine.appBackground == "#17251F"


def test_app_viewmodel_navigation(tmp_path: Path):
    db_file = tmp_path / "nav_test.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))
    ensure_initial_seed(uow)

    app_vm = AppViewModel(uow)
    assert app_vm.activePage == "overview"

    app_vm.navigateTo("transactions")
    assert app_vm.activePage == "transactions"

    app_vm.navigateTo("budgets")
    assert app_vm.activePage == "budgets"
