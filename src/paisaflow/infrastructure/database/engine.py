"""Database engine setup with SQLite foreign key enforcement and WAL mode."""

from pathlib import Path
from typing import Optional

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def configure_sqlite_pragmas(dbapi_connection, connection_record) -> None:  # noqa: ANN001
    """Enforce strict SQLite settings for financial integrity."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.close()


def create_db_engine(db_path: Optional[Path] = None, in_memory: bool = False) -> Engine:
    """Create and configure a SQLAlchemy SQLite engine with financial safety pragmas."""
    if in_memory:
        url = "sqlite:///:memory:"
    elif db_path:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{db_path.as_posix()}"
    else:
        from paisaflow.config.settings import settings

        url = settings.database_url

    engine = create_engine(
        url,
        echo=False,
        future=True,
    )
    event.listen(engine, "connect", configure_sqlite_pragmas)
    return engine


def create_session_factory(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
