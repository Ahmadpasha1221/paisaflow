"""Database backup and restore service utilizing SQLite online backup API."""

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sqlalchemy import Engine

from paisaflow.config.settings import settings


class BackupService:
    def __init__(self, engine: Engine, backup_dir: Optional[Path] = None) -> None:
        self._engine = engine
        self._backup_dir = backup_dir or settings.backup_dir

    def create_backup(self, custom_path: Optional[Path] = None) -> Path:
        """Create a safe, atomic snapshot of the database using SQLite's online backup API."""
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        if custom_path:
            dest_file = custom_path
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            dest_file = self._backup_dir / f"paisaflow_backup_{timestamp}.db"

        # Obtain underlying sqlite3 connection
        raw_conn = self._engine.raw_connection()
        try:
            source_conn: sqlite3.Connection = raw_conn.driver_connection
            with sqlite3.connect(dest_file) as dest_conn:
                source_conn.backup(dest_conn)
        finally:
            raw_conn.close()

        # Validate the generated backup
        self.validate_backup(dest_file)
        return dest_file

    def validate_backup(self, backup_file: Path) -> bool:
        """Run SQLite integrity check on backup file."""
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file does not exist: {backup_file}")

        with sqlite3.connect(backup_file) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            row = cursor.fetchone()
            if not row or row[0] != "ok":
                raise ValueError(f"Backup integrity check failed: {row}")

            # Verify that required schema tables exist
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions';"
            )
            if not cursor.fetchone():
                raise ValueError(
                    "Backup file is not a valid PaisaFlow database (missing transactions table)."
                )

        return True

    def restore_backup(self, backup_file: Path, target_db_path: Optional[Path] = None) -> Path:
        """Validate backup, preserve current database with safety copy, and restore."""
        self.validate_backup(backup_file)
        target = target_db_path or settings.database_path

        # Step 1: Create safety copy of current target database if it exists
        if target.exists():
            safety_copy = (
                target.parent
                / f"{target.name}.recovery_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            )
            shutil.copy2(target, safety_copy)

        # Step 2: Restore backup by atomic copy
        self._engine.dispose()
        shutil.copy2(backup_file, target)
        return target
