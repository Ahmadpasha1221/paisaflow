"""Application bootstrap coordinating database initialization, ViewModels, and QML engine."""

import logging
import os
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from paisaflow.application.services import AccountService, PersonService
from paisaflow.config.settings import settings
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
from paisaflow.presentation.qml import resources_rc  # noqa: F401

# The UI restyles every Qt Quick Control (buttons, combo boxes, popups). The native "Windows"
# style silently ignores those customizations, which leaves dropdown lists empty and controls
# unstyled, so pin the fully themeable Basic style before any QML imports Qt Quick Controls.
QQuickStyle.setStyle("Basic")


def setup_logging() -> logging.Logger:
    """Configure file and console logging to user data directory."""
    logger = logging.getLogger("paisaflow")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        log_format = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        try:
            settings.log_dir.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(settings.log_file, encoding="utf-8")
            file_handler.setFormatter(log_format)
            file_handler.setLevel(logging.INFO)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to initialize file logger: {e}", file=sys.stderr)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)
    return logger


class StartupState(QObject):
    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._message = "Preparing your workspace"
        self._error_message = ""

    @Property(str, notify=changed)
    def message(self) -> str:
        return self._message

    @Property(str, notify=changed)
    def errorMessage(self) -> str:
        return self._error_message

    @Slot(str)
    def fail(self, message: str) -> None:
        self._error_message = message
        self.changed.emit()


def _application_asset(relative_path: str) -> Path:
    """Resolve a bundled asset in development and PyInstaller one-folder/one-file builds."""
    candidates = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass) / "assets" / relative_path)
    exe_dir = Path(sys.executable).parent
    candidates.append(exe_dir / "assets" / relative_path)
    candidates.append(exe_dir / "_internal" / "assets" / relative_path)
    repo_root = Path(__file__).resolve().parents[2]
    candidates.append(repo_root / "assets" / relative_path)
    for path in candidates:
        if path.exists():
            return path
    return repo_root / "assets" / relative_path


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
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"PaisaFlow {settings.version}")
        return 0

    # Ensure High DPI scaling is enabled
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # Set explicit AppUserModelID on Windows so the taskbar groups and shows the app icon
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "PaisaFlow.Flowline.Desktop.0.1.0"
            )
        except Exception:
            pass

    logger = setup_logging()
    logger.info("Initializing PaisaFlow v%s", settings.version)

    app = QGuiApplication(sys.argv)
    app.setApplicationName("PaisaFlow")
    app.setOrganizationName("PaisaFlow")
    QQuickStyle.setStyle("Basic")

    # Load high-resolution icon (ICO on Windows has multi-res frames, PNG on others)
    app_icon = QIcon()
    if sys.platform == "win32":
        ico_path = _application_asset("icons/brand.ico")
        if ico_path.exists():
            app_icon = QIcon(str(ico_path))
    if app_icon.isNull():
        app_icon = QIcon(":/paisaflow/icons/brand.png")
    if app_icon.isNull():
        app_icon = QIcon(str(_application_asset("icons/brand.png")))
    app.setWindowIcon(app_icon)

    # Show the QML splash before database and view-model initialization begins.
    startup_state = StartupState()
    splash_engine = QQmlApplicationEngine()
    splash_context = splash_engine.rootContext()
    splash_context.setContextProperty("startupState", startup_state)
    splash_context.setContextProperty("brandIconUrl", "qrc:/paisaflow/icons/brand.png")
    splash_path = Path(__file__).parent / "presentation" / "qml" / "Splash.qml"
    splash_engine.load("qrc:/paisaflow/qml/Splash.qml")
    if not splash_engine.rootObjects():
        logger.error("Failed to load splash screen from %s", splash_path)
        return -1

    splash_window = splash_engine.rootObjects()[0]
    splash_window.setIcon(app_icon)

    # Process initial paint before synchronous SQLite setup; no artificial delay is used.
    app.processEvents()

    try:
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
        qml_engine.load("qrc:/paisaflow/qml/App.qml")

        if not qml_engine.rootObjects():
            raise RuntimeError(f"Failed to load QML from {qml_path}")

        app_window = qml_engine.rootObjects()[0]
        app_window.setVisible(False)
        app_window.setIcon(app_icon)
        splash_window = splash_engine.rootObjects()[0]
        splash_window.close()
        app_window.setVisible(True)

        exit_code = app.exec()

        # Tear QML down while context objects are still referenced.
        del qml_engine
        del splash_engine
        return exit_code
    except Exception as exc:
        message = f"{exc}\n\nSee the application log for details: {settings.log_file}"
        startup_state.fail(message)
        logger.exception("PaisaFlow startup failed: %s", exc)
        print(f"PaisaFlow startup failed: {exc}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        app.exec()
        return -1
