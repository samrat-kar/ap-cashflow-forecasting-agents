"""Tests for risk assessment tools."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from tools.discount_opportunity_tool import discount_opportunity_tool
from tools.late_penalty_tool import late_penalty_tool
from tools.cash_gap_tool import cash_gap_tool


def test_discount_savings_calculation():
    today = date.today()
    invoices = [{"invoice_id": "INV-X", "vendor_id": "V001", "vendor_name": "Acme", "amount": "10000", "discount_if_paid_by": (today + timedelta(days=1)).isoformat()}]
    vendors = [{"vendor_id": "V001", "early_pay_discount_pct": "0.02", "early_pay_discount_days": "10"}]
    result = discount_opportunity_tool.invoke({"open_invoices": invoices, "vendor_master": vendors, "window_days": 3})
    assert result[0]["potential_savings"] == 200.0


def test_cash_gap_excess_calculation():
    forecast = [{"date": "2025-05-01", "projected_amount": "18000", "invoice_ids": []}]
    flags = cash_gap_tool.invoke({"forecast_schedule": forecast, "cash_threshold": 15000.0})
    assert flags[0]["excess"] == 3000.0


def test_late_penalty_risk_level_medium():
    invoices = [{"invoice_id": "INV-M", "vendor_id": "V004", "vendor_name": "OfficePro", "amount": "2000", "due_date": date.today().isoformat()}]
    vendors  = [{"vendor_id": "V004", "reliability_score": "0.75", "late_fee_pct": "0.01"}]
    flags = late_penalty_tool.invoke({"open_invoices": invoices, "vendor_master": vendors, "reliability_threshold": 0.80, "amount_threshold": 500.0})
    assert flags[0]["risk_level"] == "MEDIUM"
