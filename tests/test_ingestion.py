"""Integration-style tests for the Data Ingestion Agent."""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.csv_loader_tool import csv_loader_tool
from tools.data_validation_tool import data_validation_tool
import config


@pytest.mark.skipif(
    not os.path.exists(config.INVOICES_PATH),
    reason="Data files not generated — run python data/generate_data.py first"
)
def test_csv_loader_reads_invoices():
    rows = csv_loader_tool.invoke({"file_path": config.INVOICES_PATH})
    assert isinstance(rows, list)
    assert len(rows) > 0
    assert "invoice_id" in rows[0]


@pytest.mark.skipif(
    not os.path.exists(config.VENDORS_PATH),
    reason="Data files not generated"
)
def test_generated_data_passes_validation():
    invoices = csv_loader_tool.invoke({"file_path": config.INVOICES_PATH})
    history  = csv_loader_tool.invoke({"file_path": config.HISTORY_PATH})
    vendors  = csv_loader_tool.invoke({"file_path": config.VENDORS_PATH})

    issues = data_validation_tool.invoke({
        "invoices": invoices,
        "payment_history": history,
        "vendors": vendors,
    })
    critical = [i for i in issues if "Missing required field" in i]
    assert critical == [], f"Critical validation errors: {critical}"
