"""
Generates SAP B1-style raw data for the procurement project: 12 months of
vendor, material, PR/PO/GRN/invoice, and inventory data across 6 verticals.

Run: python3 generate_data.py
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUT = "../data"

# ---------------------------------------------------------------------------
# 1. REFERENCE DATA: Verticals, Brands (10 well-known India-dealing brands
#    per vertical, repeated as the primary vendor pool), Cities
# ---------------------------------------------------------------------------

VERTICALS = {
    "Electrical": ["Havells India", "Polycab India", "Finolex Cables", "Anchor by Panasonic",
                   "V-Guard Industries", "Crompton Greaves Consumer", "Legrand India",
                   "Schneider Electric India", "KEI Industries", "Orient Electric"],
    "Carpentry": ["Century Plyboards", "Greenply Industries", "Kitply Industries",
                  "Archidply Industries", "Duro Ply India", "Action Tesa",
                  "Merino Laminates", "Hettich India", "Ebco Private Ltd",
                  "Sarvottam Plywood"],
    "Road Construction Materials": ["UltraTech Cement", "ACC Limited", "Ambuja Cements",
                  "Shree Cement", "JK Cement", "Dalmia Bharat Cement", "Tata Steel",
                  "JSW Steel", "Birla Corporation", "L&T Construction Materials"],
    "Solar Panels": ["Tata Power Solar", "Waaree Energies", "Adani Solar", "Vikram Solar",
                  "Goldi Solar", "Premier Energies", "Emmvee Solar", "RenewSys India",
                  "Websol Energy System", "Loom Solar"],
    "Batteries": ["Exide Industries", "Amara Raja Batteries (Amaron)", "Luminous Power Technologies",
                  "Su-Kam Power Systems", "Okaya Power", "HBL Power Systems", "Livguard Energy",
                  "Panasonic Energy India", "Base Corporation", "Exicom Power Solutions"],
    "Plumbing Materials": ["Astral Pipes", "Supreme Industries", "Finolex Pipes", "Prince Pipes",
                  "Ashirvad Pipes (Aliaxis)", "CERA Sanitaryware", "Jaquar Group", "Hindware Homes",
                  "Kajaria Ceramics", "Roto Pumps"],
}

CITIES = [("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Ahmedabad", "Gujarat"),
          ("Surat", "Gujarat"), ("Delhi", "Delhi"), ("Gurugram", "Haryana"),
          ("Bengaluru", "Karnataka"), ("Chennai", "Tamil Nadu"), ("Hyderabad", "Telangana"),
          ("Kolkata", "West Bengal"), ("Jaipur", "Rajasthan"), ("Lucknow", "Uttar Pradesh"),
          ("Bhubaneswar", "Odisha"), ("Nagpur", "Maharashtra"), ("Indore", "Madhya Pradesh")]

PAYMENT_TERMS = ["Net 15", "Net 30", "Net 45", "Net 60", "Advance 20% + Net 30"]

WAREHOUSES = [
    ("WH-01", "Central Warehouse - Pune"),
    ("WH-02", "Site Store - Nashik Project"),
    ("WH-03", "Site Store - Aurangabad Project"),
]

DEPARTMENTS = [
    ("DEP-01", "Electrical Execution", "PRJ-101", "Solar Rooftop Phase 2 - Nashik"),
    ("DEP-02", "Civil & Infrastructure", "PRJ-102", "Road & Site Development - Aurangabad"),
    ("DEP-03", "Solar EPC", "PRJ-103", "Ground Mount Solar Plant - Ahmednagar"),
    ("DEP-04", "MEP (Mechanical Electrical Plumbing)", "PRJ-104", "Commercial Complex Fit-out - Pune"),
    ("DEP-05", "Maintenance & Facilities", "PRJ-105", "O&M Contracts - Multiple Sites"),
    ("DEP-06", "Carpentry & Interiors", "PRJ-106", "Corporate Office Interiors - Mumbai"),
]

random.seed(42)

# ---------------------------------------------------------------------------
# 2. VENDOR MASTER  (SAP B1 OCRD analogue)
# ---------------------------------------------------------------------------
vendor_rows = []
vcode = 1000
for vertical, brands in VERTICALS.items():
    for brand in brands:
        city, state = random.choice(CITIES)
        vendor_rows.append({
            "VendorCode": f"V-{vcode}",
            "VendorName": brand,
            "Vertical": vertical,
            "City": city,
            "State": state,
            "GSTIN": f"{random.randint(10,36):02d}{fake.bothify('?????#####?#Z#').upper()}",
            "ContactPerson": fake.name(),
            "Phone": fake.numerify("9#########"),
            "Email": f"sales@{brand.split()[0].lower()}.co.in",
            "OnboardDate": fake.date_between(start_date="-6y", end_date="-1y").isoformat(),
            "PaymentTerms": random.choice(PAYMENT_TERMS),
            "VendorRatingInternal": round(random.uniform(3.0, 4.9), 1),
            "IsActive": "Y",
        })
        vcode += 1
vendor_df = pd.DataFrame(vendor_rows)
vendor_df.to_csv(f"{OUT}/Vendor_Master.csv", index=False)

# ---------------------------------------------------------------------------
# 3. MATERIAL MASTER (SAP B1 OITM analogue)
# ---------------------------------------------------------------------------
ITEM_TEMPLATES = {
    "Electrical": [("Armoured Copper Cable 3.5C x 95 sqmm", "Mtr", 420),
                   ("PVC Insulated Wire 2.5 sqmm (90m coil)", "Coil", 1650),
                   ("MCB 32A Single Pole", "Nos", 145),
                   ("Distribution Board 8-Way", "Nos", 1250),
                   ("LED Flood Light 100W", "Nos", 1850),
                   ("Modular Switch 6A", "Nos", 65),
                   ("Cable Tray 300mm (2m length)", "Nos", 980),
                   ("Junction Box IP65", "Nos", 210),
                   ("Earthing Strip GI 25x3mm", "Mtr", 95),
                   ("Contactor 40A 3 Pole", "Nos", 1450),
                   ("MCCB 200A", "Nos", 8200),
                   ("Cable Gland Brass 25mm", "Nos", 55)],
    "Carpentry": [("Plywood 19mm BWP (8x4 ft)", "Sheet", 3450),
                  ("Laminate Sheet 1mm (8x4 ft)", "Sheet", 1250),
                  ("MDF Board 12mm (8x4 ft)", "Sheet", 1650),
                  ("Hinges SS 4 inch", "Pair", 85),
                  ("Drawer Channel 18 inch Telescopic", "Pair", 420),
                  ("Door Lock Mortise Set", "Set", 950),
                  ("Wood Screws 2 inch (box of 100)", "Box", 180),
                  ("Veneer Sheet Teak (8x4 ft)", "Sheet", 4200),
                  ("PVC Edge Banding Tape (100m roll)", "Roll", 650),
                  ("Adhesive Fevicol SH (5kg)", "Can", 1150)],
    "Road Construction Materials": [("OPC 53 Grade Cement (50kg bag)", "Bag", 385),
                  ("TMT Steel Bar Fe500D 12mm", "Ton", 62000),
                  ("Crushed Stone Aggregate 20mm", "Ton", 850),
                  ("River Sand (fine aggregate)", "Ton", 1450),
                  ("Bitumen VG-30 (drum 180kg)", "Drum", 9800),
                  ("Ready Mix Concrete M25", "Cum", 6200),
                  ("PQC Dowel Bar 32mm", "Ton", 64500),
                  ("Wire Mesh Fabric 6mm@150c/c", "Ton", 58500),
                  ("Kerb Stone Precast", "Nos", 210),
                  ("Geotextile Fabric (roll 100m2)", "Roll", 4800)],
    "Solar Panels": [("Solar Module 540Wp Mono PERC", "Nos", 12800),
                  ("Solar Module 550Wp Bifacial", "Nos", 14200),
                  ("String Inverter 50kW", "Nos", 385000),
                  ("Module Mounting Structure (per kW)", "kW Set", 4800),
                  ("DC Cable 4 sqmm Solar Grade (100m)", "Coil", 3200),
                  ("MC4 Connector Pair", "Pair", 95),
                  ("Combiner Box 6 in 1 out", "Nos", 6500),
                  ("Earthing Kit for Module Structure", "Set", 850),
                  ("Anti-Reflective Glass Panel (spare)", "Nos", 3100),
                  ("Solar Cable Gland Set", "Set", 145)],
    "Batteries": [("Tubular Battery 150Ah C10", "Nos", 14500),
                  ("Lithium-ion Battery Pack 48V 100Ah", "Nos", 118000),
                  ("Inverter 2.5kVA Pure Sinewave", "Nos", 16500),
                  ("VRLA SMF Battery 12V 100Ah", "Nos", 9800),
                  ("Battery Rack 4-Tier MS", "Nos", 3400),
                  ("Battery Interconnect Cable Set", "Set", 650),
                  ("Battery Monitoring System (BMS module)", "Nos", 4200),
                  ("Deep Cycle Battery 200Ah", "Nos", 21500)],
    "Plumbing Materials": [("UPVC Pipe 4 inch SCH-40 (3m length)", "Pcs", 1150),
                  ("CPVC Pipe 1 inch (3m length)", "Pcs", 380),
                  ("PVC Elbow 4 inch", "Nos", 95),
                  ("Ball Valve 1 inch Brass", "Nos", 320),
                  ("Water Tank 1000L HDPE", "Nos", 6800),
                  ("Sanitaryware Wash Basin", "Nos", 2450),
                  ("Concealed Cistern with Frame", "Set", 8500),
                  ("Bathroom Faucet Single Lever", "Nos", 1850),
                  ("Submersible Pump 1HP", "Nos", 9200),
                  ("Pipe Clamp GI 4 inch", "Nos", 65)],
}

item_rows = []
icode = 5000
for vertical, items in ITEM_TEMPLATES.items():
    for desc, uom, price in items:
        item_rows.append({
            "ItemCode": f"I-{icode}",
            "ItemDescription": desc,
            "Vertical": vertical,
            "UOM": uom,
            "StandardPrice": price,
            "HSNCode": f"{random.randint(3901, 8544)}",
            "PreferredBrand": random.choice(VERTICALS[vertical]),
            "ItemGroup": vertical,
        })
        icode += 1
item_df = pd.DataFrame(item_rows)
item_df.to_csv(f"{OUT}/Material_Master.csv", index=False)

dept_df = pd.DataFrame(DEPARTMENTS, columns=["DeptCode", "DeptName", "ProjectCode", "ProjectName"])
budget_alloc = {
    "PRJ-101": 9_500_000, "PRJ-102": 14_200_000, "PRJ-103": 21_000_000,
    "PRJ-104": 6_800_000, "PRJ-105": 3_200_000, "PRJ-106": 4_500_000,
}
dept_df["BudgetAllocatedINR"] = dept_df["ProjectCode"].map(budget_alloc)
dept_df.to_csv(f"{OUT}/Department_Project_Master.csv", index=False)

wh_df = pd.DataFrame(WAREHOUSES, columns=["WarehouseCode", "WarehouseName"])
wh_df.to_csv(f"{OUT}/Warehouse_Master.csv", index=False)

print(f"Vendors: {len(vendor_df)} | Materials: {len(item_df)} | Depts: {len(dept_df)} | Warehouses: {len(wh_df)}")

# ---------------------------------------------------------------------------
# 4. TRANSACTIONAL DATA: PR -> PO -> GRN -> Invoice  (12-month window)
# ---------------------------------------------------------------------------
START_DATE = datetime(2025, 9, 1)
END_DATE = datetime(2026, 8, 31)
TOTAL_DAYS = (END_DATE - START_DATE).days

vendor_by_vertical = {}
for vertical in VERTICALS:
    vendor_by_vertical[vertical] = vendor_df[vendor_df.Vertical == vertical]["VendorCode"].tolist()

items_by_vertical = {}
for vertical in VERTICALS:
    items_by_vertical[vertical] = item_df[item_df.Vertical == vertical].to_dict("records")

vendor_lookup = vendor_df.set_index("VendorCode").to_dict("index")
item_lookup = item_df.set_index("ItemCode").to_dict("index")

REQUESTERS = [fake.name() for _ in range(14)]
APPROVERS = [fake.name() for _ in range(5)]
INSPECTORS = [fake.name() for _ in range(6)]

N_PR = 950

pr_rows, po_rows, grn_rows, inv_rows, price_hist_rows = [], [], [], [], []

pr_counter, po_counter, grn_counter, inv_counter = 30001, 40001, 50001, 60001

# small monthly market price drift per vertical, to make Price/Rate Analysis meaningful
price_drift = {v: random.uniform(-0.015, 0.03) for v in VERTICALS}

for i in range(N_PR):
    dept = random.choice(DEPARTMENTS)
    vertical = random.choices(list(VERTICALS.keys()), weights=[18, 12, 20, 22, 14, 14])[0]
    item = random.choice(items_by_vertical[vertical])
    pr_date = START_DATE + timedelta(days=random.randint(0, TOTAL_DAYS - 25))
    qty = max(1, int(np.random.gamma(3, 8)))
    required_date = pr_date + timedelta(days=random.randint(7, 30))
    pr_status = random.choices(["Converted to PO", "Pending Approval", "Rejected", "Cancelled"],
                                weights=[86, 6, 5, 3])[0]
    pr_no = f"PR-{pr_counter}"
    pr_counter += 1

    pr_rows.append({
        "PRNo": pr_no, "PRDate": pr_date.date().isoformat(), "DeptCode": dept[0],
        "DeptName": dept[1], "ProjectCode": dept[2], "ProjectName": dept[3],
        "ItemCode": item["ItemCode"], "ItemDescription": item["ItemDescription"],
        "Vertical": vertical, "RequestedQty": qty, "UOM": item["UOM"],
        "RequiredByDate": required_date.date().isoformat(),
        "RequestedBy": random.choice(REQUESTERS),
        "Priority": random.choices(["High", "Medium", "Low"], weights=[25, 55, 20])[0],
        "Status": pr_status,
    })

    if pr_status != "Converted to PO":
        continue

    # ---- PO ----
    po_date = pr_date + timedelta(days=random.randint(1, 6))
    months_elapsed = (po_date.year - START_DATE.year) * 12 + (po_date.month - START_DATE.month)
    market_factor = (1 + price_drift[vertical]) ** months_elapsed
    unit_price = round(item["StandardPrice"] * market_factor * random.uniform(0.94, 1.08), 2)
    vendor_code = random.choice(vendor_by_vertical[vertical])
    ordered_qty = qty + random.choice([0, 0, 0, 1, -1])
    ordered_qty = max(1, ordered_qty)
    promised_lead_days = random.randint(3, 21)
    delivery_date = po_date + timedelta(days=promised_lead_days)
    total_amount = round(unit_price * ordered_qty, 2)
    po_status = random.choices(["Closed", "Open", "Partially Delivered", "Cancelled"],
                                weights=[70, 10, 15, 5])[0]
    po_no = f"PO-{po_counter}"
    po_counter += 1

    po_rows.append({
        "PONo": po_no, "PODate": po_date.date().isoformat(), "PRNo": pr_no,
        "VendorCode": vendor_code, "VendorName": vendor_lookup[vendor_code]["VendorName"],
        "Vertical": vertical, "ItemCode": item["ItemCode"],
        "ItemDescription": item["ItemDescription"], "OrderedQty": ordered_qty,
        "UOM": item["UOM"], "UnitPrice": unit_price, "TotalAmount": total_amount,
        "Currency": "INR", "PromisedDeliveryDate": delivery_date.date().isoformat(),
        "PaymentTerms": vendor_lookup[vendor_code]["PaymentTerms"],
        "ApprovedBy": random.choice(APPROVERS), "Status": po_status,
        "DeptCode": dept[0], "ProjectCode": dept[2],
    })

    price_hist_rows.append({
        "Month": po_date.strftime("%Y-%m"), "Vertical": vertical, "ItemCode": item["ItemCode"],
        "ItemDescription": item["ItemDescription"], "VendorCode": vendor_code,
        "UnitPrice": unit_price, "StandardPrice": item["StandardPrice"],
    })

    if po_status == "Cancelled":
        continue

    # ---- GRN ----
    n_grns = 1 if po_status != "Partially Delivered" else random.choice([1, 2])
    remaining_qty = ordered_qty
    for g in range(n_grns):
        actual_lead_days = promised_lead_days + int(np.random.normal(1.5, 4))
        actual_lead_days = max(1, actual_lead_days)
        grn_date = po_date + timedelta(days=actual_lead_days if g == 0 else actual_lead_days + random.randint(3, 10))
        this_qty = remaining_qty if (g == n_grns - 1) else max(1, remaining_qty // 2)
        remaining_qty -= this_qty
        rejected_qty = int(this_qty * random.choices([0, 0.02, 0.05, 0.1], weights=[75, 12, 8, 5])[0])
        accepted_qty = this_qty - rejected_qty
        grn_no = f"GRN-{grn_counter}"
        grn_counter += 1
        grn_rows.append({
            "GRNNo": grn_no, "GRNDate": grn_date.date().isoformat(), "PONo": po_no,
            "VendorCode": vendor_code, "WarehouseCode": random.choices(
                [w[0] for w in WAREHOUSES], weights=[50, 30, 20])[0],
            "ItemCode": item["ItemCode"], "ItemDescription": item["ItemDescription"],
            "Vertical": vertical, "ReceivedQty": this_qty, "AcceptedQty": accepted_qty,
            "RejectedQty": rejected_qty, "UOM": item["UOM"],
            "InspectedBy": random.choice(INSPECTORS),
            "QCStatus": "Rejected - Partial" if rejected_qty > 0 else "Accepted",
        })

        # ---- Invoice (usually follows GRN) ----
        if random.random() < 0.93:
            inv_date = grn_date + timedelta(days=random.randint(0, 5))
            inv_amount = round(unit_price * accepted_qty, 2)
            tax_amount = round(inv_amount * 0.18, 2)
            total_inv = round(inv_amount + tax_amount, 2)
            terms_days = {"Net 15": 15, "Net 30": 30, "Net 45": 45, "Net 60": 60,
                          "Advance 20% + Net 30": 30}[vendor_lookup[vendor_code]["PaymentTerms"]]
            due_date = inv_date + timedelta(days=terms_days)
            paid = random.random() < 0.88
            payment_delay = int(np.random.normal(3, 6))
            payment_date = due_date + timedelta(days=payment_delay) if paid else None
            inv_no = f"INV-{inv_counter}"
            inv_counter += 1
            inv_rows.append({
                "InvoiceNo": inv_no, "InvoiceDate": inv_date.date().isoformat(),
                "PONo": po_no, "GRNNo": grn_no, "VendorCode": vendor_code,
                "VendorName": vendor_lookup[vendor_code]["VendorName"], "Vertical": vertical,
                "InvoiceAmount": inv_amount, "TaxAmount": tax_amount, "TotalAmount": total_inv,
                "PaymentDueDate": due_date.date().isoformat(),
                "PaymentStatus": "Paid" if paid else random.choice(["Pending", "Overdue"]),
                "PaymentDate": payment_date.date().isoformat() if payment_date else "",
                "DeptCode": dept[0], "ProjectCode": dept[2],
            })

pr_df = pd.DataFrame(pr_rows)
po_df = pd.DataFrame(po_rows)
grn_df = pd.DataFrame(grn_rows)
inv_df = pd.DataFrame(inv_rows)
price_hist_df = pd.DataFrame(price_hist_rows)

# ---------------------------------------------------------------------------
# Calibrate savings per vertical to the 5-7% band vs. standard price

std_price_map = item_df.set_index("ItemCode")["StandardPrice"].to_dict()
po_df["_StdCost"] = po_df["ItemCode"].map(std_price_map) * po_df["OrderedQty"]

rng = np.random.default_rng(7)
for vertical in VERTICALS:
    mask = po_df.Vertical == vertical
    benchmark_cost = po_df.loc[mask, "_StdCost"].sum()
    actual_cost = po_df.loc[mask, "TotalAmount"].sum()
    if actual_cost <= 0 or benchmark_cost <= 0:
        continue
    target_savings_pct = rng.uniform(5.0, 7.0)
    desired_actual = benchmark_cost * (1 - target_savings_pct / 100.0)
    scale = desired_actual / actual_cost

    po_df.loc[mask, "UnitPrice"] = (po_df.loc[mask, "UnitPrice"] * scale).round(2)
    po_df.loc[mask, "TotalAmount"] = (po_df.loc[mask, "TotalAmount"] * scale).round(2)

    inv_mask = inv_df.Vertical == vertical
    inv_df.loc[inv_mask, "InvoiceAmount"] = (inv_df.loc[inv_mask, "InvoiceAmount"] * scale).round(2)
    inv_df.loc[inv_mask, "TaxAmount"] = (inv_df.loc[inv_mask, "InvoiceAmount"] * 0.18).round(2)
    inv_df.loc[inv_mask, "TotalAmount"] = (inv_df.loc[inv_mask, "InvoiceAmount"] + inv_df.loc[inv_mask, "TaxAmount"]).round(2)

    ph_mask = price_hist_df.Vertical == vertical
    price_hist_df.loc[ph_mask, "UnitPrice"] = (price_hist_df.loc[ph_mask, "UnitPrice"] * scale).round(2)

    print(f"  Calibrated {vertical:<28s} -> target savings {target_savings_pct:.2f}% "
          f"(benchmark Rs.{benchmark_cost:,.0f} vs actual Rs.{desired_actual:,.0f})")

po_df.drop(columns=["_StdCost"], inplace=True)

pr_df.to_csv(f"{OUT}/PR_Data.csv", index=False)
po_df.to_csv(f"{OUT}/PO_Data.csv", index=False)
grn_df.to_csv(f"{OUT}/GRN_Data.csv", index=False)
inv_df.to_csv(f"{OUT}/Invoice_Data.csv", index=False)
price_hist_df.to_csv(f"{OUT}/Price_History.csv", index=False)

print(f"PR: {len(pr_df)} | PO: {len(po_df)} | GRN: {len(grn_df)} | Invoice: {len(inv_df)} | PriceHist: {len(price_hist_df)}")

# ---------------------------------------------------------------------------
# 5. WAREHOUSE INVENTORY SNAPSHOT (SAP B1 OITW analogue) - as of END_DATE
# ---------------------------------------------------------------------------
inv_snapshot_rows = []
for item in item_rows:
    for wh_code, wh_name in WAREHOUSES:
        if random.random() < 0.75:  # not every item sits in every warehouse
            stock_qty = max(0, int(np.random.gamma(2.2, 12)))
            reorder_level = int(item["StandardPrice"] > 0) * random.randint(10, 40)
            last_received = START_DATE + timedelta(days=random.randint(0, TOTAL_DAYS))
            last_issued = last_received + timedelta(days=random.randint(0, 45))
            last_issued = min(last_issued, END_DATE)
            aging_days = (END_DATE - last_received).days
            inv_snapshot_rows.append({
                "WarehouseCode": wh_code, "WarehouseName": wh_name,
                "ItemCode": item["ItemCode"], "ItemDescription": item["ItemDescription"],
                "Vertical": item["Vertical"], "UOM": item["UOM"],
                "StockQty": stock_qty, "ReorderLevel": reorder_level,
                "LastReceivedDate": last_received.date().isoformat(),
                "LastIssuedDate": last_issued.date().isoformat(),
                "AgingDays": aging_days,
                "UnitValue": item["StandardPrice"],
                "StockValueINR": round(stock_qty * item["StandardPrice"], 2),
                "StockStatus": "Below Reorder" if stock_qty < reorder_level else "Adequate",
            })
inventory_df = pd.DataFrame(inv_snapshot_rows)
inventory_df.to_csv(f"{OUT}/Inventory_Data.csv", index=False)
print(f"Inventory snapshot rows: {len(inventory_df)}")

print("\nAll raw SAP B1-style data dumps generated successfully in /data")
