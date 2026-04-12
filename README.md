# AP Cash Flow Forecasting Multi-Agent System

A multi-agent AI system that forecasts upcoming Accounts Payable (AP) cash outflows for a fintech company. The system ingests open invoice data and historical payment records, learns vendor payment behavior, and produces actionable 30-day cash flow forecasts with risk alerts and CFO-ready reports.

Built as a submission for the **Mastering AI Agents Certification Program** by ReadyTensor.

## Links

- Publication: [AP Cash Flow Forecasting Multi-Agent System](https://app.readytensor.ai/publications/ap-cash-flow-forecasting-multi-agent-system-OVrtAS68NZ4k)

---

## Demo Output

**Executive Summary (sample run)**
- Total projected outflows (30 days): **$100,702**
- Largest single-day exposure: **$13,240** on 2026-04-05
- Early payment discount opportunities: **1 alert** (potential savings: $123.65)
- High-risk late payment flags: **3 alerts**

![30-Day Cash Flow Forecast](output/cashflow_chart.png)

---

## Architecture

```
START
  │
  ▼
[Data Ingestion Agent]  ──── loads & validates vendors.csv, open_invoices.csv, payment_history.csv
  │ data valid?
  ├── No  ──► [Error Node] ──► END
  └── Yes
  ▼
[Forecasting Agent]  ──── calculates vendor payment patterns, builds 30-day forecast
  │
  ▼
[Risk Assessment Agent]  ──── flags discount windows, late payment risks, cash spikes
  │
  ▼
[Human-in-the-Loop]  ──── (optional) user approves forecast before report is generated
  │ approved?
  ├── No  ──► END
  └── Yes
  ▼
[Reporting Agent]  ──── generates markdown report + cash flow chart PNG
  │
  ▼
END  (output/forecast_report.md + output/cashflow_chart.png)
```

### Agents

| Agent | Role | Tools Used |
|---|---|---|
| Data Ingestion | Load, validate, and clean CSV data | `csv_loader_tool`, `data_validation_tool` |
| Forecasting | Project 30-day cash outflows from vendor payment patterns | `payment_pattern_tool`, `forecast_calculator_tool` |
| Risk Assessment | Flag risks and discount opportunities | `discount_opportunity_tool`, `late_penalty_tool`, `cash_gap_tool` |
| Reporting | Generate chart and markdown report | `chart_generator_tool`, `report_writer_tool` |

### Shared State

All agents communicate through a typed `APForecastState` object managed by LangGraph:

```python
class APForecastState(TypedDict):
    open_invoices: list[dict]
    payment_history: list[dict]
    vendor_master: list[dict]
    data_quality_issues: list[str]
    vendor_payment_patterns: dict       # vendor_id -> avg_days_variance
    forecast_schedule: list[dict]       # [{date, projected_amount, invoice_ids}]
    risk_flags: list[dict]
    discount_opportunities: list[dict]
    report_path: str
    chart_path: str
    human_approved: bool
```

---

## Tech Stack

| Library | Purpose |
|---|---|
| `langgraph` | Agent orchestration (state graph) |
| `langchain-anthropic` | Claude LLM integration |
| `langchain-core` | `@tool` decorator for tools |
| `matplotlib` | Cash flow bar chart |
| `python-dotenv` | Environment variable management |
| `pytest` | Unit and integration tests |

**LLM:** Claude (`claude-sonnet-4-6`) — used by agents for reasoning and summarization. Tools are pure Python (no LLM inside tools).

---

## Project Structure

```
ap-cashflow-agent/
├── README.md
├── requirements.txt
├── .env.example                      ← copy to .env and add your API key
├── config.py                         ← all configurable parameters
├── main.py                           ← entry point
├── data/
│   └── generate_data.py              ← generates all 3 CSV files
├── agents/
│   ├── ingestion_agent.py
│   ├── forecasting_agent.py
│   ├── risk_agent.py
│   └── reporting_agent.py
├── tools/
│   ├── csv_loader_tool.py
│   ├── data_validation_tool.py
│   ├── payment_pattern_tool.py
│   ├── forecast_calculator_tool.py
│   ├── discount_opportunity_tool.py
│   ├── late_penalty_tool.py
│   ├── cash_gap_tool.py
│   ├── chart_generator_tool.py
│   └── report_writer_tool.py
├── graph/
│   ├── state.py                      ← APForecastState TypedDict
│   └── workflow.py                   ← LangGraph state graph definition
├── output/                           ← generated report and chart (git-ignored)
└── tests/
    ├── test_tools.py
    ├── test_ingestion.py
    ├── test_forecasting.py
    └── test_risk.py
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/samrat-kar/ap-cashflow-forecasting-agents
cd ap-cashflow-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_key_here
```

### 5. Generate simulated data

```bash
python data/generate_data.py
```

This creates `data/vendors.csv`, `data/open_invoices.csv`, and `data/payment_history.csv`.

### 6. Run the pipeline

```bash
python main.py
```

The system will:
1. Load and validate the AP data
2. Compute vendor payment patterns
3. Build a 30-day forecast
4. Identify risks and discount opportunities
5. Ask for your approval (human-in-the-loop)
6. Generate `output/forecast_report.md` and `output/cashflow_chart.png`

### 7. Run tests

```bash
pytest tests/ -v
```

---

## Configuration

All parameters are in `.env` (or `config.py` for defaults):

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Your Anthropic API key (required) |
| `MODEL_NAME` | `claude-sonnet-4-6` | Claude model to use |
| `FORECAST_HORIZON_DAYS` | `30` | Days to forecast ahead |
| `DISCOUNT_WINDOW_DAYS` | `3` | Days remaining to flag discount windows |
| `CASH_THRESHOLD` | `15000` | Daily outflow spike threshold ($) |
| `RELIABILITY_THRESHOLD` | `0.80` | Vendor reliability below this = high risk |
| `LARGE_INVOICE_THRESHOLD` | `1000` | Invoice above this + risky vendor = flag |
| `ENABLE_HUMAN_APPROVAL` | `true` | Set to `false` to skip human review step |

---

## Certification Requirements

| Requirement | Implementation |
|---|---|
| Minimum 3 agents with distinct roles | 4 agents (Ingestion, Forecasting, Risk, Reporting) |
| Clear agent communication/coordination | LangGraph shared `APForecastState` |
| Orchestration framework | LangGraph `StateGraph` |
| Minimum 3 tools | 9 tools across all agents |
| Human-in-the-loop | Approval step before report generation |
| Clean GitHub repo with setup instructions | This README |

---

## License

[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
