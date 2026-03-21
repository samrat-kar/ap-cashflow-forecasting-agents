"""discount_opportunity_tool — flags invoices whose early-pay discount window closes soon."""

from datetime import date, timedelta
from langchain_core.tools import tool


@tool
def discount_opportunity_tool(
    open_invoices: list[dict],
    vendor_master: list[dict],
    window_days: int = 3,
) -> list[dict]:
    """
    Find invoices where the early payment discount window closes within window_days days.
    Returns a list of flagged invoices with potential savings amount.
    """
    today = date.today()
    cutoff = today + timedelta(days=window_days)

    vendor_map = {v["vendor_id"]: v for v in vendor_master}
    opportunities = []

    for inv in open_invoices:
        discount_by_str = inv.get("discount_if_paid_by", "")
        if not discount_by_str:
            continue
        try:
            discount_by = date.fromisoformat(discount_by_str)
            amount = float(inv["amount"])
        except (ValueError, TypeError):
            continue

        if today <= discount_by <= cutoff:
            vid = inv.get("vendor_id", "")
            vendor = vendor_map.get(vid, {})
            discount_pct = float(vendor.get("early_pay_discount_pct", 0))
            savings = round(amount * discount_pct, 2)

            opportunities.append({
                "invoice_id": inv.get("invoice_id"),
                "vendor_id": vid,
                "vendor_name": inv.get("vendor_name", vendor.get("vendor_name", "")),
                "amount": amount,
                "discount_pct": discount_pct,
                "potential_savings": savings,
                "discount_if_paid_by": discount_by_str,
                "days_remaining": (discount_by - today).days,
            })

    return sorted(opportunities, key=lambda x: x["days_remaining"])
