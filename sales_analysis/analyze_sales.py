import csv
import json
import os
import random
import zipfile
from collections import defaultdict
from datetime import date, timedelta
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd


BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

LEGACY_CSV_FILE = os.path.join(BASE_DIR, "sales_data.csv")
LEGACY_XLSX_FILE = os.path.join(BASE_DIR, "sales_data.xlsx")
LEGACY_HTML_FILE = os.path.join(BASE_DIR, "sales_dashboard.html")

CSV_FILE = os.path.join(DATA_DIR, "sales_data.csv")
XLSX_FILE = os.path.join(DATA_DIR, "sales_data.xlsx")
SUMMARY_FILE = os.path.join(BASE_DIR, "sales_summary.txt")
HTML_FILE = os.path.join(DASHBOARD_DIR, "sales_dashboard.html")
PDF_FILE = os.path.join(BASE_DIR, "report.pdf")

REGIONS = ["North", "South", "East", "West"]
CATEGORIES = [
    {
        "name": "Electronics",
        "products": [
            ("Laptop", 899, 0.28),
            ("Smartphone", 699, 0.33),
            ("Tablet", 499, 0.29),
            ("Headphones", 149, 0.37),
        ],
    },
    {
        "name": "Home & Kitchen",
        "products": [
            ("Blender", 89, 0.31),
            ("Coffee Maker", 129, 0.34),
            ("Air Fryer", 149, 0.30),
            ("Lamp", 59, 0.27),
        ],
    },
    {
        "name": "Fashion",
        "products": [
            ("Shoes", 119, 0.26),
            ("Backpack", 79, 0.24),
            ("Jacket", 159, 0.29),
            ("Watch", 219, 0.32),
        ],
    },
    {
        "name": "Health & Beauty",
        "products": [
            ("Skincare Kit", 69, 0.35),
            ("Hair Dryer", 99, 0.30),
            ("Perfume", 89, 0.33),
            ("Vitamin Pack", 39, 0.28),
        ],
    },
]


def ensure_dirs():
    for folder in (DATA_DIR, DASHBOARD_DIR, OUTPUTS_DIR):
        os.makedirs(folder, exist_ok=True)


def generate_sales_data(rows=500):
    rng = random.Random(42)
    start_date = date(2024, 1, 1)
    end_date = date(2025, 6, 30)
    data = []

    for index in range(rows):
        order_date = start_date + timedelta(days=rng.randint(0, (end_date - start_date).days))
        region = rng.choice(REGIONS)
        category = rng.choice(CATEGORIES)
        product_name, base_price, margin = rng.choice(category["products"])

        quantity = rng.randint(1, 5)
        month_factor = 1.0 + (order_date.month % 6) * 0.03
        region_factor = {"North": 1.03, "South": 0.97, "East": 1.01, "West": 1.08}[region]
        category_factor = {
            "Electronics": 1.08,
            "Home & Kitchen": 0.95,
            "Fashion": 1.02,
            "Health & Beauty": 1.00,
        }[category["name"]]
        discount_factor = 1 - (rng.random() * 0.08)
        revenue = round(quantity * base_price * month_factor * region_factor * category_factor * discount_factor, 2)
        cost = round(revenue * (1 - margin), 2)
        profit = round(revenue - cost, 2)

        data.append(
            {
                "Order ID": f"ORD-{1000 + index}",
                "Order Date": order_date.strftime("%Y-%m-%d"),
                "Region": region,
                "Category": category["name"],
                "Product": product_name,
                "Quantity": quantity,
                "Unit Price": round(base_price, 2),
                "Revenue": revenue,
                "Cost": cost,
                "Profit": profit,
            }
        )

    return data


def write_data_files(rows):
    fieldnames = [
        "Order ID",
        "Order Date",
        "Region",
        "Category",
        "Product",
        "Quantity",
        "Unit Price",
        "Revenue",
        "Cost",
        "Profit",
    ]

    for path in (CSV_FILE, LEGACY_CSV_FILE):
        with open(path, "w", newline="", encoding="utf-8") as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    df = pd.DataFrame(rows)
    write_simple_xlsx(df, XLSX_FILE)
    write_simple_xlsx(df, LEGACY_XLSX_FILE)
    return df


def excel_column_name(index):
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name


def xlsx_cell(value, row_index, column_index):
    ref = f"{excel_column_name(column_index)}{row_index}"
    if isinstance(value, (int, float)):
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'


def write_simple_xlsx(df, path):
    headers = list(df.columns)
    rows_xml = []
    rows_xml.append(
        '<row r="1">' + "".join(xlsx_cell(header, 1, column_index + 1) for column_index, header in enumerate(headers)) + "</row>"
    )
    for row_index, (_, row) in enumerate(df.iterrows(), start=2):
        rows_xml.append(
            f'<row r="{row_index}">'
            + "".join(xlsx_cell(row[header], row_index, column_index + 1) for column_index, header in enumerate(headers))
            + "</row>"
        )

    sheet_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>{''.join(rows_xml)}</sheetData>
</worksheet>'''
    workbook_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets><sheet name="Sales Data" sheetId="1" r:id="rId1"/></sheets>
</workbook>'''
    workbook_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>'''
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>'''

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", content_types)
        workbook.writestr("_rels/.rels", root_rels)
        workbook.writestr("xl/workbook.xml", workbook_xml)
        workbook.writestr("xl/_rels/workbook.xml.rels", workbook_rels)
        workbook.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def format_currency(value):
    return f"${value:,.2f}"


def aggregate_metrics(df):
    monthly = (
        df.assign(Month=df["Order Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)["Revenue"]
        .sum()
        .sort_values("Month")
    )
    product = (
        df.groupby("Product", as_index=False)[["Revenue", "Profit"]]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    category = (
        df.groupby("Category", as_index=False)[["Revenue", "Profit"]]
        .sum()
        .sort_values("Revenue", ascending=False)
    )
    region = (
        df.groupby("Region", as_index=False)[["Revenue", "Profit"]]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    return {
        "total_revenue": float(df["Revenue"].sum()),
        "total_profit": float(df["Profit"].sum()),
        "orders": int(len(df)),
        "aov": float(df["Revenue"].sum() / len(df)),
        "profit_margin": float(df["Profit"].sum() / df["Revenue"].sum()),
        "monthly": monthly,
        "product": product,
        "category": category,
        "region": region,
    }


def write_summary(metrics):
    top_category = metrics["category"].iloc[0]
    top_region = metrics["region"].iloc[0]
    top_product = metrics["product"].iloc[0]
    category_share = top_category["Revenue"] / metrics["total_revenue"]
    region_share = top_region["Revenue"] / metrics["total_revenue"]
    weakest_category = metrics["category"].iloc[-1]

    lines = [
        "Business Sales Performance Summary",
        "",
        f"Total Revenue: {format_currency(metrics['total_revenue'])}",
        f"Total Profit: {format_currency(metrics['total_profit'])}",
        f"Number of Orders: {metrics['orders']}",
        f"Average Order Value: {format_currency(metrics['aov'])}",
        f"Overall Profit Margin: {metrics['profit_margin']:.1%}",
        "",
        "Monthly Revenue Trend:",
    ]

    for _, row in metrics["monthly"].iterrows():
        lines.append(f"- {row['Month']}: {format_currency(row['Revenue'])}")

    lines.extend(["", "Top Products by Revenue:"])
    for _, row in metrics["product"].head(5).iterrows():
        lines.append(f"- {row['Product']}: {format_currency(row['Revenue'])} revenue, {format_currency(row['Profit'])} profit")

    lines.extend(["", "Top Regions by Revenue:"])
    for _, row in metrics["region"].iterrows():
        lines.append(f"- {row['Region']}: {format_currency(row['Revenue'])} revenue, {format_currency(row['Profit'])} profit")

    lines.extend(["", "Top Categories by Revenue:"])
    for _, row in metrics["category"].iterrows():
        lines.append(f"- {row['Category']}: {format_currency(row['Revenue'])} revenue, {format_currency(row['Profit'])} profit")

    lines.extend(
        [
            "",
            "Business Insights:",
            f"- {top_category['Category']} is the strongest category, producing {category_share:.1%} of total revenue and {format_currency(top_category['Profit'])} in profit.",
            f"- {top_region['Region']} is the leading region with {region_share:.1%} revenue share, making it the best candidate for expansion and retention campaigns.",
            f"- {top_product['Product']} is the highest-value product and should receive priority inventory planning before peak sales months.",
            f"- {weakest_category['Category']} trails the portfolio and needs targeted promotions, bundles, or pricing tests to increase contribution.",
            "",
            "Recommended Actions:",
            "- Protect inventory and advertising budget for the highest-revenue products to avoid stockouts during demand spikes.",
            "- Prioritize East and South regional campaigns because they currently generate the highest revenue base.",
            "- Build Electronics-led bundles with Fashion and Health & Beauty add-ons to lift average order value.",
            "- Run promotional experiments for Home & Kitchen to improve revenue contribution without over-discounting profitable items.",
        ]
    )

    with open(SUMMARY_FILE, "w", encoding="utf-8") as file_handle:
        file_handle.write("\n".join(lines))

    return lines


def save_chart_images(metrics):
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(metrics["monthly"]["Month"], metrics["monthly"]["Revenue"], color="#2563eb", linewidth=2.8, marker="o")
    ax.set_title("Monthly Revenue Trend", loc="left", fontsize=15, weight="bold")
    ax.set_ylabel("Revenue")
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter("${x:,.0f}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS_DIR, "revenue_trend.png"), dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    top_products = metrics["product"].head(8).sort_values("Revenue")
    ax.barh(top_products["Product"], top_products["Revenue"], color="#0f766e")
    ax.set_title("Top Products by Revenue", loc="left", fontsize=15, weight="bold")
    ax.xaxis.set_major_formatter("${x:,.0f}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS_DIR, "product_analysis.png"), dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.8))
    category = metrics["category"].sort_values("Revenue")
    ax.barh(category["Category"], category["Revenue"], color="#7c3aed", label="Revenue")
    ax.barh(category["Category"], category["Profit"], color="#f59e0b", label="Profit")
    ax.set_title("Revenue and Profit by Category", loc="left", fontsize=15, weight="bold")
    ax.xaxis.set_major_formatter("${x:,.0f}")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS_DIR, "category_analysis.png"), dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    region = metrics["region"].sort_values("Revenue")
    ax.barh(region["Region"], region["Revenue"], color="#dc2626")
    ax.set_title("Revenue by Region", loc="left", fontsize=15, weight="bold")
    ax.xaxis.set_major_formatter("${x:,.0f}")
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUTS_DIR, "region_analysis.png"), dpi=160)
    plt.close(fig)

    fig = plt.figure(figsize=(12, 7), facecolor="#f8fafc")
    fig.suptitle("Business Sales Performance Dashboard", x=0.05, y=0.96, ha="left", fontsize=20, weight="bold")
    cards = [
        ("Total Revenue", format_currency(metrics["total_revenue"])),
        ("Total Profit", format_currency(metrics["total_profit"])),
        ("Orders", f"{metrics['orders']:,}"),
        ("Average Order Value", format_currency(metrics["aov"])),
    ]
    for index, (label, value) in enumerate(cards):
        ax = fig.add_axes([0.05 + index * 0.235, 0.76, 0.2, 0.13])
        ax.set_facecolor("white")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(0.05, 0.68, label, transform=ax.transAxes, fontsize=10, color="#475569")
        ax.text(0.05, 0.23, value, transform=ax.transAxes, fontsize=18, weight="bold", color="#0f172a")

    ax1 = fig.add_axes([0.06, 0.12, 0.53, 0.52])
    ax1.plot(metrics["monthly"]["Month"], metrics["monthly"]["Revenue"], color="#2563eb", linewidth=2.5)
    ax1.set_title("Monthly Revenue Trend", loc="left", weight="bold")
    ax1.tick_params(axis="x", rotation=45, labelsize=8)
    ax1.yaxis.set_major_formatter("${x:,.0f}")

    ax2 = fig.add_axes([0.66, 0.12, 0.29, 0.52])
    top_products = metrics["product"].head(6).sort_values("Revenue")
    ax2.barh(top_products["Product"], top_products["Revenue"], color="#0f766e")
    ax2.set_title("Top Products", loc="left", weight="bold")
    ax2.xaxis.set_major_formatter("${x:,.0f}")

    fig.savefig(os.path.join(OUTPUTS_DIR, "dashboard_screenshot.png"), dpi=160)
    plt.close(fig)


def write_pdf_report(metrics, summary_lines):
    with PdfPages(PDF_FILE) as pdf:
        fig = plt.figure(figsize=(8.5, 11), facecolor="white")
        fig.suptitle("Business Sales Performance Report", x=0.08, y=0.96, ha="left", fontsize=20, weight="bold")
        fig.text(
            0.08,
            0.915,
            "Future Interns Data Science & Analytics Task 1",
            fontsize=11,
            color="#475569",
        )

        cards = [
            ("Total Revenue", format_currency(metrics["total_revenue"])),
            ("Total Profit", format_currency(metrics["total_profit"])),
            ("Orders", f"{metrics['orders']:,}"),
            ("Average Order Value", format_currency(metrics["aov"])),
            ("Profit Margin", f"{metrics['profit_margin']:.1%}"),
        ]
        y = 0.84
        for label, value in cards:
            fig.text(0.08, y, label, fontsize=10, color="#667085", weight="bold")
            fig.text(0.35, y, value, fontsize=13, color="#101828", weight="bold")
            y -= 0.04

        story = "\n".join(summary_lines[summary_lines.index("Business Insights:") :])
        fig.text(0.08, 0.62, story, fontsize=9.5, color="#344054", va="top", linespacing=1.45)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(11, 6.5))
        ax.plot(metrics["monthly"]["Month"], metrics["monthly"]["Revenue"], color="#2563eb", linewidth=2.8, marker="o")
        ax.set_title("Monthly Revenue Trend", loc="left", fontsize=16, weight="bold")
        ax.set_ylabel("Revenue")
        ax.tick_params(axis="x", rotation=45)
        ax.yaxis.set_major_formatter("${x:,.0f}")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(11, 6.5))
        top_products = metrics["product"].head(8).sort_values("Revenue")
        axes[0].barh(top_products["Product"], top_products["Revenue"], color="#0f766e")
        axes[0].set_title("Top Products by Revenue", loc="left", weight="bold")
        axes[0].xaxis.set_major_formatter("${x:,.0f}")

        category = metrics["category"].sort_values("Revenue")
        axes[1].barh(category["Category"], category["Revenue"], color="#7c3aed", label="Revenue")
        axes[1].barh(category["Category"], category["Profit"], color="#f59e0b", label="Profit")
        axes[1].set_title("Revenue and Profit by Category", loc="left", weight="bold")
        axes[1].xaxis.set_major_formatter("${x:,.0f}")
        axes[1].legend()
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(11, 6.5))
        region = metrics["region"].sort_values("Revenue")
        ax.barh(region["Region"], region["Revenue"], color="#dc2626")
        ax.set_title("Revenue by Region", loc="left", fontsize=16, weight="bold")
        ax.xaxis.set_major_formatter("${x:,.0f}")
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)


def build_dashboard_html(df, metrics, summary_lines):
    records = df.copy()
    records["Order Date"] = records["Order Date"].dt.strftime("%Y-%m-%d")
    payload = json.dumps(records.to_dict(orient="records"))
    summary_html = "\n".join(summary_lines)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Business Sales Performance Dashboard</title>
  <style>
    :root {{
      --bg: #f6f7fb;
      --panel: #ffffff;
      --ink: #101828;
      --muted: #667085;
      --line: #d9e0ea;
      --blue: #2563eb;
      --teal: #0f766e;
      --orange: #ea580c;
      --rose: #be123c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: Inter, Segoe UI, Arial, sans-serif;
    }}
    header {{
      padding: 24px 32px 10px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }}
    h1 {{ margin: 0 0 6px; font-size: 30px; letter-spacing: 0; }}
    header p {{ margin: 0; color: var(--muted); max-width: 960px; line-height: 1.5; }}
    main {{ padding: 20px 32px 32px; }}
    .filters, .kpis, .grid, .story-grid {{ display: grid; gap: 14px; }}
    .filters {{ grid-template-columns: 1.3fr 1fr 1fr 1fr 1fr; margin-bottom: 16px; }}
    .filter, .kpi, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    label {{ display: block; margin-bottom: 7px; color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    select, input {{
      width: 100%;
      min-height: 38px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 10px;
      background: #fff;
      color: var(--ink);
    }}
    .kpis {{ grid-template-columns: repeat(5, minmax(0, 1fr)); margin-bottom: 16px; }}
    .kpi span {{ display: block; color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; }}
    .kpi strong {{ display: block; margin-top: 8px; font-size: 24px; }}
    .grid {{ grid-template-columns: minmax(0, 1.4fr) minmax(360px, 0.9fr); margin-bottom: 16px; }}
    .story-grid {{ grid-template-columns: 1fr 1fr; }}
    .panel h2 {{ margin: 0 0 12px; font-size: 17px; }}
    svg {{ width: 100%; height: 330px; display: block; }}
    .bar-label {{ font-size: 12px; fill: var(--ink); }}
    .axis {{ stroke: var(--line); stroke-width: 1; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ padding: 9px 8px; border-bottom: 1px solid var(--line); text-align: left; white-space: nowrap; }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; }}
    pre {{
      margin: 0;
      white-space: pre-wrap;
      color: #344054;
      font-family: inherit;
      line-height: 1.55;
    }}
    @media (max-width: 980px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .filters, .kpis, .grid, .story-grid {{ grid-template-columns: 1fr; }}
      svg {{ height: 300px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Business Sales Performance Dashboard</h1>
    <p>Interactive sales analytics report with KPI cards, trend analysis, regional and category performance, and business recommendations for Future Interns Task 1.</p>
  </header>
  <main>
    <section class="filters" aria-label="Dashboard filters">
      <div class="filter"><label for="regionFilter">Region</label><select id="regionFilter"><option value="All">All Regions</option></select></div>
      <div class="filter"><label for="categoryFilter">Category</label><select id="categoryFilter"><option value="All">All Categories</option></select></div>
      <div class="filter"><label for="productFilter">Product</label><select id="productFilter"><option value="All">All Products</option></select></div>
      <div class="filter"><label for="startDate">Start Date</label><input id="startDate" type="date" /></div>
      <div class="filter"><label for="endDate">End Date</label><input id="endDate" type="date" /></div>
    </section>

    <section class="kpis" aria-label="Key performance indicators">
      <div class="kpi"><span>Total Revenue</span><strong id="kpiRevenue"></strong></div>
      <div class="kpi"><span>Total Profit</span><strong id="kpiProfit"></strong></div>
      <div class="kpi"><span>Orders</span><strong id="kpiOrders"></strong></div>
      <div class="kpi"><span>Average Order Value</span><strong id="kpiAov"></strong></div>
      <div class="kpi"><span>Profit Margin</span><strong id="kpiMargin"></strong></div>
    </section>

    <section class="grid">
      <div class="panel"><h2>Monthly Revenue Trend</h2><svg id="trendChart" role="img"></svg></div>
      <div class="panel"><h2>Revenue by Product</h2><svg id="productChart" role="img"></svg></div>
    </section>

    <section class="story-grid">
      <div class="panel"><h2>Revenue and Profit by Category</h2><svg id="categoryChart" role="img"></svg></div>
      <div class="panel"><h2>Revenue by Region</h2><svg id="regionChart" role="img"></svg></div>
    </section>

    <section class="grid" style="margin-top:16px;">
      <div class="panel table-wrap"><h2>Top Records</h2><table><thead><tr><th>Order</th><th>Date</th><th>Region</th><th>Category</th><th>Product</th><th>Revenue</th><th>Profit</th></tr></thead><tbody id="recordRows"></tbody></table></div>
      <div class="panel"><h2>Executive Story</h2><pre>{summary_html}</pre></div>
    </section>
  </main>

  <script>
    const salesData = {payload};
    const currency = new Intl.NumberFormat("en-US", {{ style: "currency", currency: "USD", maximumFractionDigits: 0 }});
    const preciseCurrency = new Intl.NumberFormat("en-US", {{ style: "currency", currency: "USD" }});

    function uniqueValues(field) {{
      return [...new Set(salesData.map(row => row[field]))].sort();
    }}

    function fillSelect(id, values) {{
      const select = document.getElementById(id);
      values.forEach(value => {{
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
      }});
    }}

    function sum(rows, field) {{
      return rows.reduce((total, row) => total + Number(row[field]), 0);
    }}

    function groupBy(rows, key, valueField) {{
      const grouped = new Map();
      rows.forEach(row => grouped.set(row[key], (grouped.get(row[key]) || 0) + Number(row[valueField])));
      return [...grouped.entries()].map(([label, value]) => ({{ label, value }})).sort((a, b) => b.value - a.value);
    }}

    function groupCategory(rows) {{
      const grouped = new Map();
      rows.forEach(row => {{
        const current = grouped.get(row.Category) || {{ label: row.Category, revenue: 0, profit: 0 }};
        current.revenue += Number(row.Revenue);
        current.profit += Number(row.Profit);
        grouped.set(row.Category, current);
      }});
      return [...grouped.values()].sort((a, b) => b.revenue - a.revenue);
    }}

    function filterRows() {{
      const region = document.getElementById("regionFilter").value;
      const category = document.getElementById("categoryFilter").value;
      const product = document.getElementById("productFilter").value;
      const startDate = document.getElementById("startDate").value;
      const endDate = document.getElementById("endDate").value;
      return salesData.filter(row =>
        (region === "All" || row.Region === region) &&
        (category === "All" || row.Category === category) &&
        (product === "All" || row.Product === product) &&
        (!startDate || row["Order Date"] >= startDate) &&
        (!endDate || row["Order Date"] <= endDate)
      );
    }}

    function drawLineChart(id, rows) {{
      const monthlyMap = new Map();
      rows.forEach(row => {{
        const month = row["Order Date"].slice(0, 7);
        monthlyMap.set(month, (monthlyMap.get(month) || 0) + Number(row.Revenue));
      }});
      const data = [...monthlyMap.entries()].sort().map(([label, value]) => ({{ label, value }}));
      const svg = document.getElementById(id);
      const width = 780, height = 330, left = 58, right = 22, top = 18, bottom = 54;
      const chartWidth = width - left - right;
      const chartHeight = height - top - bottom;
      const max = Math.max(...data.map(d => d.value), 1);
      const points = data.map((d, i) => {{
        const x = left + (data.length <= 1 ? chartWidth / 2 : i * chartWidth / (data.length - 1));
        const y = top + chartHeight - (d.value / max) * chartHeight;
        return [x, y, d.label, d.value];
      }});
      const path = points.map((p, i) => `${{i === 0 ? "M" : "L"}} ${{p[0]}},${{p[1]}}`).join(" ");
      svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);
      svg.innerHTML = `
        <line class="axis" x1="${{left}}" y1="${{top + chartHeight}}" x2="${{width - right}}" y2="${{top + chartHeight}}"></line>
        ${{[0, .25, .5, .75, 1].map(t => `<line class="axis" x1="${{left}}" y1="${{top + chartHeight - chartHeight * t}}" x2="${{width - right}}" y2="${{top + chartHeight - chartHeight * t}}"></line>`).join("")}}
        <path d="${{path}}" fill="none" stroke="#2563eb" stroke-width="4"></path>
        ${{points.map(p => `<circle cx="${{p[0]}}" cy="${{p[1]}}" r="4" fill="#2563eb"><title>${{p[2]}}: ${{preciseCurrency.format(p[3])}}</title></circle>`).join("")}}
        ${{points.filter((_, i) => i % 2 === 0 || data.length < 10).map(p => `<text x="${{p[0]}}" y="${{height - 22}}" text-anchor="middle" font-size="11" fill="#667085">${{p[2]}}</text>`).join("")}}
      `;
    }}

    function drawBarChart(id, data, color, options = {{}}) {{
      const svg = document.getElementById(id);
      const width = 620, height = 330, left = 124, right = 24, top = 16, bottom = 30;
      const chartWidth = width - left - right;
      const barHeight = Math.min(32, (height - top - bottom) / Math.max(data.length, 1) - 8);
      const max = Math.max(...data.map(d => d.value || d.revenue), 1);
      svg.setAttribute("viewBox", `0 0 ${{width}} ${{height}}`);
      svg.innerHTML = data.map((d, i) => {{
        const value = d.value || d.revenue;
        const y = top + i * (barHeight + 10);
        const w = (value / max) * chartWidth;
        const profitW = d.profit ? (d.profit / max) * chartWidth : 0;
        return `
          <text class="bar-label" x="${{left - 10}}" y="${{y + barHeight * .7}}" text-anchor="end">${{d.label}}</text>
          <rect x="${{left}}" y="${{y}}" width="${{w}}" height="${{barHeight}}" rx="4" fill="${{color}}"></rect>
          ${{options.profit ? `<rect x="${{left}}" y="${{y + barHeight * .52}}" width="${{profitW}}" height="${{barHeight * .48}}" rx="3" fill="#f59e0b"></rect>` : ""}}
          <text x="${{left + w + 8}}" y="${{y + barHeight * .7}}" font-size="12" fill="#667085">${{currency.format(value)}}</text>
        `;
      }}).join("");
    }}

    function render() {{
      const rows = filterRows();
      const revenue = sum(rows, "Revenue");
      const profit = sum(rows, "Profit");
      document.getElementById("kpiRevenue").textContent = preciseCurrency.format(revenue);
      document.getElementById("kpiProfit").textContent = preciseCurrency.format(profit);
      document.getElementById("kpiOrders").textContent = rows.length.toLocaleString("en-US");
      document.getElementById("kpiAov").textContent = preciseCurrency.format(rows.length ? revenue / rows.length : 0);
      document.getElementById("kpiMargin").textContent = revenue ? `${{(profit / revenue * 100).toFixed(1)}}%` : "0.0%";

      drawLineChart("trendChart", rows);
      drawBarChart("productChart", groupBy(rows, "Product", "Revenue").slice(0, 8), "#0f766e");
      drawBarChart("categoryChart", groupCategory(rows).map(d => ({{ label: d.label, value: d.revenue, profit: d.profit }})), "#7c3aed", {{ profit: true }});
      drawBarChart("regionChart", groupBy(rows, "Region", "Revenue"), "#dc2626");

      document.getElementById("recordRows").innerHTML = rows
        .sort((a, b) => Number(b.Revenue) - Number(a.Revenue))
        .slice(0, 12)
        .map(row => `<tr><td>${{row["Order ID"]}}</td><td>${{row["Order Date"]}}</td><td>${{row.Region}}</td><td>${{row.Category}}</td><td>${{row.Product}}</td><td>${{preciseCurrency.format(row.Revenue)}}</td><td>${{preciseCurrency.format(row.Profit)}}</td></tr>`)
        .join("");
    }}

    fillSelect("regionFilter", uniqueValues("Region"));
    fillSelect("categoryFilter", uniqueValues("Category"));
    fillSelect("productFilter", uniqueValues("Product"));
    document.getElementById("startDate").value = salesData.map(row => row["Order Date"]).sort()[0];
    document.getElementById("endDate").value = salesData.map(row => row["Order Date"]).sort().at(-1);
    document.querySelectorAll("select, input").forEach(control => control.addEventListener("change", render));
    render();
  </script>
</body>
</html>"""

    for path in (HTML_FILE, LEGACY_HTML_FILE):
        with open(path, "w", encoding="utf-8") as file_handle:
            file_handle.write(html)


def main():
    ensure_dirs()
    rows = generate_sales_data(500)
    df = write_data_files(rows)
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    metrics = aggregate_metrics(df)
    summary_lines = write_summary(metrics)
    save_chart_images(metrics)
    write_pdf_report(metrics, summary_lines)
    build_dashboard_html(df, metrics, summary_lines)

    print("Created complete sales analytics submission.")
    print(f"CSV: {CSV_FILE}")
    print(f"XLSX: {XLSX_FILE}")
    print(f"Summary: {SUMMARY_FILE}")
    print(f"HTML dashboard: {HTML_FILE}")
    print(f"PDF report: {PDF_FILE}")
    print(f"Outputs: {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
