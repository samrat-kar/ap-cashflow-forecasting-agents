"""
Forecasting Agent
Projects cash outflows over the next 30 days using historical payment patterns.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import APForecastState
from tools.payment_pattern_tool import payment_pattern_tool
from tools.forecast_calculator_tool import forecast_calculator_tool
import config


def forecasting_agent(state: APForecastState) -> APForecastState:
    """
    LangGraph node: calculates vendor payment patterns and builds a 30-day forecast.
    """
    llm = ChatAnthropic(model=config.MODEL_NAME, temperature=0)

    # Step 1: Calculate vendor payment patterns (deterministic)
    patterns = payment_pattern_tool.invoke({
        "payment_history": state["payment_history"]
    })

    # Step 2: Build forecast schedule (deterministic)
    forecast = forecast_calculator_tool.invoke({
        "open_invoices": state["open_invoices"],
        "vendor_payment_patterns": patterns,
        "forecast_horizon_days": config.FORECAST_HORIZON_DAYS,
    })

    # Step 3: LLM summarizes the forecast for logging/context
    if forecast:
        total = sum(float(d["projected_amount"]) for d in forecast)
        prompt = (
            f"You are an AP analyst. Here is a 30-day cash flow forecast summary:\n"
            f"- Total projected outflow: ${total:,.0f}\n"
            f"- Days with scheduled payments: {len(forecast)}\n"
            f"- Vendor payment patterns (avg days variance): {patterns}\n\n"
            "Write a 2-sentence briefing on what the finance team should know."
        )
        briefing = llm.invoke([
            SystemMessage(content="You are a helpful AP cash flow analyst."),
            HumanMessage(content=prompt),
        ]).content
        print(f"[Forecasting Agent] Briefing:\n{briefing}")

    return {
        **state,
        "vendor_payment_patterns": patterns,
        "forecast_schedule": forecast,
    }
