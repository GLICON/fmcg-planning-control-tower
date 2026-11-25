# AI use: what I considered

I added an AI step to this project to draft the weeekly planning memo. Before building it, I asked myself:
*how would a planner use AI safely if this were a real company's data?* This page explains the choices I made.

## Why use AI here
Turning the KPI tables into a clear memo for Production and Procurement can take a planner 1-2 hours a week.
AI can draft it in seconds. The analysiis itself (forecasts, safety stock, risk flags) is done by my code, not by AI.
AI only writes the explanation.

## 1. Send as little data as possible
SupplyGraph is public data, but I treated it as if it were confidential.
- The AI receives only **summary KPIs**: the 8 products needing attention, the forecast watch-list and the 10 largest demand anomalies (about 30 rows).
- No raw transactions, customer or supplier names, prices or personal data are ever sent.

## 2. Use only an approved tool
- In a company I would only use an AI service approved by IT and data governance, on a business account
  (for example Claude through AWS Bedrock), never a personal account.
- The API key is kept in `.env`, which is never commmitted. In production it would move to a secrets manager.

## 3. Stop the AI inventing numbers
- The instructions tell the AI to use only the numbers it is given, never invent figures and label any guess as "Possible cause".

## 4. A person checks before anything is shared
- The AI output is saved as a **draft** (`outputs/ai_memo_draft.md`).
- I check every figure against `outputs/inventory_health.csv`, then save the approved memo
  as `ai_memo_example.md` with a reviewer's note.
- The AI never changes plans, orders or SAP data by itself.

## 5. Keep a record
- Every API call is logged in `outputs/ai_usage_log.csv`: time, model, amount of data sent and received, and who reviewed it.

## 6. It works without AI
- `python src/ai_assistant.py --dry-run` sends nothing. It saves the prompt so a planner can use an approved tool or write the memo by hand. Everything else in the project runs without AI.

## Data protection
- In the UK, personal data is covered by UK GDPR. I would nevr put personal data in a prompt, and I would check where an AI service processes and stores data before using it with company information.

