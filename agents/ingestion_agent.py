"""
Data Ingestion Agent
Loads, validates, and cleans raw AP data from CSV files.
"""

import os
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import APForecastState
from tools.csv_loader_tool import csv_loader_tool
from tools.data_validation_tool import data_validation_tool
import config


def ingestion_agent(state: APForecastState) -> APForecastState:
    """
    LangGraph node: loads all three CSV files, validates data,
    and populates shared state with cleaned records.
    """
    llm = ChatAnthropic(model=config.MODEL_NAME, temperature=0)

    # Load data using tools (deterministic — no LLM needed here)
    invoices = csv_loader_tool.invoke({"file_path": config.INVOICES_PATH})
    history  = csv_loader_tool.invoke({"file_path": config.HISTORY_PATH})
    vendors  = csv_loader_tool.invoke({"file_path": config.VENDORS_PATH})

    # Validate
    issues = data_validation_tool.invoke({
        "invoices": invoices,
        "payment_history": history,
        "vendors": vendors,
    })

    if issues:
        # Let the LLM summarize the data quality problems
        prompt = (
            "You are a data quality analyst. The following issues were found in the AP data.\n"
            "Summarize them concisely for a finance team:\n\n"
            + "\n".join(issues)
        )
        summary = llm.invoke([
            SystemMessage(content="You are a helpful AP data quality analyst."),
            HumanMessage(content=prompt),
        ]).content
        print(f"[Ingestion Agent] Data quality issues found:\n{summary}")

    return {
        **state,
        "open_invoices": invoices,
        "payment_history": history,
        "vendor_master": vendors,
        "data_quality_issues": issues,
    }
