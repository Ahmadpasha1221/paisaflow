"""Theme engine exposing Flowline design system tokens to QML with dynamic switching."""

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork


class ThemeEngine(QObject):
    themeChanged = Signal()

    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        super().__init__()
        self._uow = uow
        # Read saved theme preference
        with self._uow as u:
            saved_theme = u.settings.get("theme", "dark")
        self._is_dark = saved_theme == "dark"

    @Property(bool, notify=themeChanged)
    def isDark(self) -> bool:
        return self._is_dark

    @Slot()
    def reloadTheme(self) -> None:
        """Re-read the persisted theme preference (e.g. after a database restore)."""
        with self._uow as u:
            saved_theme = u.settings.get("theme", "dark")
        restored_is_dark = saved_theme == "dark"
        if self._is_dark != restored_is_dark:
            self._is_dark = restored_is_dark
            self.themeChanged.emit()

    @Slot()
    def toggleTheme(self) -> None:
        self.setTheme("light" if self._is_dark else "dark")

    @Slot(str)
    def setTheme(self, theme_name: str) -> None:
        new_is_dark = theme_name.lower() == "dark"
        if self._is_dark != new_is_dark:
            self._is_dark = new_is_dark
            with self._uow as u:
                u.settings.set("theme", "dark" if self._is_dark else "light")
                u.commit()
            self.themeChanged.emit()

    # Flowline Color Tokens
    @Property(str, notify=themeChanged)
    def appBackground(self) -> str:
        return "#17251F" if self._is_dark else "#F5F6F2"

    @Property(str, notify=themeChanged)
    def sidebarBackground(self) -> str:
        return "#1D2C23" if self._is_dark else "#EDF1EA"

    @Property(str, notify=themeChanged)
    def primarySurface(self) -> str:
        return "#26382F" if self._is_dark else "#FFFFFF"

    @Property(str, notify=themeChanged)
    def secondarySurface(self) -> str:
        return "#1D2C23" if self._is_dark else "#EDF1EA"

    @Property(str, notify=themeChanged)
    def elevatedSurface(self) -> str:
        return "#30473A" if self._is_dark else "#FFFFFF"

    @Property(str, notify=themeChanged)
    def primaryText(self) -> str:
        return "#F5F6F2" if self._is_dark else "#17251F"

    @Property(str, notify=themeChanged)
    def secondaryText(self) -> str:
        return "#B8C6BC" if self._is_dark else "#536258"

    @Property(str, notify=themeChanged)
    def primaryAccent(self) -> str:
        return "#B8F28B" if self._is_dark else "#426D35"

    @Property(str, notify=themeChanged)
    def accentHover(self) -> str:
        return "#C9F8A6" if self._is_dark else "#34572A"

    @Property(str, notify=themeChanged)
    def divider(self) -> str:
        return "#34483C" if self._is_dark else "#DCE4DA"

    @Property(str, notify=themeChanged)
    def positive(self) -> str:
        return "#B8F28B" if self._is_dark else "#286B43"

    @Property(str, notify=themeChanged)
    def negative(self) -> str:
        return "#FFB4A9" if self._is_dark else "#B54136"

    @Property(str, notify=themeChanged)
    def informational(self) -> str:
        return "#82C9D4" if self._is_dark else "#246C82"

    @Property(str, notify=themeChanged)
    def warning(self) -> str:
        return "#E9BE76" if self._is_dark else "#855A12"

    # Button text contrast color
    @Property(str, notify=themeChanged)
    def accentButtonText(self) -> str:
        return "#17251F" if self._is_dark else "#FFFFFF"
