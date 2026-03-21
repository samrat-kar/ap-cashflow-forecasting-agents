"""Centralized configuration for the AP Cash Flow Forecasting system."""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM
MODEL_NAME = os.getenv("MODEL_NAME", "claude-sonnet-4-6")

# Data paths
DATA_DIR          = os.path.join(os.path.dirname(__file__), "data")
VENDORS_PATH      = os.path.join(DATA_DIR, "vendors.csv")
INVOICES_PATH     = os.path.join(DATA_DIR, "open_invoices.csv")
HISTORY_PATH      = os.path.join(DATA_DIR, "payment_history.csv")

# Output paths
OUTPUT_DIR         = os.path.join(os.path.dirname(__file__), "output")
REPORT_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "forecast_report.md")
CHART_OUTPUT_PATH  = os.path.join(OUTPUT_DIR, "cashflow_chart.png")

# Forecast parameters
FORECAST_HORIZON_DAYS   = int(os.getenv("FORECAST_HORIZON_DAYS", "30"))
DISCOUNT_WINDOW_DAYS    = int(os.getenv("DISCOUNT_WINDOW_DAYS", "3"))
CASH_THRESHOLD          = float(os.getenv("CASH_THRESHOLD", "15000"))
RELIABILITY_THRESHOLD   = float(os.getenv("RELIABILITY_THRESHOLD", "0.80"))
LARGE_INVOICE_THRESHOLD = float(os.getenv("LARGE_INVOICE_THRESHOLD", "1000"))

# Human-in-the-loop
ENABLE_HUMAN_APPROVAL = os.getenv("ENABLE_HUMAN_APPROVAL", "true").lower() == "true"
