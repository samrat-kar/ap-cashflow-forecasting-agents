"""cash_gap_tool — identifies days where projected outflows exceed the cash threshold."""

from langchain_core.tools import tool


@tool
def cash_gap_tool(
    forecast_schedule: list[dict],
    cash_threshold: float = 15000.0,
) -> list[dict]:
    """
    Find days in the forecast where total projected outflow exceeds cash_threshold.
    Returns a list of flagged dates with amounts and excess.
    """
    flags = []
    for day in forecast_schedule:
        try:
            amount = float(day["projected_amount"])
        except (KeyError, ValueError, TypeError):
            continue
        if amount > cash_threshold:
            flags.append({
                "date": day["date"],
                "projected_amount": amount,
                "threshold": cash_threshold,
                "excess": round(amount - cash_threshold, 2),
                "invoice_ids": day.get("invoice_ids", []),
            })
    return sorted(flags, key=lambda x: x["projected_amount"], reverse=True)
