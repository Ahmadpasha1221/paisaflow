"""Input component behavior and Flowline input-state regression tests."""

from pathlib import Path

import pytest
from PySide6.QtCore import QResource, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem, QQuickWindow
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from paisaflow.bootstrap import StartupState
from paisaflow.infrastructure.database.engine import create_db_engine, create_session_factory
from paisaflow.infrastructure.database.migrations import initialize_database
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from paisaflow.presentation.qml import resources_rc  # noqa: F401
from paisaflow.presentation.viewmodels.theme_engine import ThemeEngine


@pytest.fixture(scope="session")
def qapp():
    import os

    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication.instance() or QGuiApplication([])
    return app


def _load_input(tmp_path: Path):
    db_engine = create_db_engine(db_path=tmp_path / "inputs.db")
    initialize_database(db_engine)
    uow = SqlAlchemyUnitOfWork(create_session_factory(db_engine))
    theme_engine = ThemeEngine(uow)
    qml_engine = QQmlApplicationEngine()
    qml_engine.rootContext().setContextProperty("themeEngine", theme_engine)
    qml_engine.load(str(Path("tests/ui/InputHarness.qml").resolve()))
    assert qml_engine.rootObjects(), "Input harness failed to load"
    window = qml_engine.rootObjects()[0]
    window.setVisible(True)
    return qml_engine, window, theme_engine


def _walk(item: QQuickItem):
    yield item
    for child in item.childItems():
        yield from _walk(child)


def _item(window: QQuickWindow, name: str) -> QQuickItem:
    return next(item for item in _walk(window.contentItem()) if item.objectName() == name)


def test_text_input_padding_focus_editing_selection_and_theme(qapp, tmp_path: Path):
    qml_engine, window, theme_engine = _load_input(tmp_path)
    field = _item(window, "inputField")
    assert field.property("leftPadding") >= 10
    assert field.property("rightPadding") >= 10
    assert field.property("height") == pytest.approx(42)
    assert field.property("placeholderText") == "Enter a value"

    field.forceActiveFocus()
    QTest.qWait(50)
    assert field.hasActiveFocus()
    assert (field.activeFocusOnTab() if callable(field.activeFocusOnTab) else field.activeFocusOnTab) is True
    assert field.property("selectionColor").name().lower() == theme_engine.primaryAccent.lower()
    for key in (Qt.Key_P, Qt.Key_A, Qt.Key_I, Qt.Key_S, Qt.Key_A, Qt.Key_F, Qt.Key_L, Qt.Key_O, Qt.Key_W):
        QTest.keyClick(window, key)
    assert field.property("text") == "paisaflow"
    QTest.keyClick(window, Qt.Key_Left)
    QTest.keyClick(window, Qt.Key_Backspace)
    assert field.property("text") == "paisaflw"
    QTest.keyClick(window, Qt.Key_A, Qt.ControlModifier)
    assert field.property("selectedText") == "paisaflw"
    for key in (Qt.Key_I, Qt.Key_N, Qt.Key_P, Qt.Key_U, Qt.Key_T):
        QTest.keyClick(window, key)
    assert field.property("text") == "input"

    theme_engine.toggleTheme()
    assert field.property("color").name().lower() == theme_engine.primaryText.lower()
    field.setProperty("hasError", True)
    assert field.property("hasError") is True
    field.setProperty("hasError", False)
    field.setProperty("readOnly", True)
    assert field.property("readOnly") is True
    del qml_engine


def test_currency_date_search_and_multiline_controls_are_usable(qapp, tmp_path: Path):
    qml_engine, window, theme_engine = _load_input(tmp_path)
    currency = _item(window, "currencyField")
    date = _item(window, "dateField")
    search = _item(window, "searchField")
    multiline = _item(window, "notesField")

    assert currency.property("text") == "123.45"
    assert currency.property("readOnly") is False
    assert date.property("text") == "2026-10-28"
    assert search.property("placeholderText") == "Search"
    assert multiline.property("leftPadding") == 12

    currency_editor = next(
        item for item in _walk(currency)
        if item.metaObject().className().startswith("TextInputField")
    )
    currency_editor.forceActiveFocus()
    QTest.qWait(30)
    QTest.keyClick(window, Qt.Key_End)
    QTest.keyClick(window, Qt.Key_6)
    assert currency.property("text") == "123.456"

    multiline.forceActiveFocus()
    for key in (Qt.Key_L, Qt.Key_I, Qt.Key_N, Qt.Key_E, Qt.Key_Space, Qt.Key_O, Qt.Key_N, Qt.Key_E):
        QTest.keyClick(window, key)
    QTest.keyClick(window, Qt.Key_Return)
    for key in (Qt.Key_L, Qt.Key_I, Qt.Key_N, Qt.Key_E, Qt.Key_Space, Qt.Key_T, Qt.Key_W, Qt.Key_O):
        QTest.keyClick(window, key)
    assert multiline.property("text") == "line one\nline two"
    try:
        assert multiline.property("wrapMode") is not None
    except RuntimeError:
        prop = multiline.metaObject().property(multiline.metaObject().indexOfProperty("wrapMode"))
        assert prop.isValid()
    window.resize(420, 300)
    QTest.qWait(50)
    assert 0 < multiline.width() < 420
    del qml_engine


def test_brand_resource_and_startup_splash_failure_state(qapp):
    assert QResource(":/paisaflow/icons/brand.png").isValid()
    assert QResource(":/paisaflow/qml/App.qml").isValid()
    assert QResource(":/paisaflow/qml/Splash.qml").isValid()

    state = StartupState()
    splash_engine = QQmlApplicationEngine()
    context = splash_engine.rootContext()
    context.setContextProperty("startupState", state)
    context.setContextProperty("brandIconUrl", "qrc:/paisaflow/icons/brand.png")
    splash_engine.load("qrc:/paisaflow/qml/Splash.qml")
    assert splash_engine.rootObjects(), "The resource-backed startup splash failed to load"
    splash = splash_engine.rootObjects()[0]
    splash.setVisible(True)
    splash_image = next(item for item in _walk(splash.contentItem()) if item.objectName() == "brandImage")
    QTest.qWait(80)
    assert splash_image.property("status") == 1, "Brand image did not load from Qt resources"
    assert splash_image.property("source").toString() == "qrc:/paisaflow/icons/brand.png"

    state.fail("Database unavailable")
    QTest.qWait(30)
    assert state.errorMessage == "Database unavailable"
    error_label = next(item for item in _walk(splash.contentItem()) if item.objectName() == "startupError")
    assert error_label.property("visible") is True
    assert "Database unavailable" in error_label.property("text")
    close_button = next(item for item in _walk(splash.contentItem()) if item.property("text") == "Close")
    assert close_button.property("visible") is True

    splash.close()
    assert splash.property("visible") is False
    del splash_engine
