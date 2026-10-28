# PaisaFlow — Release & Packaging Specification

## 1. Overview
PaisaFlow distributes as a self-contained Windows desktop application. It requires zero technical configuration, zero cloud dependencies, and operates with local SQLite persistence located in `%LOCALAPPDATA%\PaisaFlow`.

---

## 2. Multi-Platform Packaging Architecture

### 2.1 Target Packaging Tools
- **PyInstaller**:
  - Compiles the application into a standalone folder including Python runtime, PySide6 DLLs, Qt QML plugins, and compiled QML assets.
  - Platform metadata: multi-resolution embedded icons (`brand.ico` on Windows, `brand.icns` on macOS, hicolor desktop icons on Linux).
  - Explicit AppUserModelID on Windows (`PaisaFlow.Flowline.Desktop.0.1.0`) ensuring proper taskbar separation from Python.
  - Entry point: `paisaflow/main.py`.

### 2.2 Data Directory Separation
- **Application Binaries**: Read-only distribution folder (e.g. `C:\Program Files\PaisaFlow\` or extracted portable directory).
- **User Data & Database**:
  - Windows: `%LOCALAPPDATA%\PaisaFlow\data\paisaflow.db`
  - Linux: `~/.local/share/paisaflow/data/paisaflow.db`
  - macOS: `~/Library/Application Support/PaisaFlow/data/paisaflow.db`
- **Backups**: Separated under `backups/` in the user data directory.
- **Logs**: Written to `logs/paisaflow.log` in the user data directory.
- **Upgrade Invariant**: Overwriting or replacing binary files during an application update NEVER touches or alters the data directory.

---

## 3. Reproducible Build

Generate icons and build packages locally:

```powershell
# Setup environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# Generate icons
python scripts/generate_icons.py

# Build platform packages
python scripts/build_windows.py   # Windows x64 ZIP + SHA-256
python scripts/build_linux.py     # Linux x64 TAR.GZ + SHA-256
python scripts/build_macos.py     # macOS ZIP + SHA-256
```

All distribution archives and `.sha256` checksums are placed into `dist/`.

---

## 4. Pre-Release Verification Checklist
1. All automated tests in `tests/` pass with zero failures (`pytest tests/ -v`).
2. Linting passes (`ruff check .`).
3. Platform icons (`.ico`, `.icns`, `.png`) are verified and embedded.
4. The packaged executable launches on a clean environment without activating `.venv`.
5. First launch creates the database in the appropriate user data path.
6. Backup creation and restore both succeed from the Settings page.
7. CSV export completes and opens correctly in a spreadsheet.
8. Both Dark and Light themes render, and the choice survives a restart.
9. Installing or launching from a path containing spaces works.

---

## 5. Known Limitations

The following are deliberate, disclosed limitations of this milestone:

- **No database encryption.** The SQLite file is stored in plaintext. Protection depends on operating-system account security and disk encryption.
- **No authentication or access control.** "Profiles" (people) organise records for reporting; they are not users and provide no privacy boundary.
- **No application PIN / lock screen.**
- **No schema versioning or migration framework.** `initialize_database()` calls `CREATE TABLE IF NOT EXISTS` and seeds defaults.
- **No automatic backups.** Backups are created on-demand via the Settings interface.
- **A CSV export is not a backup.** It contains no schema or non-transaction settings and cannot restore an installation.
- **Refunds are not creatable from the UI.** Corrections are made by voiding and re-entering.
- **macOS signing and notarization.** macOS release builds generated without an Apple Developer ID certificate require right-click -> "Open" on first launch.
