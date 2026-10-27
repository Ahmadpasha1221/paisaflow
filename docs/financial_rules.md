# PaisaFlow — Financial Domain Rules & Ledger Specification

## 1. Monetary Representation Principles
1. **Never use IEEE 754 Floating-Point**: Float values such as `0.1 + 0.2 != 0.3` lead to catastrophic rounding errors in ledger systems.
2. **Integer Minor Units (Paise)**: All currency amounts are represented internally as positive 64-bit integers of `paise` ($1\text{ INR} = 100\text{ paise}$).
3. **Decimals for Intermediate Rates**: Any percentage calculations (e.g. tax, interest, budget percentage) utilize Python's `decimal.Decimal` with explicit `ROUND_HALF_UP` or `ROUND_DOWN` rules.
4. **Formatting for Locale**: Formatting to `₹1,23,456.78` (Indian Numbering System with lakh and crore grouping) occurs strictly in the presentation layer.

---

## 2. Ledger Calculation Rules

### 2.1 Account Types & Sign Conventions
Accounts are categorized as either **Asset** or **Liability**:
- **Asset Accounts**: `cash`, `bank`, `savings`, `other_asset`.
  - Inflow (Credit to asset): Increases balance (+).
  - Outflow (Debit to asset): Decreases balance (-).
  - Balance Formula:
    $$\text{Balance} = \text{Opening Balance} + \sum \text{Inflow Entries} - \sum \text{Outflow Entries}$$
- **Liability Accounts**: `credit_card`, `loan_liability`, `other_liability`.
  - Represents what the user owes.
  - Outflow (Charges/Spending): Increases liability balance (+).
  - Inflow (Repayment/Payment): Decreases liability balance (-).
  - Positive balance indicates an outstanding debt owed to the lender.

### 2.2 Transaction Types & Multi-Entry Invariants
1. **Income**:
   - Creates a transaction of type `income`.
   - Generates an **inflow** `TransactionEntry` on the target Asset account.
   - The category must be an **income** category (`IncompatibleCategoryError` otherwise).
   - Reflected in Income Reports and Cash Flow as positive cash flow.
   - Budget impact: None (budgets track expenses).

2. **Expense**:
   - Creates a transaction of type `expense`.
   - Generates an **outflow** `TransactionEntry` on the source account (Asset balance decreases or Credit Card liability increases).
   - The category must be an **expense** category (`IncompatibleCategoryError` otherwise).
   - Reflected in Expense Reports and Cash Flow as negative cash flow.
   - Budget impact: Consumes corresponding category and person budget limit.

3. **Internal Transfer**:
   - Moves money between two owned accounts (e.g. Bank to Cash or Bank to Credit Card repayment).
   - Generates two linked entries within a single atomic database transaction:
     - `Entry 1`: Outflow from Source Account (`amount_paise`).
     - `Entry 2`: Inflow to Destination Account (`amount_paise`).
   - **Critical Invariant**: Transfers **NEVER** affect income or expense reports, and do not change total household Net Worth.
   - For Credit Card Repayment: Outflow from Bank Account, Inflow to Credit Card Account (reducing liability).

4. **Refunds & Reversals**:
   - An expense refund is linked via `related_transaction_id` to the original expense where applicable.
   - Treated as an **expense reduction** rather than earned income, preventing false inflation of gross income.
   - Reverses or offsets the category spending against active budgets.

5. **Loan Principal & Debt**:
   - **Money Lent**: Outflow from Asset account, recorded as a receivable debt. Does not count as an expense.
   - **Money Borrowed**: Inflow to Asset account, recorded as a debt liability. Does not count as income.
   - **Repayments**: Reduce the outstanding debt principal balance by the exact repaid amount.
   - A repayment must be strictly positive, may **not** exceed the outstanding balance, and may not
     be recorded against an already-settled debt (`InvalidDebtPaymentError`). Overpayments are
     rejected rather than silently truncated, so repayment history always reconciles with the
     original principal.

---

## 3. Net Worth & Cash Flow Calculations
1. **Total Assets**:
   $$\text{Assets} = \sum_{\text{Asset Accounts}} \text{Balance} + \sum_{\text{Active Lent Debts}} \text{Remaining Principal}$$
2. **Total Liabilities**:
   $$\text{Liabilities} = \sum_{\text{Liability Accounts}} \text{Balance} + \sum_{\text{Active Borrowed Debts}} \text{Remaining Principal}$$
3. **Net Worth**:
   $$\text{Net Worth} = \text{Total Assets} - \text{Total Liabilities}$$
4. **Net Cash Flow (Period)**:
   $$\text{Net Cash Flow} = \sum_{\text{Period}} \text{Income} - \sum_{\text{Period}} \text{Expenses}$$

---

## 4. Input Validation Guards

These guards are enforced in the application services, so an invalid operation is rejected
before any ledger entry is written:

| Guard | Rule | Exception |
|-------|------|-----------|
| Category type | An income transaction requires an income category; an expense requires an expense category. | `IncompatibleCategoryError` |
| Archived category | Archived categories cannot receive new transactions. | `CategoryArchivedError` |
| Archived account | Archived accounts cannot receive income, expenses, or transfers. | `AccountArchivedError` |
| Person reference | Transactions and transfers must reference an existing person. | `EntityNotFoundError` |
| Account reference | Transactions and transfers must reference existing accounts. | `EntityNotFoundError` |
| Self transfer | Source and destination accounts must differ. | `InvalidTransferError` |
| Amount sign | Transaction, entry, and repayment amounts must be strictly positive. | `InvalidTransactionError` / `InvalidDebtPaymentError` |
| Debt repayment | Repayments may not exceed the outstanding balance or target a settled debt. | `InvalidDebtPaymentError` |
| Monetary type | Binary floats can never initialise a `Money` value. | `InvalidMonetaryValueError` |

---

## 5. Budget Tracking Rules
1. Monthly budgets compare actual category expenses within $[ \text{Month Start}, \text{Month End} ]$.
2. Transferred funds and loan disbursements are excluded from budget utilization.
3. Threshold alerts are triggered at:
   - **75%**: Approaching limit (Informational warning).
   - **90%**: Near capacity (Warning alert).
   - **100%**: Limit reached or exceeded (Critical alert).
4. Shared/Household budgets evaluate expenses aggregated across all household members.
