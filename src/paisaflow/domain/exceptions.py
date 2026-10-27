"""Domain exceptions for PaisaFlow financial rules and validation."""


class FinancialDomainError(Exception):
    """Base exception for all financial domain rule violations."""

    pass


class InvalidMonetaryValueError(FinancialDomainError):
    """Raised when an invalid monetary value is supplied (e.g. float, negative where forbidden)."""

    pass


class InvalidTransactionError(FinancialDomainError):
    """Raised when transaction invariants are violated."""

    pass


class InvalidTransferError(FinancialDomainError):
    """Raised when an internal transfer is invalid (e.g. identical source/dest, wrong legs)."""

    pass


class UnbalancedLedgerError(FinancialDomainError):
    """Raised when double-entry ledger legs do not balance."""

    pass


class EntityNotFoundError(FinancialDomainError):
    """Raised when an account, category, person, or transaction is not found."""

    pass


class AccountArchivedError(FinancialDomainError):
    """Raised when attempting an operation on an archived account."""

    pass


class CategoryArchivedError(FinancialDomainError):
    """Raised when attempting to post a transaction to an archived category."""

    pass


class IncompatibleCategoryError(FinancialDomainError):
    """Raised when category type does not match transaction type (e.g. expense category for income)."""

    pass


class InvalidDebtPaymentError(FinancialDomainError):
    """Raised when a debt repayment is invalid (non-positive, overpayment, or settled debt)."""

    pass


class DestructiveActionRestrictedError(FinancialDomainError):
    """Raised when attempting to delete an entity with existing financial history."""

    pass
