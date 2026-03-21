"""
main.py — Entry point for the AP Cash Flow Forecasting Multi-Agent System.

Usage:
    python main.py
"""

import os
import sys

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.workflow import build_graph
from graph.state import APForecastState


def main():
    print("="*60)
    print("AP Cash Flow Forecasting Multi-Agent System")
    print("="*60)

    # Check data files exist
    from config import VENDORS_PATH, INVOICES_PATH, HISTORY_PATH
    for path in [VENDORS_PATH, INVOICES_PATH, HISTORY_PATH]:
        if not os.path.exists(path):
            print(f"\n[ERROR] Missing data file: {path}")
            print("Run 'python data/generate_data.py' first.")
            sys.exit(1)

    # Initial state (empty — agents will populate it)
    initial_state: APForecastState = {
        "open_invoices": [],
        "payment_history": [],
        "vendor_master": [],
        "data_quality_issues": [],
        "vendor_payment_patterns": {},
        "forecast_schedule": [],
        "risk_flags": [],
        "discount_opportunities": [],
        "report_path": "",
        "chart_path": "",
        "human_approved": False,
    }

    graph = build_graph()

    print("\nRunning pipeline...\n")
    final_state = graph.invoke(initial_state)

    report = final_state.get("report_path")
    chart  = final_state.get("chart_path")

    if report and os.path.exists(report):
        print(f"\n{'='*60}")
        print(f"Pipeline complete!")
        print(f"  Report: {report}")
        print(f"  Chart:  {chart}")
        print(f"{'='*60}")
    else:
        print("\nPipeline finished (no report generated).")


if __name__ == "__main__":
    main()
