"""chart_generator_tool — produces a 30-day bar chart of projected daily outflows."""

import os
from langchain_core.tools import tool


def generate_chart(forecast_schedule: list[dict], output_path: str = "output/cashflow_chart.png") -> str:
    """
    Generate a bar chart of 30-day projected daily cash outflows using matplotlib.
    Saves the chart as a PNG and returns the file path.
    """
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import date

    dates = [date.fromisoformat(d["date"]) for d in forecast_schedule]
    amounts = [float(d["projected_amount"]) for d in forecast_schedule]

    fig, ax = plt.subplots(figsize=(14, 6))
    bars = ax.bar(dates, amounts, color="#4C72B0", edgecolor="white", linewidth=0.5)

    # Highlight bars above $15k
    for bar, amount in zip(bars, amounts):
        if amount > 15000:
            bar.set_color("#DD4444")

    ax.set_title("30-Day AP Cash Flow Forecast", fontsize=16, fontweight="bold", pad=15)
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Projected Outflow ($)", fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.xticks(rotation=45, ha="right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.grid(axis="y", alpha=0.3)

    total = sum(amounts)
    ax.annotate(
        f"Total 30-day exposure: ${total:,.0f}",
        xy=(0.02, 0.95), xycoords="axes fraction",
        fontsize=10, color="#333333",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f0f0f0", alpha=0.8)
    )

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close("all")

    return output_path


@tool
def chart_generator_tool(
    forecast_schedule: list[dict],
    output_path: str = "output/cashflow_chart.png",
) -> str:
    """
    Generate a bar chart of 30-day projected daily cash outflows using matplotlib.
    Saves the chart as a PNG and returns the file path.
    """
    return generate_chart(forecast_schedule, output_path)
