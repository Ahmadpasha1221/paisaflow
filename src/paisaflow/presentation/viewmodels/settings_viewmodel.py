"""SettingsViewModel managing app configuration, backups, restoration, and data export."""

from datetime import datetime, timezone
from pathlib import Path

from PySide6.QtCore import Property, QObject, Signal, Slot

from paisaflow.config.settings import settings
from paisaflow.infrastructure.backup.backup_service import BackupService
from paisaflow.infrastructure.database.engine import Engine
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from paisaflow.infrastructure.export.csv_exporter import CsvExportService


class SettingsViewModel(QObject):
    settingsChanged = Signal()
    backupsChanged = Signal()
    databaseRestored = Signal()
    operationSuccess = Signal(str)
    operationError = Signal(str)

    def __init__(self, uow: SqlAlchemyUnitOfWork, engine: Engine) -> None:
        super().__init__()
        self._uow = uow
        self._engine = engine
        self._backup_service = BackupService(engine=engine)
        self._export_service = CsvExportService(uow=uow)

    @Property(str, notify=settingsChanged)
    def appVersion(self) -> str:
        return settings.version

    @Property(str, notify=settingsChanged)
    def currency(self) -> str:
        return "INR (₹) - Indian Rupee"

    @Property(str, notify=settingsChanged)
    def locale(self) -> str:
        return "en-IN"

    @Property(str, notify=settingsChanged)
    def databasePath(self) -> str:
        return str(settings.database_path)

    @Property(str, notify=settingsChanged)
    def backupDirectory(self) -> str:
        return str(settings.backup_dir)

    @Property(str, notify=settingsChanged)
    def logDirectory(self) -> str:
        return str(settings.log_dir)

    @Property(list, notify=backupsChanged)
    def backups(self) -> list:
        """Available backup snapshots, newest first, for the restore workflow."""
        entries = []
        for path in self._backup_service.list_backups():
            stat = path.stat()
            entries.append(
                {
                    "path": str(path),
                    "name": path.name,
                    "sizeText": f"{stat.st_size / 1024:.0f} KB",
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                }
            )
        return entries

    @Slot(result=str)
    def createBackup(self) -> str:
        try:
            backup_file = self._backup_service.create_backup()
            msg = f"Backup saved: {backup_file.name}"
            self.operationSuccess.emit(msg)
            self.backupsChanged.emit()
            return str(backup_file)
        except Exception as e:
            self.operationError.emit(f"Backup failed: {e}")
            return ""

    @Slot(str, result=bool)
    def restoreBackup(self, backup_path_str: str) -> bool:
        try:
            path = Path(backup_path_str)
            if not path.exists():
                self.operationError.emit("Specified backup file does not exist.")
                return False

            self._backup_service.restore_backup(path)
            self.operationSuccess.emit("Database successfully restored from backup snapshot.")
            self.backupsChanged.emit()
            self.databaseRestored.emit()
            return True
        except Exception as e:
            self.operationError.emit(f"Restore failed: {e}")
            return False

    @Slot(str, result=str)
    def exportTransactionsCsv(self, destination_dir_str: str = "") -> str:
        try:
            dest_dir = (
                Path(destination_dir_str)
                if destination_dir_str
                else settings.base_data_dir / "exports"
            )
            dest_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            export_file = dest_dir / f"paisaflow_transactions_{timestamp}.csv"

            self._export_service.export_transactions(export_file)
            msg = f"Exported to {export_file.name}"
            self.operationSuccess.emit(msg)
            return str(export_file)
        except Exception as e:
            self.operationError.emit(f"Export failed: {e}")
            return ""
