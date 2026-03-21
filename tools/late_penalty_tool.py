"""late_penalty_tool — flags high-risk vendors with large upcoming invoices."""

from langchain_core.tools import tool

RISK_RELIABILITY_THRESHOLD = 0.80   # vendors below this are considered high-risk
LARGE_INVOICE_THRESHOLD = 1000.0    # invoices above this are flagged


@tool
def late_penalty_tool(
    open_invoices: list[dict],
    vendor_master: list[dict],
    reliability_threshold: float = RISK_RELIABILITY_THRESHOLD,
    amount_threshold: float = LARGE_INVOICE_THRESHOLD,
) -> list[dict]:
    """
    Identify invoices from vendors with low reliability scores that have large amounts.
    These are at risk of late payment and potential late fees.
    Returns a list of flagged invoices with risk details.
    """
    vendor_map = {v["vendor_id"]: v for v in vendor_master}
    flags = []

    for inv in open_invoices:
        vid = inv.get("vendor_id", "")
        vendor = vendor_map.get(vid, {})
        try:
            reliability = float(vendor.get("reliability_score", 1.0))
            amount = float(inv["amount"])
            late_fee_pct = float(vendor.get("late_fee_pct", 0))
        except (ValueError, TypeError):
            continue

        if reliability < reliability_threshold and amount >= amount_threshold:
            potential_fee = round(amount * late_fee_pct, 2)
            flags.append({
                "invoice_id": inv.get("invoice_id"),
                "vendor_id": vid,
                "vendor_name": inv.get("vendor_name", vendor.get("vendor_name", "")),
                "due_date": inv.get("due_date"),
                "amount": amount,
                "reliability_score": reliability,
                "late_fee_pct": late_fee_pct,
                "potential_late_fee": potential_fee,
                "risk_level": "HIGH" if reliability < 0.70 else "MEDIUM",
            })

    return sorted(flags, key=lambda x: x["reliability_score"])
