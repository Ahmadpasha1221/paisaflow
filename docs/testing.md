# PaisaFlow — Testing Strategy & Verification Plan

## 1. Quality Assurance Philosophy
Financial applications demand strict verification. Every financial computation, ledger balancing operation, and persistent state transition must have automated test coverage before UI integration.

---

## 2. Testing Levels

### 2.1 Unit Tests (`tests/unit/`)
- **Monetary Logic (`test_money.py`)**:
  - Exact integer paise representation (e.g. `Money(100)` = ₹1.00).
  - Prevention of floating point instantiation without explicit rounding.
  - Addition, subtraction, multiplication by scalar, division with explicit round modes.
  - Indian numbering system formatting (`₹1,23,456.78`).
  - Parsing from user input strings (`"1234.50"`, `"1,200"`).
- **Domain Entities & Policies (`test_entities.py`, `test_policies.py`)**:
  - Account balance calculation from entries.
  - Credit card liability sign conventions.
  - Transfer invariant: balanced inflow and outflow entries.
  - Exclusion of transfers from income and expense aggregates.
  - Refund policy: reducing expense rather than adding income.
  - Budget alert threshold calculations (75%, 90%, 100%).

### 2.2 Integration Tests (`tests/integration/`)
- **Database Repositories & Unit of Work (`test_repositories.py`)**:
  - Foreign key constraints enforcement.
  - Atomic multi-entry transaction commit & rollback on failure.
  - Migration execution from baseline to latest schema.
  - Reopening SQLite database across process restarts.
- **Application Services (`test_services.py`)**:
  - `AccountService.create_account()`, `archive_account()`.
  - `TransactionService.record_income()`, `record_expense()`, `record_transfer()`, `void_transaction()`.
  - `BudgetService.check_budget_status()`.
  - `GoalService.contribute()`.
  - `DebtService.record_debt()`, `record_payment()`.
- **Backup & Restore (`test_backup.py`)**:
  - Native SQLite online backup integrity.
  - Cryptographic / schema version validation before restore.
  - Restoration idempotency and ledger preservation.
- **Export (`test_export.py`)**:
  - Standard RFC 4180 CSV generation.
  - Correct formatting of amounts, dates, and account tags.

### 2.3 UI & Presentation Tests (`tests/ui/`)
- ViewModels and ListModels:
  - Filtering and pagination responsiveness.
  - Error and loading state exposure.
  - Property change notification signals.
  - Theme switching state management.

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
