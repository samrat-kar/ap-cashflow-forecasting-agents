"""
LangGraph workflow — wires the 4 agents into a state graph.

Flow:
  START
    -> ingestion_agent
      -> (data valid?) -> forecasting_agent
      -> (data invalid?) -> error_node
    -> forecasting_agent
    -> risk_agent
    -> (human approval enabled?) -> human_review_node
    -> reporting_agent
    -> END
"""

from langgraph.graph import StateGraph, END
from graph.state import APForecastState
from agents.ingestion_agent import ingestion_agent
from agents.forecasting_agent import forecasting_agent
from agents.risk_agent import risk_agent
from agents.reporting_agent import reporting_agent
import config


# ---------------------------------------------------------------------------
# Extra nodes
# ---------------------------------------------------------------------------

def error_node(state: APForecastState) -> APForecastState:
    """Terminal node when data validation fails."""
    issues = state.get("data_quality_issues", [])
    print("\n[ERROR] Data validation failed. Pipeline stopped.")
    print("Issues found:")
    for issue in issues:
        print(f"  - {issue}")
    return state


def human_review_node(state: APForecastState) -> APForecastState:
    """
    Human-in-the-loop: shows forecast summary and asks for approval.
    Sets human_approved = True/False in state.
    """
    forecast = state.get("forecast_schedule", [])
    total = sum(float(d["projected_amount"]) for d in forecast)

    print("\n" + "="*60)
    print("HUMAN REVIEW REQUIRED")
    print("="*60)
    print(f"Total 30-day projected outflow: ${total:,.0f}")
    print(f"Payment days in forecast: {len(forecast)}")
    print(f"Risk flags: {len(state.get('risk_flags', []))}")
    print(f"Discount opportunities: {len(state.get('discount_opportunities', []))}")
    print("="*60)

    answer = input("Approve forecast and generate report? [y/N]: ").strip().lower()
    approved = answer == "y"

    if not approved:
        print("[Human Review] Report generation cancelled.")

    return {**state, "human_approved": approved}


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def route_after_ingestion(state: APForecastState) -> str:
    """Route to error node if critical data issues exist, else proceed."""
    issues = state.get("data_quality_issues", [])
    # Only hard-stop on missing required fields; warn on other issues
    critical = [i for i in issues if "Missing required field" in i]
    return "error" if critical else "forecast"


def route_after_human_review(state: APForecastState) -> str:
    return "report" if state.get("human_approved", False) else END


# ---------------------------------------------------------------------------
# Build the graph
# ---------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(APForecastState)

    graph.add_node("ingestion", ingestion_agent)
    graph.add_node("forecast",  forecasting_agent)
    graph.add_node("risk",      risk_agent)
    graph.add_node("report",    reporting_agent)
    graph.add_node("error",     error_node)

    graph.set_entry_point("ingestion")

    graph.add_conditional_edges(
        "ingestion",
        route_after_ingestion,
        {"forecast": "forecast", "error": "error"},
    )
    graph.add_edge("forecast", "risk")

    if config.ENABLE_HUMAN_APPROVAL:
        graph.add_node("human_review", human_review_node)
        graph.add_edge("risk", "human_review")
        graph.add_conditional_edges(
            "human_review",
            route_after_human_review,
            {"report": "report", END: END},
        )
    else:
        graph.add_edge("risk", "report")

    graph.add_edge("report", END)
    graph.add_edge("error", END)

    return graph.compile()
