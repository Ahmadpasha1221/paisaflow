"""Database backup and restore service utilizing SQLite online backup API."""

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from sqlalchemy import Engine

from paisaflow.config.settings import settings

# Tables that a usable PaisaFlow database must contain. A backup missing any of
# these cannot be restored without silently losing financial records.
REQUIRED_TABLES = frozenset(
    {
        "people",
        "accounts",
        "categories",
        "transactions",
        "transaction_entries",
    }
)


def sqlite_sidecar_paths(db_path: Path) -> tuple[Path, Path]:
    """Return the write-ahead-log and shared-memory sidecar paths for a database file."""
    return (
        db_path.with_name(f"{db_path.name}-wal"),
        db_path.with_name(f"{db_path.name}-shm"),
    )


class BackupService:
    def __init__(self, engine: Engine, backup_dir: Optional[Path] = None) -> None:
        self._engine = engine
        self._backup_dir = backup_dir or settings.backup_dir

    def _engine_db_path(self) -> Path:
        """Return the database file the engine is actually connected to.

        Restoring must always target the live database, never a path that merely
        happens to match the current configuration.
        """
        url = self._engine.url
        if url.get_backend_name() != "sqlite":
            raise ValueError(f"Backup/restore requires a SQLite engine, got {url.drivername}.")
        if not url.database or url.database == ":memory:":
            raise ValueError("Cannot back up or restore an in-memory database.")
        return Path(url.database)

    def list_backups(self) -> List[Path]:
        """Return available backup snapshots from the backup directory, newest first."""
        if not self._backup_dir.exists():
            return []
        backups = [p for p in self._backup_dir.glob("paisaflow_backup_*.db") if p.is_file()]
        return sorted(backups, key=lambda p: p.stat().st_mtime, reverse=True)

    def _snapshot_to(self, dest_file: Path) -> Path:
        """Write a transactionally consistent snapshot of the live database to ``dest_file``.

        Uses SQLite's online backup API so that committed data still sitting in the
        write-ahead log is included. A plain file copy would silently omit it.
        """
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        raw_conn = self._engine.raw_connection()
        try:
            source_conn: sqlite3.Connection = raw_conn.driver_connection
            with sqlite3.connect(dest_file) as dest_conn:
                source_conn.backup(dest_conn)
        finally:
            raw_conn.close()
        return dest_file

    def create_backup(self, custom_path: Optional[Path] = None) -> Path:
        """Create a safe, atomic snapshot of the database using SQLite's online backup API."""
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        if custom_path:
            dest_file = custom_path
        else:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            dest_file = self._backup_dir / f"paisaflow_backup_{timestamp}.db"

        self._snapshot_to(dest_file)

        # Validate the generated backup before reporting success
        self.validate_backup(dest_file)
        return dest_file

    def validate_backup(self, backup_file: Path) -> bool:
        """Run SQLite integrity check on backup file and verify the expected schema is present."""
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file does not exist: {backup_file}")

        with sqlite3.connect(backup_file) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            row = cursor.fetchone()
            if not row or row[0] != "ok":
                raise ValueError(f"Backup integrity check failed: {row}")

            # Verify that required schema tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            present = {r[0] for r in cursor.fetchall()}
            missing = REQUIRED_TABLES - present
            if missing:
                raise ValueError(
                    "Backup file is not a valid PaisaFlow database "
                    f"(missing tables: {', '.join(sorted(missing))})."
                )

        return True

    def restore_backup(self, backup_file: Path, target_db_path: Optional[Path] = None) -> Path:
        """Validate backup, preserve current database with safety copy, and restore.

        The current database is snapshotted through SQLite's backup API (so the safety
        copy includes data still resident in the WAL), the engine is disposed, and any
        stale WAL/SHM sidecars of the previous database are removed before the
        replacement is put in place.
        """
        self.validate_backup(backup_file)
        target = target_db_path or self._engine_db_path()

        # Step 1: Create a consistent safety snapshot of the current target database
        if target.exists():
            safety_copy = target.parent / (
                f"{target.name}.recovery_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            )
            self._snapshot_to(safety_copy)

        # Step 2: Release pooled connections, then restore the backup by atomic copy
        self._engine.dispose()
        shutil.copy2(backup_file, target)

        # Step 3: Drop sidecars belonging to the replaced database so SQLite never
        # tries to recover the old write-ahead log against the new file.
        for sidecar in sqlite_sidecar_paths(target):
            sidecar.unlink(missing_ok=True)

        return target
