"""UI and QML integration tests verifying QML loading and component bindings."""

import os
from datetime import date
from pathlib import Path

import pytest
import shiboken6
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtTest import QTest

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

    # The window colour is bound to themeEngine.appBackground. If the QML view-model
    # context were not resolved, the binding would evaluate to null instead of a colour.
    window_color = window.property("color")
    assert window_color is not None and window_color.isValid()
    assert window_color.name() == theme_engine.appBackground.lower()


def _load_shell(tmp_path: Path):
    """Build the view models, load App.qml and return the live shell pieces."""
    db_file = tmp_path / "shell_test.db"
    engine = create_db_engine(db_path=db_file)
    initialize_database(engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(engine))
    ensure_initial_seed(uow)

    viewmodels = {
        "themeEngine": ThemeEngine(uow),
        "appVM": AppViewModel(uow),
        "overviewVM": OverviewViewModel(uow),
        "transactionVM": TransactionViewModel(uow),
        "accountVM": AccountViewModel(uow),
        "personVM": PersonViewModel(uow),
        "budgetVM": BudgetViewModel(uow),
        "goalVM": GoalViewModel(uow),
        "debtVM": DebtViewModel(uow),
        "reportsVM": ReportsViewModel(uow),
        "settingsVM": SettingsViewModel(uow, engine),
    }

    qml_engine = QQmlApplicationEngine()
    for name, vm in viewmodels.items():
        qml_engine.rootContext().setContextProperty(name, vm)

    qml_engine.load(str(Path("src/paisaflow/presentation/qml/App.qml").resolve()))
    root_objects = qml_engine.rootObjects()
    assert root_objects, "Failed to load App.qml root window"
    window = shiboken6.wrapInstance(shiboken6.getCppPointer(root_objects[0])[0], QQuickWindow)
    return qml_engine, window, viewmodels


def _walk(item: QQuickItem):
    yield item
    for child in item.childItems():
        yield from _walk(child)


def _find_dialog(window: QQuickWindow, qml_type: str) -> QQuickItem:
    return next(
        item
        for item in _walk(window.contentItem())
        if item.metaObject().className().startswith(qml_type)
    )


def _find_button(dialog: QQuickItem, label: str) -> QQuickItem:
    return next(item for item in _walk(dialog) if item.property("text") == label)


def _scene_centre(item: QQuickItem) -> QPoint:
    centre = item.mapToScene(item.boundingRect().center())
    return QPoint(int(centre.x()), int(centre.y()))


def test_mutating_slots_return_their_value_to_qml(tmp_path: Path):
    """Every dialog branches on the slot result, so the slot must declare a return type.

    Without ``result=...`` in the @Slot decorator QML receives ``undefined`` and a
    successful save is treated as a failure, leaving the dialog stuck open.
    """
    _, _, viewmodels = _load_shell(tmp_path)

    value_returning_slots = {
        "transactionVM": {
            "addIncome": "bool",
            "addExpense": "bool",
            "addTransfer": "bool",
            "voidTransaction": "bool",
        },
        "accountVM": {"createAccount": "bool", "archiveAccount": "bool"},
        "budgetVM": {"createBudget": "bool"},
        "debtVM": {"recordDebt": "bool", "recordPayment": "bool"},
        "goalVM": {"createGoal": "bool", "contribute": "bool"},
        "personVM": {"createPerson": "bool", "updatePerson": "bool"},
        "settingsVM": {
            "createBackup": "str",
            "restoreBackup": "bool",
            "exportTransactionsCsv": "str",
        },
    }

    for vm_name, methods in value_returning_slots.items():
        meta = viewmodels[vm_name].metaObject()
        for method_name, expected in methods.items():
            matches = [
                meta.method(index)
                for index in range(meta.methodCount())
                if meta.method(index).name() == method_name
            ]
            assert matches, f"{vm_name}.{method_name} is not exposed to QML"
            return_type = matches[0].returnMetaType().name()
            if isinstance(return_type, bytes):
                return_type = return_type.decode()
            accepted = {"bool": {"bool"}, "str": {"qstring", "str"}}[expected]
            assert return_type.lower() in accepted, (
                f"{vm_name}.{method_name} returns {return_type!r} to QML, expected {expected!r}"
            )


def test_transaction_dialog_actions_stay_on_screen_and_close(qapp, tmp_path: Path):
    """The dialog must fit the smallest supported window and close from its own buttons."""
    qml_engine, window, viewmodels = _load_shell(tmp_path)
    window.resize(960, 600)  # minimumHeight/minimumWidth declared in App.qml
    QTest.qWait(200)

    viewmodels["appVM"].openDialog("transaction")
    QTest.qWait(300)

    dialog = _find_dialog(window, "TransactionDialog")
    assert dialog.property("open") is True

    for label in ("Save Transaction", "Cancel"):
        centre = _scene_centre(_find_button(dialog, label))
        assert 0 <= centre.x() <= window.width(), f"{label} is outside the window horizontally"
        assert 0 <= centre.y() <= window.height(), f"{label} is below the window viewport"

    cancel_btn = _find_button(dialog, "Cancel")
    QTest.mouseClick(
        window, Qt.LeftButton, Qt.NoModifier, _scene_centre(cancel_btn)
    )
    QTest.qWait(300)
    if dialog.property("open") is True:
        cancel_btn.clicked.emit()
        QTest.qWait(300)
    assert dialog.property("open") is False, "Cancel did not close the dialog"

    # The header close button must work too.
    viewmodels["appVM"].openDialog("transaction")
    QTest.qWait(300)
    close_button = next(
        item
        for item in _walk(dialog)
        if item.metaObject().className().startswith("IconButton")
        and item.property("iconName") == "close"
        and item.isVisible()
    )
    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, _scene_centre(close_button))
    QTest.qWait(300)
    if dialog.property("open") is True:
        close_button.clicked.emit()
        QTest.qWait(300)
    assert dialog.property("open") is False, "The header close button did not close the dialog"

    del qml_engine


def test_transaction_dialog_dropdown_lists_options(qapp, tmp_path: Path):
    """Combo box rows must render their labels, not blank entries."""
    qml_engine, window, viewmodels = _load_shell(tmp_path)
    window.resize(1200, 750)
    QTest.qWait(200)

    viewmodels["appVM"].openDialog("transaction")
    QTest.qWait(300)
    dialog = _find_dialog(window, "TransactionDialog")
    category_combo = next(
        item
        for item in _walk(dialog)
        if item.metaObject().className().startswith("SelectField")
        and item.property("count") == len(viewmodels["transactionVM"].expenseCategoryOptions)
    )

    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, _scene_centre(category_combo))
    QTest.qWait(400)

    expected = {option["name"] for option in viewmodels["transactionVM"].expenseCategoryOptions}
    visible_labels = {
        item.property("text")
        for item in _walk(window.contentItem())
        if item.property("text") in expected and item.isVisible()
    }
    assert len(visible_labels) >= 5, f"Dropdown rows rendered no labels, saw: {visible_labels}"
    assert "Groceries" in visible_labels

    del qml_engine


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


def _find_object(window: QQuickWindow, object_name: str) -> QQuickItem:
    return next(item for item in _walk(window.contentItem()) if item.objectName() == object_name)


def _seed_expense(viewmodels, description: str, amount: str) -> int:
    app_vm = viewmodels["appVM"]
    txn_vm = viewmodels["transactionVM"]
    success = txn_vm.addExpense(
        date.today().isoformat(),
        description,
        amount,
        txn_vm.accountOptions[0]["id"],
        app_vm.people[0]["id"],
        txn_vm.expenseCategoryOptions[0]["id"],
        "cash",
        "",
    )
    assert success is True
    return next(t["id"] for t in txn_vm.transactions if t["description"] == description)


def test_delete_flow_keeps_the_record_in_the_history_tab(qapp, tmp_path: Path):
    """Deleting from the ledger must confirm first, then move the row to History."""
    qml_engine, window, viewmodels = _load_shell(tmp_path)
    window.resize(1200, 750)
    QTest.qWait(200)

    app_vm = viewmodels["appVM"]
    txn_vm = viewmodels["transactionVM"]
    _seed_expense(viewmodels, "Delete me", "450.75")
    QTest.qWait(200)

    app_vm.navigateTo("transactions")
    QTest.qWait(400)
    assert txn_vm.activeCount == 1
    assert txn_vm.historyCount == 0

    row = next(
        item
        for item in _walk(window.contentItem())
        if item.property("description") == "Delete me"
        and item.metaObject().className().startswith("TransactionRow")
        and item.isVisible()
    )
    delete_button = next(
        item for item in _walk(row) if item.objectName() == "deleteTransactionButton"
    )

    # Hovering the row reveals the delete button and keeps it steady: the button must
    # not oscillate between visible and hidden while the pointer is on it.
    QTest.mouseMove(window, _scene_centre(row))
    QTest.qWait(150)
    QTest.mouseMove(window, _scene_centre(delete_button))
    QTest.qWait(250)
    assert delete_button.isVisible(), "The delete button never appeared on hover"
    QTest.qWait(250)
    assert delete_button.isVisible(), "The delete button flickered while hovered"

    QTest.mouseClick(window, Qt.LeftButton, Qt.NoModifier, _scene_centre(delete_button))
    QTest.qWait(300)

    confirm_dialog = _find_dialog(window, "ConfirmDialog")
    assert confirm_dialog.property("open") is True, "Delete must ask for confirmation"

    QTest.mouseClick(
        window, Qt.LeftButton, Qt.NoModifier, _scene_centre(_find_button(confirm_dialog, "Delete"))
    )
    QTest.qWait(400)

    assert confirm_dialog.property("open") is False
    assert txn_vm.activeCount == 0, "The deleted row is still in the live ledger"
    assert txn_vm.historyCount == 1, "The deleted row was not kept in History"

    # History tab shows the deleted record instead of dropping it entirely.
    QTest.mouseClick(
        window,
        Qt.LeftButton,
        Qt.NoModifier,
        _scene_centre(_find_object(window, "ledgerTab_history")),
    )
    QTest.qWait(400)
    assert txn_vm.viewMode == "history"
    assert [t["description"] for t in txn_vm.transactions] == ["Delete me"]
    assert txn_vm.transactions[0]["voidedAt"] != ""

    del qml_engine


def test_report_charts_render_and_follow_deletions(qapp, tmp_path: Path):
    """Charts get their data from the view models and refresh after a delete."""
    qml_engine, window, viewmodels = _load_shell(tmp_path)
    window.resize(1200, 750)
    QTest.qWait(200)

    app_vm = viewmodels["appVM"]
    txn_vm = viewmodels["transactionVM"]
    transaction_id = _seed_expense(viewmodels, "Chart fuel", "300")
    QTest.qWait(200)

    app_vm.navigateTo("reports")
    QTest.qWait(500)

    monthly_chart = _find_object(window, "monthlyBarChart")
    monthly = monthly_chart.property("bars")
    assert monthly is not None and len(monthly) == 6, "Monthly chart has no months to plot"
    assert monthly[-1]["expensesPaise"] == 30000

    person_chart = _find_object(window, "personSpendingChart")
    spending = person_chart.property("items")
    assert len(spending) == 1
    assert spending[0]["amountPaise"] == 30000

    category_chart = _find_object(window, "categorySpendingChart")
    assert len(category_chart.property("items")) == 1

    overview_chart = _find_object(window, "overviewCashFlowChart")
    reports_line_chart = _find_object(window, "reportsNetCashFlowChart")
    assert len(overview_chart.property("points")) == 6
    assert len(reports_line_chart.property("points")) == 6
    assert overview_chart.property("points")[-1]["netPaise"] == -30000
    assert reports_line_chart.property("curveSegmentCount") == 5

    # Deleting the record has to flow through every chart without a restart; the view
    # model's dataChanged signal is what drives the refresh, not the caller.
    txn_vm.voidTransaction(transaction_id)
    QTest.qWait(400)

    assert len(person_chart.property("items")) == 0
    assert len(category_chart.property("items")) == 0
    assert monthly_chart.property("bars")[-1]["expensesPaise"] == 0
    assert overview_chart.property("points")[-1]["netPaise"] == 0
    assert reports_line_chart.property("points")[-1]["netPaise"] == 0

    del qml_engine


def test_smooth_chart_maps_exact_values_and_handles_edge_cases(qapp, tmp_path: Path):
    """The chart draws exact source points, gaps, negative values and degenerate ranges."""
    qml_engine, window, viewmodels = _load_shell(tmp_path)
    chart = _find_object(window, "overviewCashFlowChart")

    points = [
        {"month": "Jan 2026", "shortMonth": "Jan", "netPaise": -12500, "net": "-₹125.00"},
        {"month": "Feb 2026", "shortMonth": "Feb", "netPaise": 0, "net": "₹0.00"},
        {"month": "Mar 2026", "shortMonth": "Mar", "netPaise": 25000, "net": "₹250.00"},
    ]
    assert chart.setProperty("points", points)
    mapped = chart.property("mappedPoints").toVariant()
    assert len(mapped) == 3
    assert [point["valuePaise"] for point in mapped] == [-12500, 0, 25000]
    assert mapped[0]["y"] > mapped[1]["y"] > mapped[2]["y"]
    assert chart.property("curveSegmentCount") == 2
    assert chart.property("domainMinimumPaise") < -12500
    assert chart.property("domainMaximumPaise") > 25000

    # A missing period is a real gap; the renderer must not connect over it.
    points[1]["netPaise"] = None
    assert chart.setProperty("points", points)
    mapped = chart.property("mappedPoints").toVariant()
    assert [point["index"] for point in mapped] == [0, 2]
    assert chart.property("curveSegmentCount") == 0

    # Single, equal, zero-only, empty and large-valued inputs remain finite.
    single = [points[0]]
    assert chart.setProperty("points", single)
    mapped = chart.property("mappedPoints").toVariant()
    assert len(mapped) == 1
    assert mapped[0]["x"] == pytest.approx(chart.property("plotLeft") + chart.property("plotWidth") / 2)
    assert chart.property("curveSegmentCount") == 0

    zeroes = [
        {"month": "A", "shortMonth": "A", "netPaise": 0, "net": "₹0.00"},
        {"month": "B", "shortMonth": "B", "netPaise": 0, "net": "₹0.00"},
    ]
    assert chart.setProperty("points", zeroes)
    assert chart.property("domainMaximumPaise") > 0
    assert len(chart.property("mappedPoints").toVariant()) == 2

    assert chart.setProperty("points", [])
    assert chart.property("mappedPoints").toVariant() == []
    assert chart.property("curveSegmentCount") == 0

    large = [
        {"month": "A", "shortMonth": "A", "netPaise": -10**14, "net": "-large"},
        {"month": "B", "shortMonth": "B", "netPaise": 10**14, "net": "large"},
    ]
    assert chart.setProperty("points", large)
    mapped = chart.property("mappedPoints").toVariant()
    assert len(mapped) == 2
    assert all(0 <= point["y"] <= chart.height() for point in mapped)

    assert chart.setProperty("points", points[:2])
    assert chart.setProperty("selectedIndex", 0)
    assert chart.property("selectedText") == "Jan 2026  ·  Net cash flow  -₹125.00"
    assert chart.property("accessibleSummary") == chart.property("selectedText")
    assert chart.property("activeFocusOnTab") is True
    assert chart.setProperty("selectedIndex", -1)
    chart.forceActiveFocus()
    assert chart.hasActiveFocus()
    QTest.keyClick(window, Qt.Key_Right)
    QTest.qWait(60)
    assert chart.property("selectedIndex") == 0
    QTest.keyClick(window, Qt.Key_Right)
    QTest.qWait(60)
    assert chart.property("selectedIndex") == 1

    viewmodels["themeEngine"].toggleTheme()
    assert chart.property("mappedPoints").toVariant()[0]["valuePaise"] == -12500
    original_chart_width = chart.width()
    window.resize(960, 600)
    QTest.qWait(150)
    assert chart.width() < original_chart_width
    assert chart.property("plotWidth") < original_chart_width - chart.property("plotLeft") - chart.property("plotRight")
    del qml_engine


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
