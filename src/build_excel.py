"""Build the Excel planning workbook."""

from pathlib import Path
import pandas as pd
from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]               # the project folder
inv = pd.read_csv(ROOT / "outputs" / "inventory_health.csv").sort_values(["abc", "product"])
YELLOW = PatternFill("solid", fgColor="FFFF00")          # yellow = a setting you can change

wb = Workbook()
ws = wb.active
ws.title = "Planning Table"

# Settings used by the formulas (change them in Excel and everything updates)
ws["A1"] = "Weekly planning table"; ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = "Blue = data from the pipeline · Black = formulas · Yellow = settings you can change"
ws["A4"], ws["B4"] = "Service level", 0.95
ws["A5"], ws["B5"] = "Review period (days)", 7
ws["A6"], ws["B6"] = "Excess threshold (days of cover)", 30
ws["C4"], ws["D4"] = "z-score", "=NORMSINV(B4)"          # 95% -> 1.645
for cell in ("B4", "B5", "B6"):
    ws[cell].fill = YELLOW
ws["B4"].number_format = "0.0%"

# Header row
headers = ["Product", "Segment", "Avg daily demand", "Daily demand std dev", "Lead time (days)",
           "Current stock (4-wk avg)", "Fill rate", "Safety stock", "Reorder point",
           "Days of cover", "Suggested order", "Status"]
for col, title in enumerate(headers, start=1):
    ws.cell(8, col, title).font = Font(bold=True)

# One row per product: A-G = data (blue), H-L = Excel formulas
first = 9
for i, r in enumerate(inv.itertuples(), start=first):
    data = [r.product, r.segment, r.avg_daily_demand, r.sd_daily_demand,
            r.lead_time_days, r.avg_stock_28d, r.fill_rate_pct / 100]
    for col, value in enumerate(data, start=1):
        ws.cell(i, col, value).font = Font(color="0000FF")
    ws[f"G{i}"].number_format = "0.0%"
    ws[f"H{i}"] = f"=ROUND($D$4*D{i}*SQRT(E{i}),0)"              # safety stock
    ws[f"I{i}"] = f"=ROUND(C{i}*E{i}+H{i},0)"                     # reorder point
    ws[f"J{i}"] = f"=ROUND(F{i}/C{i},1)"                          # days of cover
    ws[f"K{i}"] = f"=MAX(0,ROUND(I{i}+C{i}*$B$5-F{i},0))"         # suggested order
    ws[f"L{i}"] = (f'=IF(G{i}<0.95,"SERVICE RISK",IF(F{i}<H{i},"BELOW SAFETY STOCK",'   # status
                   f'IF(F{i}<I{i},"REPLENISH",IF(J{i}>$B$6,"EXCESS","OK"))))')
last = first + len(inv) - 1

# Totals: total to order, and how many products need attention
ws[f"K{last + 2}"] = f"=SUM(K{first}:K{last})"
ws[f"L{last + 2}"] = (f'=COUNTIF(L{first}:L{last},"SERVICE RISK")+COUNTIF(L{first}:L{last},"BELOW SAFETY STOCK")'
                      f'+COUNTIF(L{first}:L{last},"EXCESS")&" items need attention"')

# Colour each row by its status: red = problem, amber = order soon, blue = too much stock
for status, colour in [("SERVICE RISK", "F8D7DA"), ("BELOW SAFETY STOCK", "F8D7DA"),
                       ("REPLENISH", "FFF3CD"), ("EXCESS", "DCE8F7")]:
    ws.conditional_formatting.add(f"A{first}:L{last}", FormulaRule(
        formula=[f'$L{first}="{status}"'], fill=PatternFill("solid", fgColor=colour)))
ws.auto_filter.ref = f"A8:L{last}"                       # filter buttons on the header
ws.column_dimensions["A"].width = 30

# Sheet 2: pick a product from a drop-down; INDEX/MATCH looks up its numbers
calc = wb.create_sheet("Reorder Calculator")
calc["A1"] = "Reorder calculator: choose a product in the yellow cell"
calc["A3"], calc["B3"] = "Product", inv.loc[inv["fill_rate_pct"].idxmin(), "product"]
calc["B3"].fill = YELLOW
dropdown = DataValidation(type="list", formula1=f"='Planning Table'!$A${first}:$A${last}")
calc.add_data_validation(dropdown)
dropdown.add("B3")

fields = {"Segment": "B", "Avg daily demand": "C", "Lead time (days)": "E", "Current stock": "F",
          "Safety stock": "H", "Reorder point": "I", "Days of cover": "J", "Suggested order": "K", "Status": "L"}
for row, (label, column) in enumerate(fields.items(), start=5):
    calc[f"A{row}"] = label
    calc[f"B{row}"] = (f"=INDEX('Planning Table'!{column}{first}:{column}{last},"
                       f"MATCH($B$3,'Planning Table'!A{first}:A{last},0))")
calc.column_dimensions["A"].width = 22

(ROOT / "excel").mkdir(exist_ok=True)
wb.save(ROOT / "excel" / "planning_workbook.xlsx")
print(f"Saved excel/planning_workbook.xlsx ({len(inv)} products)")