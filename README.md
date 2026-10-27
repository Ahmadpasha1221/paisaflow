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

## Getting Started

### Prerequisites
- Windows 10/11
- Python 3.11+ (Python 3.12 / 3.13 supported)

### Development Setup
```powershell
# 1. Clone repository and navigate
cd PaisaFlow

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Run application
python main.py
```

### Running Tests
```powershell
pytest -v
```

### Building the Windows Executable
```powershell
python scripts/build_windows.py
```
The bundle is written to `dist/PaisaFlow/`. See [Release & Packaging Guide](docs/release.md)
for verification steps.

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
