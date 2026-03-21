"""data_validation_tool — validates required fields, date formats, non-negative amounts."""

from datetime import date
from langchain_core.tools import tool

INVOICE_REQUIRED = ["invoice_id", "vendor_id", "due_date", "amount"]
HISTORY_REQUIRED = ["vendor_id", "due_date", "actual_payment_date", "amount", "days_variance"]
VENDOR_REQUIRED  = ["vendor_id", "vendor_name", "payment_terms_days", "reliability_score"]


def _check_date(value: str, field: str, row_id: str) -> str | None:
    try:
        date.fromisoformat(value)
        return None
    except (ValueError, TypeError):
        return f"[{row_id}] Invalid date in '{field}': {value!r}"


def _check_non_negative(value: str, field: str, row_id: str) -> str | None:
    try:
        if float(value) < 0:
            return f"[{row_id}] Negative value in '{field}': {value}"
        return None
    except (ValueError, TypeError):
        return f"[{row_id}] Non-numeric value in '{field}': {value!r}"


@tool
def data_validation_tool(
    invoices: list[dict],
    payment_history: list[dict],
    vendors: list[dict],
) -> list[str]:
    """
    Validate all three datasets for required fields, date formats, and non-negative amounts.
    Returns a list of issue strings (empty list = no issues).
    """
    issues: list[str] = []

    # --- Invoices ---
    for row in invoices:
        rid = row.get("invoice_id", "UNKNOWN")
        for field in INVOICE_REQUIRED:
            if not row.get(field):
                issues.append(f"[{rid}] Missing required field: '{field}'")
        if row.get("due_date"):
            if err := _check_date(row["due_date"], "due_date", rid):
                issues.append(err)
        if row.get("amount"):
            if err := _check_non_negative(row["amount"], "amount", rid):
                issues.append(err)

    # --- Payment history ---
    for row in payment_history:
        rid = row.get("payment_id", row.get("invoice_id", "UNKNOWN"))
        for field in HISTORY_REQUIRED:
            if not row.get(field):
                issues.append(f"[{rid}] Missing required field: '{field}'")
        for date_field in ("due_date", "actual_payment_date"):
            if row.get(date_field):
                if err := _check_date(row[date_field], date_field, rid):
                    issues.append(err)
        if row.get("amount"):
            if err := _check_non_negative(row["amount"], "amount", rid):
                issues.append(err)

    # --- Vendors ---
    for row in vendors:
        rid = row.get("vendor_id", "UNKNOWN")
        for field in VENDOR_REQUIRED:
            if not row.get(field):
                issues.append(f"[{rid}] Missing required field: '{field}'")

    return issues
