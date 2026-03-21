"""
Risk Assessment Agent
Identifies financial risks and opportunities in the AP forecast.
"""

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from graph.state import APForecastState
from tools.discount_opportunity_tool import discount_opportunity_tool
from tools.late_penalty_tool import late_penalty_tool
from tools.cash_gap_tool import cash_gap_tool
import config


def risk_agent(state: APForecastState) -> APForecastState:
    """
    LangGraph node: runs all three risk tools and summarizes findings via LLM.
    """
    llm = ChatAnthropic(model=config.MODEL_NAME, temperature=0)

    # Deterministic risk checks
    discounts = discount_opportunity_tool.invoke({
        "open_invoices": state["open_invoices"],
        "vendor_master": state["vendor_master"],
        "window_days": config.DISCOUNT_WINDOW_DAYS,
    })

    late_risks = late_penalty_tool.invoke({
        "open_invoices": state["open_invoices"],
        "vendor_master": state["vendor_master"],
        "reliability_threshold": config.RELIABILITY_THRESHOLD,
        "amount_threshold": config.LARGE_INVOICE_THRESHOLD,
    })

    cash_gaps = cash_gap_tool.invoke({
        "forecast_schedule": state["forecast_schedule"],
        "cash_threshold": config.CASH_THRESHOLD,
    })

    # LLM summarizes all risk findings
    all_flags = late_risks + cash_gaps
    prompt_parts = ["You are an AP risk analyst. Summarize these risks for the CFO in 3 bullet points:\n"]
    if late_risks:
        prompt_parts.append(f"Late payment risks ({len(late_risks)}): {[f['invoice_id'] for f in late_risks]}")
    if cash_gaps:
        prompt_parts.append(f"Cash gap alerts ({len(cash_gaps)}): dates {[g['date'] for g in cash_gaps]}")
    if discounts:
        prompt_parts.append(f"Discount opportunities ({len(discounts)}): potential savings ${sum(d['potential_savings'] for d in discounts):,.2f}")
    if not (late_risks or cash_gaps or discounts):
        prompt_parts.append("No significant risks detected.")

    summary = llm.invoke([
        SystemMessage(content="You are a helpful AP risk analyst."),
        HumanMessage(content="\n".join(prompt_parts)),
    ]).content
    print(f"[Risk Agent] Risk Summary:\n{summary}")

    return {
        **state,
        "risk_flags": all_flags,
        "discount_opportunities": discounts,
    }
