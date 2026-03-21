"""Shared LangGraph state schema for the AP Cash Flow Forecasting system."""

from typing import TypedDict


class APForecastState(TypedDict):
    open_invoices: list[dict]
    payment_history: list[dict]
    vendor_master: list[dict]
    data_quality_issues: list[str]
    vendor_payment_patterns: dict          # vendor_id -> avg_days_variance
    forecast_schedule: list[dict]          # [{date, projected_amount, invoice_ids}]
    risk_flags: list[dict]
    discount_opportunities: list[dict]
    report_path: str
    chart_path: str
    human_approved: bool
