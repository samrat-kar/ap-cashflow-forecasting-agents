"""
generate_data.py
Generates simulated AP data: vendors.csv, open_invoices.csv, payment_history.csv
Run: python data/generate_data.py
"""

import csv
import random
import os
from datetime import date, timedelta

random.seed(42)

TODAY = date.today()
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Vendor definitions
# ---------------------------------------------------------------------------
VENDORS = [
    {"vendor_id": "V001", "vendor_name": "Acme Software",   "payment_terms_days": 30, "category": "Software",        "avg_invoice_amount": 5000,  "amount_std_dev": 800,  "reliability_score": 0.95, "early_pay_discount_pct": 0.02,  "early_pay_discount_days": 10, "late_fee_pct": 0.015},
    {"vendor_id": "V002", "vendor_name": "Global Supplies",  "payment_terms_days": 60, "category": "Office Supplies", "avg_invoice_amount": 1200,  "amount_std_dev": 300,  "reliability_score": 0.75, "early_pay_discount_pct": 0.00,  "early_pay_discount_days": 0,  "late_fee_pct": 0.010},
    {"vendor_id": "V003", "vendor_name": "CloudHost Inc",    "payment_terms_days": 15, "category": "Infrastructure",  "avg_invoice_amount": 8500,  "amount_std_dev": 500,  "reliability_score": 0.99, "early_pay_discount_pct": 0.015, "early_pay_discount_days": 5,  "late_fee_pct": 0.020},
    {"vendor_id": "V004", "vendor_name": "Office Pro",       "payment_terms_days": 45, "category": "Office Supplies", "avg_invoice_amount": 650,   "amount_std_dev": 150,  "reliability_score": 0.85, "early_pay_discount_pct": 0.00,  "early_pay_discount_days": 0,  "late_fee_pct": 0.005},
    {"vendor_id": "V005", "vendor_name": "Freight Fast",     "payment_terms_days": 30, "category": "Freight",         "avg_invoice_amount": 2200,  "amount_std_dev": 600,  "reliability_score": 0.70, "early_pay_discount_pct": 0.01,  "early_pay_discount_days": 7,  "late_fee_pct": 0.012},
    {"vendor_id": "V006", "vendor_name": "TechConsult LLC",  "payment_terms_days": 45, "category": "Consulting",      "avg_invoice_amount": 12000, "amount_std_dev": 2000, "reliability_score": 0.90, "early_pay_discount_pct": 0.02,  "early_pay_discount_days": 10, "late_fee_pct": 0.018},
    {"vendor_id": "V007", "vendor_name": "Rapid Courier",    "payment_terms_days": 15, "category": "Freight",         "avg_invoice_amount": 450,   "amount_std_dev": 100,  "reliability_score": 0.65, "early_pay_discount_pct": 0.00,  "early_pay_discount_days": 0,  "late_fee_pct": 0.008},
]

VENDOR_MAP = {v["vendor_id"]: v for v in VENDORS}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def rand_amount(avg, std):
    """Return a positive rounded invoice amount."""
    return max(50.0, round(random.gauss(avg, std), 2))


def days_variance_for_vendor(reliability_score):
    """
    Draw a days_variance from a distribution shaped by reliability.
    High reliability → tight cluster around 0.
    Low reliability → skewed positive (late payments).
    """
    if reliability_score >= 0.95:
        return int(round(random.gauss(0, 1)))
    elif reliability_score >= 0.85:
        return int(round(random.gauss(1, 3)))
    elif reliability_score >= 0.75:
        return int(round(random.gauss(3, 5)))
    elif reliability_score >= 0.65:
        return int(round(random.gauss(5, 7)))
    else:
        return int(round(random.gauss(8, 10)))


def is_q4(d: date) -> bool:
    return d.month in (10, 11, 12)


# ---------------------------------------------------------------------------
# 1. vendors.csv
# ---------------------------------------------------------------------------

def generate_vendor_master():
    path = os.path.join(DATA_DIR, "vendors.csv")
    fieldnames = [
        "vendor_id", "vendor_name", "payment_terms_days", "category",
        "avg_invoice_amount", "amount_std_dev", "reliability_score",
        "early_pay_discount_pct", "early_pay_discount_days", "late_fee_pct"
    ]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(VENDORS)
    print(f"  Written: {path}  ({len(VENDORS)} vendors)")


# ---------------------------------------------------------------------------
# 2. payment_history.csv  (12 months of history)
# ---------------------------------------------------------------------------

def generate_payment_history(months=12):
    path = os.path.join(DATA_DIR, "payment_history.csv")
    fieldnames = [
        "payment_id", "vendor_id", "invoice_id",
        "due_date", "actual_payment_date", "amount", "days_variance"
    ]

    rows = []
    payment_counter = 1

    start_date = TODAY - timedelta(days=months * 30)

    for vendor in VENDORS:
        vid = vendor["vendor_id"]
        terms = vendor["payment_terms_days"]
        avg = vendor["avg_invoice_amount"]
        std = vendor["amount_std_dev"]

        # Walk month by month
        cursor = start_date
        inv_counter = 1
        while cursor < TODAY - timedelta(days=7):  # leave a week gap before today
            # 2-4 invoices per month per vendor
            num_invoices = random.randint(2, 4)
            for _ in range(num_invoices):
                # Invoice date spread across the month
                inv_date = cursor + timedelta(days=random.randint(0, 28))
                if inv_date >= TODAY - timedelta(days=7):
                    continue

                due = inv_date + timedelta(days=terms)
                if due >= TODAY:
                    continue  # skip if not yet due (will be open invoice)

                # Q4 volume spike
                multiplier = 1.25 if is_q4(inv_date) else 1.0
                amount = round(rand_amount(avg, std) * multiplier, 2)

                variance = days_variance_for_vendor(vendor["reliability_score"])
                actual_payment = due + timedelta(days=variance)

                invoice_id = f"HIST-{vid}-{inv_counter:04d}"
                inv_counter += 1

                # ~5% chance of partial payment (split into two rows)
                if random.random() < 0.05:
                    part1 = round(amount * random.uniform(0.4, 0.6), 2)
                    part2 = round(amount - part1, 2)
                    for part_amount in [part1, part2]:
                        rows.append({
                            "payment_id": f"PAY-{payment_counter:05d}",
                            "vendor_id": vid,
                            "invoice_id": invoice_id,
                            "due_date": due.isoformat(),
                            "actual_payment_date": actual_payment.isoformat(),
                            "amount": part_amount,
                            "days_variance": variance,
                        })
                        payment_counter += 1
                else:
                    rows.append({
                        "payment_id": f"PAY-{payment_counter:05d}",
                        "vendor_id": vid,
                        "invoice_id": invoice_id,
                        "due_date": due.isoformat(),
                        "actual_payment_date": actual_payment.isoformat(),
                        "amount": amount,
                        "days_variance": variance,
                    })
                    payment_counter += 1

            cursor += timedelta(days=30)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written: {path}  ({len(rows)} payment records)")


# ---------------------------------------------------------------------------
# 3. open_invoices.csv  (20-30 invoices due in next 30-45 days)
# ---------------------------------------------------------------------------

def generate_open_invoices(n=25):
    path = os.path.join(DATA_DIR, "open_invoices.csv")
    fieldnames = [
        "invoice_id", "vendor_id", "vendor_name", "invoice_date", "due_date",
        "amount", "status", "cost_center", "po_number",
        "payment_terms_days", "discount_if_paid_by"
    ]

    cost_centers = ["CC-100", "CC-200", "CC-300", "CC-400"]
    rows = []

    for i in range(1, n + 1):
        vendor = random.choice(VENDORS)
        vid = vendor["vendor_id"]
        terms = vendor["payment_terms_days"]

        # Due date spread across next 5 to 45 days
        days_until_due = random.randint(5, 45)
        due_date = TODAY + timedelta(days=days_until_due)
        invoice_date = due_date - timedelta(days=terms)

        amount = round(rand_amount(vendor["avg_invoice_amount"], vendor["amount_std_dev"]), 2)

        # Discount window
        if vendor["early_pay_discount_pct"] > 0 and vendor["early_pay_discount_days"] > 0:
            discount_by = invoice_date + timedelta(days=vendor["early_pay_discount_days"])
        else:
            discount_by = ""

        rows.append({
            "invoice_id": f"INV-2025-{i:03d}",
            "vendor_id": vid,
            "vendor_name": vendor["vendor_name"],
            "invoice_date": invoice_date.isoformat(),
            "due_date": due_date.isoformat(),
            "amount": amount,
            "status": "open",
            "cost_center": random.choice(cost_centers),
            "po_number": f"PO-{random.randint(10000, 99999)}",
            "payment_terms_days": terms,
            "discount_if_paid_by": discount_by,
        })

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written: {path}  ({len(rows)} open invoices)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating simulated AP data...")
    generate_vendor_master()
    generate_payment_history(months=12)
    generate_open_invoices(n=25)
    print("Done. Data files are in data/")
