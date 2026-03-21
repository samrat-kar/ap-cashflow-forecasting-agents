"""payment_pattern_tool — calculates average days_variance per vendor from history."""

from langchain_core.tools import tool


@tool
def payment_pattern_tool(payment_history: list[dict]) -> dict[str, float]:
    """
    Group payment history by vendor_id and calculate mean days_variance for each.
    Negative variance = typically pays early; positive = typically pays late.
    Returns: {vendor_id: avg_days_variance}
    """
    totals: dict[str, list[float]] = {}
    for row in payment_history:
        vid = row.get("vendor_id")
        try:
            variance = float(row["days_variance"])
        except (KeyError, ValueError, TypeError):
            continue
        totals.setdefault(vid, []).append(variance)

    return {vid: round(sum(vals) / len(vals), 2) for vid, vals in totals.items()}
