"""
build_dashboard_json.py
-------------------------
Queries every view in procurement.db and writes ONE consolidated JSON file
(dashboard/data.json) that the HTML/JS dashboard loads.

This is the mechanism behind "all dashboards update simultaneously": every
dashboard page in the app reads from this single file. Change the raw CSVs
-> re-run load_to_sqlite.py -> re-run this script -> refresh the browser
(or redeploy) -> every page reflects the new numbers at once, because they
never hold their own copy of the data; they all render from data.json.

Run:
    python3 build_dashboard_json.py
"""

import sqlite3
import pandas as pd
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "..", "sql", "procurement.db")
OUT_PATH = os.path.join(BASE, "..", "dashboard", "data.json")

VIEWS = [
    "vw_VendorPerformance",
    "vw_PR_Summary",
    "vw_PO_Summary",
    "vw_GRN_Summary",
    "vw_Invoice_Summary",
    "vw_WarehouseInventory",
    "vw_DeliveryTime",
    "vw_ProcurementCycleTime",
    "vw_PriceRateAnalysis",
    "vw_MonthlySpend",
    "vw_SpendByCategory",
    "vw_SpendByDeptProject",
    "vw_BudgetVsActual",
    "vw_OrderFulfilment",
    "vw_OperationsKPI",
    "vw_ExceptionRisk",
    "vw_MonthlyProcurementTrend",
    "vw_ExecutiveSummary",
    "vw_CostOptimization",
]


def df_records(df: pd.DataFrame):
    return json.loads(df.to_json(orient="records"))


def main():
    conn = sqlite3.connect(DB_PATH)
    payload = {"generated_at": pd.Timestamp.now().isoformat(), "views": {}}

    for view in VIEWS:
        df = pd.read_sql(f"SELECT * FROM {view}", conn)
        payload["views"][view] = df_records(df)
        print(f"{view:<32s} -> {len(df):>5} rows")

    # A couple of small raw tables useful directly in the UI (filters, master data)
    for table in ["Vendor_Master", "Material_Master", "Department_Project_Master", "Warehouse_Master"]:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
        payload["views"][table] = df_records(df)
        print(f"{table:<32s} -> {len(df):>5} rows")

    with open(OUT_PATH, "w") as f:
        json.dump(payload, f)

    size_kb = os.path.getsize(OUT_PATH) / 1024
    print(f"\nWrote {OUT_PATH} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
