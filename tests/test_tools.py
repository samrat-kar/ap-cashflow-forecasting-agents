"""Unit tests for all tools."""

import pytest
from datetime import date, timedelta

# Add project root to path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.payment_pattern_tool import payment_pattern_tool
from tools.forecast_calculator_tool import forecast_calculator_tool
from tools.discount_opportunity_tool import discount_opportunity_tool
from tools.late_penalty_tool import late_penalty_tool
from tools.cash_gap_tool import cash_gap_tool
from tools.data_validation_tool import data_validation_tool


# ---------------------------------------------------------------------------
# payment_pattern_tool
# ---------------------------------------------------------------------------

def test_payment_pattern_tool_calculates_mean_variance():
    history = [
        {"vendor_id": "V001", "days_variance": "2"},
        {"vendor_id": "V001", "days_variance": "-1"},
        {"vendor_id": "V001", "days_variance": "3"},
    ]
    result = payment_pattern_tool.invoke({"payment_history": history})
    assert result["V001"] == pytest.approx(1.33, rel=0.01)


def test_payment_pattern_tool_multiple_vendors():
    history = [
        {"vendor_id": "V001", "days_variance": "0"},
        {"vendor_id": "V002", "days_variance": "5"},
        {"vendor_id": "V002", "days_variance": "7"},
    ]
    result = payment_pattern_tool.invoke({"payment_history": history})
    assert result["V001"] == 0.0
    assert result["V002"] == 6.0


def test_payment_pattern_tool_ignores_bad_rows():
    history = [
        {"vendor_id": "V001", "days_variance": "2"},
        {"vendor_id": "V001", "days_variance": "bad"},
        {"vendor_id": "V001", "days_variance": "4"},
    ]
    result = payment_pattern_tool.invoke({"payment_history": history})
    assert result["V001"] == pytest.approx(3.0, rel=0.01)


# ---------------------------------------------------------------------------
# discount_opportunity_tool
# ---------------------------------------------------------------------------

def test_discount_opportunity_tool_flags_closing_windows():
    today = date.today()
    invoices = [{
        "invoice_id": "INV-001",
        "vendor_id": "V001",
        "vendor_name": "Acme",
        "amount": "5000",
        "discount_if_paid_by": (today + timedelta(days=2)).isoformat(),
    }]
    vendors = [{
        "vendor_id": "V001",
        "vendor_name": "Acme",
        "early_pay_discount_pct": "0.02",
        "early_pay_discount_days": "10",
    }]
    flags = discount_opportunity_tool.invoke({
        "open_invoices": invoices,
        "vendor_master": vendors,
        "window_days": 3,
    })
    assert len(flags) == 1
    assert flags[0]["invoice_id"] == "INV-001"
    assert flags[0]["potential_savings"] == pytest.approx(100.0)


def test_discount_opportunity_tool_ignores_expired_windows():
    today = date.today()
    invoices = [{
        "invoice_id": "INV-002",
        "vendor_id": "V001",
        "vendor_name": "Acme",
        "amount": "5000",
        "discount_if_paid_by": (today - timedelta(days=1)).isoformat(),
    }]
    vendors = [{"vendor_id": "V001", "early_pay_discount_pct": "0.02", "early_pay_discount_days": "10"}]
    flags = discount_opportunity_tool.invoke({
        "open_invoices": invoices,
        "vendor_master": vendors,
        "window_days": 3,
    })
    assert len(flags) == 0


# ---------------------------------------------------------------------------
# data_validation_tool
# ---------------------------------------------------------------------------

def test_data_validation_tool_catches_missing_due_date():
    invoices = [{"invoice_id": "INV-001", "vendor_id": "V001", "amount": "100"}]
    issues = data_validation_tool.invoke({
        "invoices": invoices,
        "payment_history": [],
        "vendors": [],
    })
    assert any("due_date" in issue for issue in issues)


def test_data_validation_tool_catches_negative_amount():
    invoices = [{
        "invoice_id": "INV-001",
        "vendor_id": "V001",
        "due_date": date.today().isoformat(),
        "amount": "-500",
    }]
    issues = data_validation_tool.invoke({
        "invoices": invoices,
        "payment_history": [],
        "vendors": [],
    })
    assert any("Negative" in issue for issue in issues)


def test_data_validation_tool_passes_clean_data():
    today = date.today().isoformat()
    invoices = [{"invoice_id": "INV-001", "vendor_id": "V001", "due_date": today, "amount": "500"}]
    vendors  = [{"vendor_id": "V001", "vendor_name": "Acme", "payment_terms_days": "30", "reliability_score": "0.9"}]
    issues = data_validation_tool.invoke({
        "invoices": invoices,
        "payment_history": [],
        "vendors": vendors,
    })
    assert issues == []


# ---------------------------------------------------------------------------
# cash_gap_tool
# ---------------------------------------------------------------------------

def test_cash_gap_tool_flags_high_days():
    forecast = [
        {"date": "2025-04-01", "projected_amount": "20000", "invoice_ids": []},
        {"date": "2025-04-02", "projected_amount": "5000",  "invoice_ids": []},
    ]
    flags = cash_gap_tool.invoke({"forecast_schedule": forecast, "cash_threshold": 15000.0})
    assert len(flags) == 1
    assert flags[0]["date"] == "2025-04-01"
    assert flags[0]["excess"] == 5000.0


def test_cash_gap_tool_returns_empty_when_no_spikes():
    forecast = [
        {"date": "2025-04-01", "projected_amount": "3000", "invoice_ids": []},
    ]
    flags = cash_gap_tool.invoke({"forecast_schedule": forecast, "cash_threshold": 15000.0})
    assert flags == []


# ---------------------------------------------------------------------------
# late_penalty_tool
# ---------------------------------------------------------------------------

def test_late_penalty_tool_flags_high_risk_vendors():
    invoices = [{
        "invoice_id": "INV-001",
        "vendor_id": "V007",
        "vendor_name": "Rapid Courier",
        "amount": "2000",
        "due_date": date.today().isoformat(),
    }]
    vendors = [{
        "vendor_id": "V007",
        "vendor_name": "Rapid Courier",
        "reliability_score": "0.65",
        "late_fee_pct": "0.008",
    }]
    flags = late_penalty_tool.invoke({
        "open_invoices": invoices,
        "vendor_master": vendors,
        "reliability_threshold": 0.80,
        "amount_threshold": 1000.0,
    })
    assert len(flags) == 1
    assert flags[0]["risk_level"] == "HIGH"


def test_late_penalty_tool_ignores_reliable_vendors():
    invoices = [{
        "invoice_id": "INV-002",
        "vendor_id": "V001",
        "vendor_name": "Acme",
        "amount": "5000",
        "due_date": date.today().isoformat(),
    }]
    vendors = [{"vendor_id": "V001", "reliability_score": "0.95", "late_fee_pct": "0.015"}]
    flags = late_penalty_tool.invoke({
        "open_invoices": invoices,
        "vendor_master": vendors,
        "reliability_threshold": 0.80,
        "amount_threshold": 1000.0,
    })
    assert flags == []
