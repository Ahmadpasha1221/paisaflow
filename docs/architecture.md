# PaisaFlow — Architecture Specification

## 1. Overview
PaisaFlow is an offline-first, single-user desktop personal finance application built for Windows using Python, PySide6 (Qt Quick / QML), SQLite, and SQLAlchemy. It is designed around financial domain correctness, local privacy, auditability, and clear separation of concerns.

## 2. Architectural Boundaries & Layering

The application follows clean architecture principles with strict dependency direction: Presentation -> Application -> Domain <- Infrastructure.

```
+-----------------------------------------------------------+
|              Presentation Layer (PySide6 / QML)           |
|  - QML Views (App.qml, Pages, Components, Dialogs)        |
|  - QObject ViewModels / Controllers (Bridge to UI)        |
|  - Qt AbstractItemModels (Paginated & Filtered Lists)     |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|                    Application Layer                      |
|  - Use Case Services (TransactionService, AccountService) |
|  - Command & Query Handlers                               |
|  - Data Transfer Objects (DTOs)                           |
+-----------------------------------------------------------+
         |                                         |
         v                                         v
+-----------------------+              +--------------------+
|     Domain Layer      |              |   Infrastructure   |
| - Entities (Account,  |              | - SQLite / Engine  |
|   Transaction, etc.)  |<-------------| - SQLAlchemy ORM   |
| - Value Objects: Money|              |   Repositories     |
|   (Paise/Int), Date   |              | - Migrations       |
| - Financial Invariants|              | - Backup & Restore |
| - Domain Services     |              | - CSV Export       |
+-----------------------+              +--------------------+
```

### 2.1 Domain Layer (`src/paisaflow/domain/`)
- Pure Python business logic with zero dependencies on PySide6, Qt, QML, or database drivers.
- **Value Objects**:
  - `Money`: Exact integer minor units (`Paise` for INR; 1 INR = 100 paise). Explicit arithmetic with rounding policies; no binary floats.
  - `Currency`: ISO code (`INR`), symbol (`₹`), locale formatting parameters.
- **Entities**:
  - `Person`: Member of household or primary individual.
  - `Account`: Storage of value (Cash, Bank, Savings, Credit Card, Other).
  - `Category`: Income or Expense tax/budget grouping with optional hierarchy.
  - `Transaction`: Economic event with date, description, type, person, entries.
  - `TransactionEntry`: Double-entry signed movement affecting a specific account.
  - `Budget`: Category or person spending limit for a period (e.g. monthly).
  - `SavingsGoal`: Target asset accumulation tracking.
  - `Debt`: Money lent or borrowed with counterparty tracking and repayment links.
- **Domain Invariants**:
  - Balanced multi-leg transactions (sum of balanced debits/credits where appropriate or verified net zero transfer legs).
  - Explicit sign conventions per account type.
  - Transfers never count as income or expense.
  - Historical records are immutable; corrections done via voiding or reversal entries.

### 2.2 Application Layer (`src/paisaflow/application/`)
- Coordinates business use cases.
- Exposes transactional boundaries through Unit of Work.
- Converts Domain Entities into read-only DTOs for consumption by presentation models.
- Validates inputs before domain operations (via Pydantic schemas or domain validators).
- Services:
  - `AccountService`: Manage accounts, calculate real-time ledger balances.
  - `TransactionService`: Record income, expense, transfer, adjustment, split transactions atomically.
  - `PersonService`: Manage profiles, household summary, person-scoped spending.
  - `BudgetService`: Evaluate utilization, threshold alerts (75%, 90%, 100%).
  - `GoalService`: Track savings goals and linked accounts/transfers.
  - `DebtService`: Track loans, repayments, and outstanding balances.
  - `ReportService`: Cash flow, category breakdown, net worth over time.
  - `BackupService`: Safe SQLite online backup API snapshots and validation before restore.
  - `ExportService`: Structured CSV export for transactions and financial summaries.

### 2.3 Infrastructure Layer (`src/paisaflow/infrastructure/`)
- Database access via SQLAlchemy 2.0 with SQLite engine configured with foreign keys enabled (`PRAGMA foreign_keys = ON;`).
- Schema migrations using Alembic with deterministic auto-upgrades on application startup.
- Safe backup and restore using SQLite's native backup API (`sqlite3.Connection.backup`), guaranteeing atomic snapshots without locking errors.
- Logging with sanitized output (no monetary or personal data in error logs).
- Local storage directories resolved through platform-standard paths (`%LOCALAPPDATA%\PaisaFlow`).

### 2.4 Presentation Layer (`src/paisaflow/presentation/`)
- **PySide6 / QML**: Modern desktop UI using Qt Quick Controls with the custom Flowline design system.
- ViewModels inherit from `QObject` with `@Property`, `@Signal`, and `@Slot` to expose reactive state and methods to QML.
- List/Table views backed by `QAbstractListModel` / `QAbstractTableModel` for smooth performance with large data sets without loading unlimited rows into memory.
- Theme engine provides dynamic switching between Dark and Light themes with persistent preference storage.
- Custom canvas or Qt Charts integration for financial visualization (spending trends, category distribution).

## 3. Data Flow & Concurrency
- Long-running tasks (backup creation, large CSV exports, complex reports) execute via worker threads (`QRunnable` / `QThreadPool`) returning results via Qt signals to prevent UI stutter.
- UI event handlers never execute business logic directly; they delegate to ViewModels which invoke Application Services inside an atomic Unit of Work.
- Error handling propagates friendly error messages to the UI via toast notifications and banner states, while capturing sanitized diagnostics in log files.

## 4. Privacy & Security
- 100% offline; zero telemetry or network calls.
- Data kept in user profile directory (`%LOCALAPPDATA%\PaisaFlow\paisaflow.db`).
- Database backups validated for schema version and cryptographic hash before restoration.
