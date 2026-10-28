# PaisaFlow

**Personal finance, made clear.**

PaisaFlow is a modern, offline-first personal and household finance manager built with Python, PySide6 (Qt Quick / QML), SQLite, and SQLAlchemy.

Designed according to the **Flowline** design system, PaisaFlow provides:
- **Strict Financial Correctness**: Double-entry ledger architecture, integer minor units (Paise), zero floating-point arithmetic for currency.
- **Privacy by Default**: 100% offline. No cloud accounts, no telemetry, no tracking. All data resides on your machine.
- **Household & Multi-Profile Support**: Track individual members or view consolidated household finances.
- **Comprehensive Tracking**: Accounts, Income & Expenses, Internal Transfers, Category Budgets, Savings Goals, Debts (Lent/Borrowed), and interactive reports.
- **Data Protection**: One-click verified local backups, recovery snapshots, and CSV export.

---

## Downloads & Installation

Pre-built standalone packages are available from [GitHub Releases](https://github.com/Ahmadpasha1221/paisaflow/releases).
No separate Python, PySide6, or database installation is required.

### Supported Platforms

| Platform | Format | Tested Baseline | Storage Location |
|---|---|---|---|
| **Windows** | Portable ZIP (`.zip`) | Windows 10, 11 (x64) | `%LOCALAPPDATA%\PaisaFlow\` |
| **Linux** | Portable Archive (`.tar.gz`) | Ubuntu 22.04 LTS, Debian 12, glibc ≥ 2.31 | `~/.local/share/paisaflow/` |
| **macOS** | App Bundle ZIP (`.zip`) | macOS 12+ (Apple Silicon & Intel) | `~/Library/Application Support/PaisaFlow/` |

### Installation Instructions

#### Windows
1. Download `PaisaFlow-<version>-windows-x64.zip` from Releases.
2. Extract the ZIP archive to your preferred location (e.g. `C:\Users\<user>\AppData\Local\Programs\PaisaFlow` or Desktop).
3. Run `PaisaFlow.exe`.
4. (Optional) Create a shortcut on your Desktop or pin to your Start Menu / Taskbar.

#### Linux
1. Download `PaisaFlow-<version>-linux-x64.tar.gz` from Releases.
2. Extract the archive:
   ```bash
   tar -xzf PaisaFlow-<version>-linux-x64.tar.gz
   cd PaisaFlow
   ```
3. Run the application:
   ```bash
   ./PaisaFlow
   ```
4. (Optional) Copy `paisaflow.desktop` to `~/.local/share/applications/` for desktop menu integration.

#### macOS
1. Download `PaisaFlow-<version>-macos-<arch>.zip` from Releases.
2. Double-click to unzip the `PaisaFlow.app` bundle.
3. Drag `PaisaFlow.app` into your `/Applications` directory.
4. Launch PaisaFlow from Applications or Spotlight.

> [!NOTE]
> On macOS, because the release binary is unsigned, right-click `PaisaFlow.app` and choose **Open** on first launch, or allow it via **System Settings > Privacy & Security**.

---

## Getting Started (Developers)

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Git

### Development Setup
```powershell
# 1. Clone repository and navigate
cd PaisaFlow

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate    # Linux / macOS

# 3. Install dependencies and dev tools
pip install -e ".[dev]"

# 4. Generate platform icon assets
python scripts/generate_icons.py

# 5. Run application
python main.py
```

### Running Tests
```powershell
pytest tests/ -v
```

### Building Standalone Distribution Packages

```powershell
# Windows x64:
python scripts/build_windows.py

# Linux x64:
python scripts/build_linux.py

# macOS:
python scripts/build_macos.py
```
Packaged distributions, archives, and `.sha256` checksum files are generated in `dist/`.

---

## Local Data & Privacy Scope

PaisaFlow is **100% offline-first**:
- All financial entries, categories, accounts, and settings are stored locally in an embedded SQLite database.
- Zero telemetry, analytics, cloud sync, or background internet access.
- Data directory is strictly decoupled from application binaries, ensuring updates and reinstalls never overwrite your financial ledger.
- To use an alternative storage path (e.g. on an encrypted volume or flash drive), set the `PAISAFLOW_DATA_DIR` environment variable:
  ```powershell
  $env:PAISAFLOW_DATA_DIR = "D:\SecureFinances"
  python main.py
  ```

---

## Privacy & Security Scope

PaisaFlow is offline-first: it makes no network connections and collects no telemetry. It does
**not** encrypt the database, does **not** provide user authentication, and has no application
PIN. Protection therefore relies on your operating-system account security and disk encryption.
People recorded in the app are financial profiles for reporting, not user accounts. See
[Known Limitations](docs/release.md#5-known-limitations) for the full list.

---

## Documentation
- [Architecture](docs/architecture.md)
- [Data Model](docs/data_model.md)
- [Financial Rules & Ledger Invariants](docs/financial_rules.md)
- [Flowline Design System](docs/design_system.md)
- [Testing Strategy](docs/testing.md)
- [Release & Packaging Guide](docs/release.md)
