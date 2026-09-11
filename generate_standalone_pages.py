import os

PAGES = [
    ("executive", "Executive / Management Dashboard"),
    ("opskpi", "Operations KPI Dashboard"),
    ("spend", "Spend Analytics Dashboard"),
    ("price", "Material Price / Rate Analysis Dashboard"),
    ("pr", "PR Processing Dashboard"),
    ("po", "PO Processing Dashboard"),
    ("grn", "GRN Processing Dashboard"),
    ("invoice", "Invoice Processing Dashboard"),
    ("cycle", "Total Procurement Cycle Time Dashboard"),
    ("fulfilment", "Procurement Performance / Order Fulfilment Dashboard"),
    ("vendor", "Supplier / Vendor Performance Score Dashboard"),
    ("delivery", "Delivery Time & Average Lead Time Dashboard"),
    ("inventory", "Warehouse Inventory & Aging Dashboard"),
    ("trend", "Monthly Procurement Trend Dashboard"),
    ("risk", "Exception / Risk Dashboard"),
    ("outcomes", "Project Outcomes & Cost Optimization Dashboard"),
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Innovel Energy Services</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<link rel="stylesheet" href="../style.css">
</head>
<body data-page="{page_id}">

<div class="main-col" style="width:100%;">

  <header class="topbar">
    <div style="display:flex; align-items:center; gap:14px;">
      <a class="back-link" href="../index.html">&larr; All dashboards</a>
      <div class="topbar-title" id="pageTitle">{title}</div>
    </div>
    <div class="topbar-controls">
      <label class="filter-label" for="jumpNav">Jump to</label>
      <select id="jumpNav"><option value="">Choose a dashboard…</option></select>

      <label class="filter-label" for="verticalFilter">Vertical</label>
      <select id="verticalFilter">
        <option value="ALL">All verticals</option>
      </select>

      <button id="refreshBtn" class="refresh-btn" title="Reload data.json — simulates a refresh after the source data changes">
        <span class="refresh-icon">&#10227;</span> Refresh data
      </button>
    </div>
  </header>

  <main class="content" id="content">
    <div class="loading" id="loadingState">Loading procurement data&hellip;</div>
  </main>

</div>

<script src="../lib.js"></script>
<script src="../standalone.js"></script>
</body>
</html>
"""

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard", "pages")
os.makedirs(OUT_DIR, exist_ok=True)

for page_id, title in PAGES:
    content = TEMPLATE.format(title=title, page_id=page_id)
    path = os.path.join(OUT_DIR, f"{page_id}.html")
    with open(path, "w") as f:
        f.write(content)
    print(f"Wrote {path}")

print(f"\n{len(PAGES)} standalone dashboard pages generated in dashboard/pages/")
