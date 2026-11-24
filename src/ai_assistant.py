"""AI planning assistant: drafts the weekly planning memo from the KPI tables.

Run:  python src/ai_assistant.py --dry-run   saves the prompt to outputs/ai_prompt.txt (paste it into Claude, free)
      python src/ai_assistant.py             sends it to the Claude API
"""

import os, sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

# What the AI must do (it may only use our numbers, never invent its own)
INSTRUCTIONS = """You are a senior material planner at an FMCG manufacturer.
Write a short weekly planning memo for the Production and Procurement teams.
Rules: use ONLY the numbers in the tables; never invent figures; label guesses "Possible cause".
Structure: 1) Headline (2 sentences) 2) Top 5 actions with product, number and owner
3) Forecast watch-list 4) Questions for Sales or the plant. Under 350 words, plain English."""

# Read the results from the notebooks
inv = pd.read_csv(OUT / "inventory_health.csv")
acc = pd.read_csv(OUT / "forecast_accuracy_by_product.csv")
anomalies = pd.read_csv(OUT / "demand_anomalies.csv")
flows = pd.read_csv(OUT / "daily_flows.csv")
fill_rate = flows["delivered_units"].sum() / flows["ordered_units"].sum() * 100

# Keep only what needs attention
at_risk = inv[inv["risk"] != "Healthy"][["product", "segment", "risk", "fill_rate_pct",
                                         "production_vs_orders_pct", "avg_stock_28d", "safety_stock",
                                         "days_of_cover", "lead_time_days"]]
watch_list = acc[acc["flag"] != "OK"][["product", "actual_units", "wape_pct", "bias_pct", "flag"]].head(10)

# Put it all into one message for the AI
prompt = (f"Network fill rate Jan-Aug 2023: {fill_rate:.1f}%. Active products: {len(inv)}, "
          f"healthy: {(inv['risk'] == 'Healthy').sum()}.\n\n"
          f"PRODUCTS AT RISK:\n{at_risk.to_string(index=False)}\n\n"
          f"FORECAST WATCH-LIST (blend forecast, last 4 weeks):\n{watch_list.to_string(index=False)}\n\n"
          f"BIGGEST DEMAND ANOMALIES (Isolation Forest):\n{anomalies.head(10).to_string(index=False)}\n\n"
          "Write the memo.")
(OUT / "ai_prompt.txt").write_text(INSTRUCTIONS + "\n\n" + prompt, encoding="utf-8")

load_dotenv()
if "--dry-run" in sys.argv or not os.getenv("ANTHROPIC_API_KEY"):
    print("Prompt saved to outputs/ai_prompt.txt. Paste it into Claude to get the memo.")
else:
    import anthropic                                     # only needed when calling the API
    reply = anthropic.Anthropic().messages.create(
        model="claude-sonnet-5-5", max_tokens=1200, system=INSTRUCTIONS,
        messages=[{"role": "user", "content": prompt}])
    memo = "# Weekly planning memo (AI draft, reviewed by the planner)\n\n" + reply.content[0].text
    (ROOT / "ai_memo_example.md").write_text(memo, encoding="utf-8")
    print(memo)