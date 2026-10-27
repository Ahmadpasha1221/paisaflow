# PaisaFlow — Release & Packaging Specification

## 1. Overview
PaisaFlow distributes as a self-contained Windows desktop application. It requires zero technical configuration, zero cloud dependencies, and operates with local SQLite persistence located in `%LOCALAPPDATA%\PaisaFlow`.

---

## 2. Windows Packaging Architecture

### 2.1 Target Packaging Tools
- **PyInstaller / pyside6-deploy**:
  - Compiles the application into a standalone folder or single executable bundle including Python runtime, PySide6 DLLs, Qt QML plugins, and compiled QML assets.
  - Windows executable metadata: application icon, company name, product version, file description.
  - Entry point: `paisaflow/main.py`.

### 2.2 Data Directory Separation
- **Application Binaries**: `C:\Program Files\PaisaFlow\` (or user portable folder).
- **User Data & Database**: `%LOCALAPPDATA%\PaisaFlow\data\paisaflow.db`.
- **Backups**: `%LOCALAPPDATA%\PaisaFlow\backups\`.
- **Logs**: `%LOCALAPPDATA%\PaisaFlow\logs\paisaflow.log`.
- **Upgrade Invariant**: Overwriting or replacing binary files during an application update NEVER touches or alters the data directory.

---

## 3. Pre-Release Verification Checklist
1. All automated tests in `tests/` pass with zero failures.
2. Code formatting and linting (`ruff check`, `ruff format --check`) pass.
3. Clean-install test on a system without Python installed.
4. Verify database creation, initial migration, and sample/empty state on first run.
5. Verify backup creation and restore on fresh directory.
6. Verify export of CSV transactions.
7. Verify both Dark and Light themes render with correct contrast.
