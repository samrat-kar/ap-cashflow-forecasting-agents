"""Tests for the Forecasting tools."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from tools.forecast_calculator_tool import forecast_calculator_tool
from tools.payment_pattern_tool import payment_pattern_tool


def test_forecast_covers_30_day_window():
    today = date.today()
    invoices = [
        {
            "invoice_id": f"INV-00{i}",
            "vendor_id": "V001",
            "due_date": (today + timedelta(days=i * 5)).isoformat(),
            "amount": str(1000 * i),
        }
        for i in range(1, 6)
    ]
    patterns = {"V001": 0.0}
    schedule = forecast_calculator_tool.invoke({
        "open_invoices": invoices,
        "vendor_payment_patterns": patterns,
        "forecast_horizon_days": 30,
    })
    assert len(schedule) >= 4
    for day in schedule:
        d = date.fromisoformat(day["date"])
        assert today <= d <= today + timedelta(days=30)


def test_forecast_adjusts_for_late_vendor():
    today = date.today()
    due = today + timedelta(days=5)
    invoices = [{"invoice_id": "INV-001", "vendor_id": "V002", "due_date": due.isoformat(), "amount": "2000"}]
    # Vendor typically pays 3 days late → expected date = due + 3
    patterns = {"V002": 3.0}
    schedule = forecast_calculator_tool.invoke({
        "open_invoices": invoices,
        "vendor_payment_patterns": patterns,
        "forecast_horizon_days": 30,
    })
    assert len(schedule) == 1
    expected_date = (due + timedelta(days=3)).isoformat()
    assert schedule[0]["date"] == expected_date
