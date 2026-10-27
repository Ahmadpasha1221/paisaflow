# PaisaFlow — Testing Strategy & Verification Plan

## 1. Quality Assurance Philosophy
Financial applications demand strict verification. Every financial computation, ledger balancing operation, and persistent state transition must have automated test coverage before UI integration.

---

## 2. Testing Levels

Run everything with `pytest` from the repository root. The suite below is the actual
current inventory — it is deliberately factual, so it can be trusted as a coverage map.

### 2.1 Unit Tests (`tests/unit/`)
- **Monetary Logic (`test_money.py`)**
  - Exact integer paise representation (e.g. `Money(100)` = ₹1.00).
  - Rejection of binary floats.
  - Addition, subtraction, scalar multiplication, division with `ROUND_HALF_UP`.
  - Indian numbering formatting (`₹1,23,456.78`) including lakh/crore and negatives.
  - Parsing from user input strings (`"1234.50"`, `"₹ 1,200.00"`, `"-50.25"`).
- **Ledger Policy (`test_ledger_policy.py`)**
  - Asset and credit-card liability balance sign conventions.
  - Entry validation for income and transfers.
  - Rejection of same-account transfers and unbalanced legs.
- **Financial Invariants (`test_financial_invariants.py`)**
  - INV-1 internal transfer leaves total assets unchanged.
  - INV-2 budget utilisation thresholds (75% / 90% / 100%).
  - INV-3 lent = receivable, borrowed = payable, neither is income/expense.
  - INV-4 savings-goal progress and remaining amount.
- **Entity Timestamps (`test_entity_timestamps.py`)**
  - Every entity timestamp is produced by a `default_factory`, not a value frozen at import time.

### 2.2 Integration Tests (`tests/integration/`)
- **Persistence & Ledger Consistency (`test_database_persistence.py`)**
  - Default category seeding on initialisation.
  - Income/expense lifecycle updates account balances exactly.
  - Atomic transfers, and rejection of same-account transfers.
  - Voiding a transaction restores the balance exactly once.
  - Data survives closing and reopening the database.
- **Financial Guards (`test_financial_guards.py`)**
  - Income/expense rejected for a mismatched or archived category.
  - Transactions and transfers rejected for a non-existent person.
  - Debt overpayment, settled-debt repayment, and non-positive repayment rejected.
  - Partial repayments reconcile exactly with the remaining balance.
- **Backup & Restore (`test_backup_restore.py`)**
  - SQLite online-backup integrity and round-trip restore.
  - The pre-restore safety copy captures data still resident in the WAL.
  - Stale `-wal` / `-shm` sidecars are removed during restore.
  - Unrelated SQLite files are rejected as backups.
- **Settings Backup/Restore Workflow (`test_settings_restore_workflow.py`)**
  - Backups are listed, restoring replaces data and notifies the shell, failures are reported.
- **CSV Export (`test_csv_export.py`)**
  - RFC 4180 output with exact amounts, dates, and account tags.
  - Spreadsheet formula injection is neutralised for user-controlled text.

### 2.3 UI & Presentation Tests (`tests/ui/`)
- **QML shell (`test_qml_loading.py`)**: `App.qml` loads offscreen, the window colour binding
  resolves through `themeEngine`, and navigation state changes via `AppViewModel`.

### 2.4 Not yet covered

The following are **not** currently covered by automated tests and are tracked in
[release.md](release.md) as known limitations: GUI form-level validation paths, keyboard/focus
navigation, colour-contrast checks, packaged-executable behaviour, and migration of an existing
database across a schema change.

---

## 3. Financial Invariant Test Matrix

| Invariant | Description | Expected Outcome |
|-----------|-------------|------------------|
| **INV-1** | Internal Transfer | $\Delta \text{Assets} = 0$, $\text{Income} = 0$, $\text{Expense} = 0$ |
| **INV-2** | Split Consistency | $\sum \text{Split Entries} = \text{Transaction Total}$ |
| **INV-3** | Rollback on Failure | If destination account invalid, source account balance unchanged |
| **INV-4** | Loan Inflow | Borrowed cash increases asset & liability; zero earned income |
| **INV-5** | Double-Count Prevention | Goal contribution transfer does not double-count net worth |
| **INV-6** | Idempotent Submission | Double-clicking submit creates exactly one transaction |
| **INV-7** | Reversal Correctness | Voiding a transaction restores account balance exactly to previous state |
