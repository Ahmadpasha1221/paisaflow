"""Application configuration and filesystem path resolution."""

import os
from pathlib import Path

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    app_name: str = "PaisaFlow"
    version: str = "0.1.0"
    base_data_dir: Path = Field(default_factory=lambda: AppConfig._resolve_base_data_dir())

    @staticmethod
    def _resolve_base_data_dir() -> Path:
        """Resolve platform-specific data directory.

        Windows: %LOCALAPPDATA%\\PaisaFlow
        macOS:   ~/Library/Application Support/PaisaFlow
        Linux:   $XDG_DATA_HOME/paisaflow (default: ~/.local/share/paisaflow)
        Override: PAISAFLOW_DATA_DIR environment variable
        """
        import sys

        env_dir = os.environ.get("PAISAFLOW_DATA_DIR")
        if env_dir:
            return Path(env_dir).resolve()

        if sys.platform == "win32":
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                return Path(local_app_data) / "PaisaFlow"
            return Path.home() / "AppData" / "Local" / "PaisaFlow"
        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "PaisaFlow"
        else:
            # Linux and other Unix systems following XDG Base Directory specification
            xdg_data = os.environ.get("XDG_DATA_HOME")
            if xdg_data:
                return Path(xdg_data) / "paisaflow"
            return Path.home() / ".local" / "share" / "paisaflow"

    @property
    def data_dir(self) -> Path:
        path = self.base_data_dir / "data"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def database_path(self) -> Path:
        return self.data_dir / "paisaflow.db"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database_path.as_posix()}"

    @property
    def backup_dir(self) -> Path:
        path = self.base_data_dir / "backups"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def log_dir(self) -> Path:
        path = self.base_data_dir / "logs"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def log_file(self) -> Path:
        return self.log_dir / "paisaflow.log"


# Singleton instance
settings = AppConfig()
