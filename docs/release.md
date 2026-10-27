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

## 3. Reproducible Build

Build the distributable with the packaging script (it derives every path from its own
location, so no machine-specific configuration is required):

```powershell
.\\.venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
python -m pip install pyinstaller
python scripts/build_windows.py
```

The resulting bundle is written to `dist/PaisaFlow/` (`PaisaFlow.exe` plus `_internal/`).
`PaisaFlow.spec` is an equivalent declarative form of the same build and is also
path-independent.

Verify the bundle before shipping:

```powershell
Test-Path dist/PaisaFlow/PaisaFlow.exe
dist/PaisaFlow/PaisaFlow.exe
```

There is no installer (MSI/Inno Setup) in the repository; the distributable is the
portable folder produced above.

---

## 4. Pre-Release Verification Checklist
1. All automated tests in `tests/` pass with zero failures (`pytest`).
2. Linting passes (`ruff check .`) and formatting is clean (`ruff format --check .`).
3. The packaged executable launches on a clean machine **without** the developer virtual
   environment present.
4. First launch creates the database under `%LOCALAPPDATA%\PaisaFlow\data\` and shows a
   usable empty state.
5. Backup creation and restore both succeed from the Settings page.
6. CSV export completes and opens correctly in a spreadsheet.
7. Both Dark and Light themes render, and the choice survives a restart.
8. Installing into a path containing spaces works.

---

## 5. Known Limitations

The following are deliberate, disclosed limitations of this milestone. They are **not**
implemented, and the application must not be described as providing them:

- **No database encryption.** The SQLite file is stored in plaintext. Protection depends on
  operating-system account security and disk encryption, not on the application.
- **No authentication or access control.** "Profiles" (people) organise records for
  reporting; they are not users and provide no privacy or permission boundary.
- **No application PIN / lock screen.**
- **No schema versioning or migration framework.** `initialize_database()` calls
  `CREATE TABLE IF NOT EXISTS` and seeds defaults. It never drops or resets data, but it
  also cannot alter an existing table, so a future release that changes a column layout
  requires an explicit migration before that release can upgrade existing databases.
- **No automatic backups.** Backups are created only when the user asks. There is therefore
  no backup-retention policy to configure.
- **A CSV export is not a backup.** It contains no schema, no settings, and no accounts,
  goals, or debts, and cannot restore an installation.
- **Refunds are not creatable from the UI.** The domain validates a `refund` transaction
  type, but no service or form records one; corrections are made by voiding and re-entering.
- **No duplicate-submission protection** beyond the reference-number uniqueness constraint.
- **No application icon or Windows version metadata** is embedded in the executable.
- **Packaging has not been validated on a machine without Python installed.**
