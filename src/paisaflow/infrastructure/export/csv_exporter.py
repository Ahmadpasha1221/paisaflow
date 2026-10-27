"""CSV export service for transactions."""

import csv
from pathlib import Path
from typing import Iterable, Optional

from paisaflow.domain.entities.transaction import Transaction
from paisaflow.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork

# Characters that make spreadsheet applications (Excel, LibreOffice, Google Sheets)
# treat a cell as a formula when the CSV is opened directly.
_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@", "\t", "\r")


def sanitize_spreadsheet_cell(value: str) -> str:
    """Neutralise spreadsheet formula injection for user-controlled text fields.

    A leading quote is the conventional, spreadsheet-safe way to keep the original
    text visible while preventing the cell from being evaluated as a formula.
    """
    if value and value[0] in _FORMULA_TRIGGER_CHARS:
        return "'" + value
    return value


class CsvExportService:
    def __init__(self, uow: SqlAlchemyUnitOfWork) -> None:
        self._uow = uow

    def export_transactions(
        self, file_path: Path, transactions: Optional[Iterable[Transaction]] = None
    ) -> Path:
        """Export given transactions or all transactions to a CSV file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with self._uow as uow:
            if transactions is None:
                txns, _ = uow.transactions.query_transactions(limit=100000)
            else:
                txns = list(transactions)

            # Pre-fetch lookup caches for speed
            people = {p.id: p.name for p in uow.people.get_all(include_inactive=True)}
            categories = {c.id: c.name for c in uow.categories.get_all(include_archived=True)}
            accounts = {a.id: a.name for a in uow.accounts.get_all(include_archived=True)}

            headers = [
                "Reference",
                "Date",
                "Time",
                "Type",
                "Description",
                "Amount (INR)",
                "Person",
                "Category",
                "Payment Method",
                "Status",
                "Affected Accounts",
                "Notes",
            ]

            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for t in txns:
                    person_name = people.get(t.person_id, "Unknown")
                    cat_name = categories.get(t.category_id, "") if t.category_id else ""
                    affected_accts = ", ".join(
                        accounts.get(e.account_id, "Unknown") for e in t.entries
                    )

                    writer.writerow(
                        [
                            sanitize_spreadsheet_cell(t.reference_no),
                            t.transaction_date.isoformat(),
                            t.transaction_time.isoformat(),
                            t.transaction_type.value,
                            sanitize_spreadsheet_cell(t.description),
                            t.amount.format(include_symbol=False),
                            sanitize_spreadsheet_cell(person_name),
                            sanitize_spreadsheet_cell(cat_name),
                            t.payment_method.value,
                            t.status.value,
                            sanitize_spreadsheet_cell(affected_accts),
                            sanitize_spreadsheet_cell(t.notes or ""),
                        ]
                    )

        return file_path
