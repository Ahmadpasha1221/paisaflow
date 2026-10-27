# PaisaFlow — Data Model Specification

## 1. Principles
1. **Explicit Integer Minor Units**: All monetary values are stored as integers representing Paise (1 INR = 100 paise). SQLite `INTEGER` is used.
2. **Double-Entry Grounding**: Balances are calculated through ledger entries (`TransactionEntry`). An account's current balance is the sum of its opening balance plus all signed entries.
3. **Immutability of History**: Historical transactions are never silently altered. Modifications create audit entries or follow void/reversal workflows.
4. **Relational Integrity**: Foreign keys (`PRAGMA foreign_keys = ON`) with `RESTRICT` on accounts and categories that have transaction history to prevent orphaned records.
5. **Multi-profile & Multi-context**: All transactions, accounts, and budgets associate with a `Person` or are scoped to Household (all people).

---

## 2. Entity Relational Schema

### 2.1 Person
Represents a household member or primary profile.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `color_code` (TEXT NOT NULL DEFAULT '#B8F28B')
- `avatar_path` (TEXT NULL)
- `is_active` (BOOLEAN NOT NULL DEFAULT 1)
- `created_at` (TEXT NOT NULL) -- ISO8601 UTC
- `updated_at` (TEXT NOT NULL)

### 2.2 Account
Represents an asset or liability store of value.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `account_type` (TEXT NOT NULL) -- 'cash', 'bank', 'savings', 'credit_card', 'other'
- `owner_person_id` (INTEGER NOT NULL, FK -> Person.id)
- `currency` (TEXT NOT NULL DEFAULT 'INR')
- `opening_balance_paise` (INTEGER NOT NULL DEFAULT 0)
- `opening_date` (TEXT NOT NULL) -- YYYY-MM-DD
- `is_archived` (BOOLEAN NOT NULL DEFAULT 0)
- `notes` (TEXT NULL)
- `created_at` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.3 Category
Classification of income or expense.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `category_type` (TEXT NOT NULL) -- 'income', 'expense'
- `parent_id` (INTEGER NULL, FK -> Category.id)
- `icon_name` (TEXT NOT NULL DEFAULT 'tag')
- `color_code` (TEXT NOT NULL DEFAULT '#82C9D4')
- `is_archived` (BOOLEAN NOT NULL DEFAULT 0)
- `created_at` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.4 Transaction
Economic event representing income, expense, transfer, adjustment, or refund.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `reference_no` (TEXT UNIQUE NOT NULL) -- e.g. TXN-20261027-ABCD
- `transaction_date` (TEXT NOT NULL) -- YYYY-MM-DD
- `transaction_time` (TEXT NOT NULL) -- HH:MM:SS
- `transaction_type` (TEXT NOT NULL) -- 'income', 'expense', 'transfer', 'adjustment', 'refund'
- `description` (TEXT NOT NULL)
- `amount_paise` (INTEGER NOT NULL) -- Positive absolute value in minor units
- `person_id` (INTEGER NOT NULL, FK -> Person.id)
- `category_id` (INTEGER NULL, FK -> Category.id) -- Required for income/expense
- `payment_method` (TEXT NOT NULL) -- 'cash', 'upi', 'debit_card', 'credit_card', 'bank_transfer', 'other'
- `status` (TEXT NOT NULL DEFAULT 'completed') -- 'completed', 'voided', 'reconciled'
- `related_transaction_id` (INTEGER NULL, FK -> Transaction.id) -- E.g. for refund linking
- `notes` (TEXT NULL)
- `created_at` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.5 TransactionEntry (Ledger Leg)
Individual debit/credit balance movement on an account.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `transaction_id` (INTEGER NOT NULL, FK -> Transaction.id ON DELETE CASCADE)
- `account_id` (INTEGER NOT NULL, FK -> Account.id)
- `direction` (TEXT NOT NULL) -- 'inflow' (increases asset / decreases liability), 'outflow' (decreases asset / increases liability)
- `amount_paise` (INTEGER NOT NULL) -- Stored as positive integer; signed calculation handled by direction and account type
- `created_at` (TEXT NOT NULL)

*Transfer Rule*: A transfer transaction generates exactly two `TransactionEntry` records:
1. Outflow from source account.
2. Inflow to destination account.

### 2.6 Budget
Spending limit target for a specific category or person over a period.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `category_id` (INTEGER NULL, FK -> Category.id) -- If NULL, applies to total expenses
- `person_id` (INTEGER NULL, FK -> Person.id) -- If NULL, household-wide
- `period_type` (TEXT NOT NULL DEFAULT 'monthly') -- 'monthly', 'weekly'
- `period_start` (TEXT NOT NULL) -- YYYY-MM-01
- `period_end` (TEXT NOT NULL)
- `limit_amount_paise` (INTEGER NOT NULL)
- `alert_threshold_75` (BOOLEAN NOT NULL DEFAULT 1)
- `alert_threshold_90` (BOOLEAN NOT NULL DEFAULT 1)
- `alert_threshold_100` (BOOLEAN NOT NULL DEFAULT 1)
- `is_active` (BOOLEAN NOT NULL DEFAULT 1)
- `created_at` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.7 SavingsGoal
Target asset accumulation goal.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `name` (TEXT NOT NULL)
- `target_amount_paise` (INTEGER NOT NULL)
- `current_amount_paise` (INTEGER NOT NULL DEFAULT 0)
- `target_date` (TEXT NULL) -- YYYY-MM-DD
- `linked_account_id` (INTEGER NULL, FK -> Account.id)
- `person_id` (INTEGER NOT NULL, FK -> Person.id)
- `is_achieved` (BOOLEAN NOT NULL DEFAULT 0)
- `notes` (TEXT NULL)
- `created_at` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.8 GoalContribution
Explicit record of goal allocations (prevents double-counting with account transfers).
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `goal_id` (INTEGER NOT NULL, FK -> SavingsGoal.id ON DELETE CASCADE)
- `amount_paise` (INTEGER NOT NULL)
- `date` (TEXT NOT NULL)
- `notes` (TEXT NULL)
- `created_at` (TEXT NOT NULL)

### 2.9 Debt
Manual record of money lent or borrowed.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `debt_type` (TEXT NOT NULL) -- 'lent' (asset/receivable), 'borrowed' (liability/payable)
- `person_id` (INTEGER NOT NULL, FK -> Person.id)
- `counterparty_name` (TEXT NOT NULL)
- `principal_amount_paise` (INTEGER NOT NULL)
- `remaining_amount_paise` (INTEGER NOT NULL)
- `due_date` (TEXT NULL) -- YYYY-MM-DD
- `is_settled` (BOOLEAN NOT NULL DEFAULT 0)
- `notes` (TEXT NULL)
- `created_at` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.10 DebtPayment
Record of repayments toward principal.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `debt_id` (INTEGER NOT NULL, FK -> Debt.id ON DELETE CASCADE)
- `amount_paise` (INTEGER NOT NULL)
- `payment_date` (TEXT NOT NULL)
- `account_id` (INTEGER NULL, FK -> Account.id)
- `notes` (TEXT NULL)
- `created_at` (TEXT NOT NULL)

### 2.11 AppSetting
Key-value store for application configuration.
- `key` (TEXT PRIMARY KEY)
- `value` (TEXT NOT NULL)
- `updated_at` (TEXT NOT NULL)

### 2.12 AuditLog
Local append-only audit trail for destructive actions.
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `action` (TEXT NOT NULL) -- 'VOID_TRANSACTION', 'RESTORE_BACKUP', 'ARCHIVE_ACCOUNT', etc.
- `details` (TEXT NOT NULL)
- `timestamp` (TEXT NOT NULL)
