"""
Reporting Agent
Compiles forecast and risk data into a structured CFO-ready report.
"""

from graph.state import APForecastState
from tools.chart_generator_tool import generate_chart
from tools.report_writer_tool import write_report
import config


def reporting_agent(state: APForecastState) -> APForecastState:
    """
    LangGraph node: generates the cash flow chart and writes the markdown report.
    Calls tools as plain functions to avoid LangGraph deepcopy/serialization conflicts.
    """
    chart_path = generate_chart(
        forecast_schedule=state["forecast_schedule"],
        output_path=config.CHART_OUTPUT_PATH,
    )
    print(f"[Reporting Agent] Chart saved: {chart_path}")

    report_path = write_report(
        forecast_schedule=state["forecast_schedule"],
        risk_flags=state["risk_flags"],
        discount_opportunities=state["discount_opportunities"],
        chart_path=chart_path,
        output_path=config.REPORT_OUTPUT_PATH,
    )
    print(f"[Reporting Agent] Report saved: {report_path}")

    return {
        **state,
        "chart_path": chart_path,
        "report_path": report_path,
    }
