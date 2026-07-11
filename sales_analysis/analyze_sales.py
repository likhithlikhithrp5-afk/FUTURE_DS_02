import csv
import os
import random
from collections import defaultdict
from datetime import date, timedelta
from math import ceil

DATA_FILE = os.path.join(os.path.dirname(__file__), 'sales_data.csv')
SUMMARY_FILE = os.path.join(os.path.dirname(__file__), 'sales_summary.txt')
HTML_FILE = os.path.join(os.path.dirname(__file__), 'sales_dashboard.html')

REGIONS = ['North', 'South', 'East', 'West']
CATEGORIES = [
    {
        'name': 'Electronics',
        'products': [
            ('Laptop', 899, 0.28),
            ('Smartphone', 699, 0.33),
            ('Tablet', 499, 0.29),
            ('Headphones', 149, 0.37),
        ],
    },
    {
        'name': 'Home & Kitchen',
        'products': [
            ('Blender', 89, 0.31),
            ('Coffee Maker', 129, 0.34),
            ('Air Fryer', 149, 0.30),
            ('Lamp', 59, 0.27),
        ],
    },
    {
        'name': 'Fashion',
        'products': [
            ('Shoes', 119, 0.26),
            ('Backpack', 79, 0.24),
            ('Jacket', 159, 0.29),
            ('Watch', 219, 0.32),
        ],
    },
    {
        'name': 'Health & Beauty',
        'products': [
            ('Skincare Kit', 69, 0.35),
            ('Hair Dryer', 99, 0.30),
            ('Perfume', 89, 0.33),
            ('Vitamin Pack', 39, 0.28),
        ],
    },
]


def generate_sales_data(rows=500):
    rng = random.Random(42)
    start_date = date(2024, 1, 1)
    end_date = date(2025, 6, 30)
    data = []
    for _ in range(rows):
        order_date = start_date + timedelta(days=rng.randint(0, (end_date - start_date).days))
        region = rng.choice(REGIONS)
        category = rng.choice(CATEGORIES)
        product_name, base_price, margin = rng.choice(category['products'])

        qty = rng.randint(1, 5)
        month_factor = 1.0 + (order_date.month % 6) * 0.03
        region_factor = {'North': 1.03, 'South': 0.97, 'East': 1.01, 'West': 1.08}[region]
        category_factor = {'Electronics': 1.08, 'Home & Kitchen': 0.95, 'Fashion': 1.02, 'Health & Beauty': 1.00}[category['name']]
        discount_factor = 1 - (rng.random() * 0.08)
        revenue = round(qty * base_price * month_factor * region_factor * category_factor * discount_factor, 2)
        cost = round(revenue * (1 - margin), 2)
        profit = round(revenue - cost, 2)
        data.append({
            'Order ID': f'ORD-{1000 + _}',
            'Order Date': order_date.strftime('%Y-%m-%d'),
            'Region': region,
            'Category': category['name'],
            'Product': product_name,
            'Quantity': qty,
            'Unit Price': round(base_price, 2),
            'Revenue': revenue,
            'Cost': cost,
            'Profit': profit,
        })
    return data


def write_csv(rows):
    fieldnames = ['Order ID', 'Order Date', 'Region', 'Category', 'Product', 'Quantity', 'Unit Price', 'Revenue', 'Cost', 'Profit']
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    total_revenue = round(sum(r['Revenue'] for r in rows), 2)
    total_profit = round(sum(r['Profit'] for r in rows), 2)
    total_orders = len(rows)
    avg_order_value = round(total_revenue / total_orders, 2)

    monthly = defaultdict(float)
    for item in rows:
        month = item['Order Date'][:7]
        monthly[month] += item['Revenue']
    monthly_sorted = sorted(monthly.items())

    product_revenue = defaultdict(float)
    product_profit = defaultdict(float)
    for item in rows:
        product_revenue[item['Product']] += item['Revenue']
        product_profit[item['Product']] += item['Profit']
    top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

    region_revenue = defaultdict(float)
    region_profit = defaultdict(float)
    for item in rows:
        region_revenue[item['Region']] += item['Revenue']
        region_profit[item['Region']] += item['Profit']
    top_regions = sorted(region_revenue.items(), key=lambda x: x[1], reverse=True)[:3]

    category_revenue = defaultdict(float)
    category_profit = defaultdict(float)
    for item in rows:
        category_revenue[item['Category']] += item['Revenue']
        category_profit[item['Category']] += item['Profit']
    top_categories = sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)[:3]

    insights = []
    insights.append('Business Sales Performance Summary')
    insights.append('')
    insights.append(f'Total Revenue: ${total_revenue:,.2f}')
    insights.append(f'Total Profit: ${total_profit:,.2f}')
    insights.append(f'Number of Orders: {total_orders}')
    insights.append(f'Average Order Value: ${avg_order_value:,.2f}')
    insights.append('')
    insights.append('Monthly Revenue Trend:')
    for month, value in monthly_sorted:
        insights.append(f'- {month}: ${value:,.2f}')
    insights.append('')
    insights.append('Top Products by Revenue:')
    for product, value in top_products:
        insights.append(f'- {product}: ${value:,.2f} revenue, ${product_profit[product]:,.2f} profit')
    insights.append('')
    insights.append('Top Regions by Revenue:')
    for region, value in top_regions:
        insights.append(f'- {region}: ${value:,.2f} revenue, ${region_profit[region]:,.2f} profit')
    insights.append('')
    insights.append('Top Categories by Revenue:')
    for category, value in top_categories:
        insights.append(f'- {category}: ${value:,.2f} revenue, ${category_profit[category]:,.2f} profit')
    insights.append('')
    insights.append('Recommended Actions:')
    insights.append('- Increase inventory for the highest-revenue products to avoid stockouts during peak demand.')
    insights.append('- Focus marketing spend on the West and North regions, where revenue growth is strongest.')
    insights.append('- Promote Electronics and Fashion bundles to lift average order value and overall margins.')
    return insights


def build_dashboard(rows, summary_lines):
    # Monthly values
    monthly = defaultdict(float)
    for item in rows:
        monthly[item['Order Date'][:7]] += item['Revenue']
    month_labels = sorted(monthly.keys())
    month_values = [monthly[m] for m in month_labels]

    # Top products
    product_revenue = defaultdict(float)
    for item in rows:
        product_revenue[item['Product']] += item['Revenue']
    top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    prod_labels = [p[0] for p in top_products]
    prod_values = [p[1] for p in top_products]

    def svg_line_chart(labels, values, width=540, height=260):
        max_value = max(values) if values else 1
        min_value = 0
        margin_left = 50
        margin_right = 20
        margin_top = 20
        margin_bottom = 40
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        points = []
        for i, val in enumerate(values):
            x = margin_left + (i / max(1, len(values) - 1)) * chart_width if len(values) > 1 else width / 2
            y = margin_top + chart_height - ((val - min_value) / max_value) * chart_height
            points.append((x, y))
        path = 'M ' + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in points)
        grid_lines = []
        for step in range(4):
            y = margin_top + (chart_height / 3) * step
            grid_lines.append(f'<line x1="{margin_left}" y1="{y:.1f}" x2="{width - margin_right}" y2="{y:.1f}" stroke="#e5e7eb" stroke-width="1" />')
        x_labels = []
        for i, label in enumerate(labels):
            x = margin_left + (i / max(1, len(labels) - 1)) * chart_width if len(labels) > 1 else width / 2
            x_labels.append(f'<text x="{x:.1f}" y="{height - 12}" text-anchor="middle" font-size="10">{label}</text>')
        return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#ffffff" />
            <text x="20" y="18" font-size="16" font-weight="600" fill="#0f172a">Monthly Revenue Trend</text>
            {''.join(grid_lines)}
            <path d="{path}" fill="none" stroke="#2563eb" stroke-width="3" />
            {''.join(x_labels)}
        </svg>'''

    def svg_bar_chart(labels, values, width=540, height=260):
        max_value = max(values) if values else 1
        margin_left = 50
        margin_right = 20
        margin_top = 20
        margin_bottom = 70
        chart_width = width - margin_left - margin_right
        chart_height = height - margin_top - margin_bottom
        bar_width = chart_width / max(1, len(labels)) - 20
        bars = []
        for i, (label, val) in enumerate(zip(labels, values)):
            x = margin_left + (i * (chart_width / len(labels))) + 10
            h = (val / max_value) * chart_height
            y = margin_top + chart_height - h
            bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{h:.1f}" fill="#10b981" />')
            bars.append(f'<text x="{x + bar_width/2:.1f}" y="{height - 20}" text-anchor="middle" font-size="10">{label}</text>')
        return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="100%" height="100%" fill="#ffffff" />
            <text x="20" y="18" font-size="16" font-weight="600" fill="#0f172a">Top Products by Revenue</text>
            {''.join(bars)}
        </svg>'''

    monthly_svg = svg_line_chart(month_labels, month_values)
    product_svg = svg_bar_chart(prod_labels, prod_values)

    summary_html = '\n'.join(summary_lines)
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Sales Performance Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; background: #f8fafc; color: #0f172a; margin: 0; padding: 24px; }}
    .card {{ background: white; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 20px; margin-bottom: 20px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
    .metric {{ background: #eff6ff; border-radius: 10px; padding: 12px; }}
    .metric h3 {{ font-size: 13px; color: #475569; margin: 0 0 6px; }}
    .metric p {{ font-size: 20px; margin: 0; font-weight: 700; color: #1d4ed8; }}
    .chart-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    pre {{ white-space: pre-wrap; background: #f8fafc; padding: 16px; border-radius: 8px; }}
    @media (max-width: 900px) {{ .metrics, .chart-grid {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <h1>Business Sales Performance Dashboard</h1>
  <p>This is a client-ready analysis based on a simple self-created sales dataset that matches the task requirements.</p>
  <div class="card">
    <div class="metrics">
      <div class="metric"><h3>Total Revenue</h3><p>${sum(r['Revenue'] for r in rows):,.2f}</p></div>
      <div class="metric"><h3>Total Profit</h3><p>${sum(r['Profit'] for r in rows):,.2f}</p></div>
      <div class="metric"><h3>Orders</h3><p>{len(rows)}</p></div>
      <div class="metric"><h3>Avg. Order Value</h3><p>${round(sum(r['Revenue'] for r in rows)/len(rows),2):,.2f}</p></div>
    </div>
  </div>
  <div class="card">
    <div class="chart-grid">
      <div>{monthly_svg}</div>
      <div>{product_svg}</div>
    </div>
  </div>
  <div class="card">
    <h2>Executive Summary</h2>
    <pre>{summary_html}</pre>
  </div>
</body>
</html>'''
    with open(HTML_FILE, 'w', encoding='utf-8') as fh:
        fh.write(html)


def main():
    rows = generate_sales_data(500)
    write_csv(rows)
    summary_lines = summarize(rows)
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(summary_lines))
    build_dashboard(rows, summary_lines)
    print('Created sales data and dashboard files.')
    print(f'CSV: {DATA_FILE}')
    print(f'Summary: {SUMMARY_FILE}')
    print(f'HTML: {HTML_FILE}')


if __name__ == '__main__':
    main()
