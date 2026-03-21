"""forecast_calculator_tool — projects daily cash outflows for the next 30 days."""

from datetime import date, timedelta
from langchain_core.tools import tool


@tool
def forecast_calculator_tool(
    open_invoices: list[dict],
    vendor_payment_patterns: dict[str, float],
    forecast_horizon_days: int = 30,
) -> list[dict]:
    """
    Adjust each invoice's due date by its vendor's average payment variance,
    then aggregate projected amounts by expected payment date.

    Returns a list of dicts: [{date, projected_amount, invoice_ids}]
    covering the next forecast_horizon_days from today.
    """
    today = date.today()
    end_date = today + timedelta(days=forecast_horizon_days)

    # Accumulate by date
    daily: dict[date, dict] = {}

    for inv in open_invoices:
        vid = inv.get("vendor_id", "")
        try:
            due = date.fromisoformat(inv["due_date"])
            amount = float(inv["amount"])
        except (KeyError, ValueError, TypeError):
            continue

        avg_variance = vendor_payment_patterns.get(vid, 0.0)
        expected_date = due + timedelta(days=int(round(avg_variance)))

        # Only include dates within the forecast window
        if expected_date < today or expected_date > end_date:
            continue

        if expected_date not in daily:
            daily[expected_date] = {"date": expected_date.isoformat(), "projected_amount": 0.0, "invoice_ids": []}
        daily[expected_date]["projected_amount"] = round(daily[expected_date]["projected_amount"] + amount, 2)
        daily[expected_date]["invoice_ids"].append(inv.get("invoice_id", ""))

    # Return sorted list
    return sorted(daily.values(), key=lambda x: x["date"])
