"""
Loads the raw CSV data (data/) into a local SQLite database and applies
the schema and views. In production this connects to the live SAP B1
SQL Server/HANA database instead - the views stay the same.

Run: python3 load_to_sqlite.py
"""

import sqlite3
import pandas as pd
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "..", "data")
SQL_DIR = os.path.join(BASE, "..", "sql")
DB_PATH = os.path.join(BASE, "..", "sql", "procurement.db")

TABLE_FILE_MAP = {
    "Vendor_Master": "Vendor_Master.csv",
    "Material_Master": "Material_Master.csv",
    "Department_Project_Master": "Department_Project_Master.csv",
    "Warehouse_Master": "Warehouse_Master.csv",
    "PR_Data": "PR_Data.csv",
    "PO_Data": "PO_Data.csv",
    "GRN_Data": "GRN_Data.csv",
    "Invoice_Data": "Invoice_Data.csv",
    "Inventory_Data": "Inventory_Data.csv",
    "Price_History": "Price_History.csv",
}


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    # 1. Create schema
    with open(os.path.join(SQL_DIR, "01_schema.sql")) as f:
        conn.executescript(f.read())

    # 2. Load CSVs into tables
    for table, filename in TABLE_FILE_MAP.items():
        path = os.path.join(DATA_DIR, filename)
        df = pd.read_csv(path)
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"Loaded {len(df):>5} rows -> {table}")

    # 3. Create views
    with open(os.path.join(SQL_DIR, "02_views.sql")) as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()
    print(f"\nDatabase built: {DB_PATH}")


if __name__ == "__main__":
    main()
