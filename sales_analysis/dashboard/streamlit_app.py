from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sales_data.csv"


st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")


@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH, parse_dates=["Order Date"])
    data["Month"] = data["Order Date"].dt.to_period("M").astype(str)
    return data


df = load_data()

st.title("Business Sales Performance Dashboard")
st.caption("Interactive KPI dashboard for Future Interns Data Science & Analytics Task 1")

with st.sidebar:
    st.header("Filters")
    regions = st.multiselect("Region", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
    categories = st.multiselect("Category", sorted(df["Category"].unique()), default=sorted(df["Category"].unique()))
    products = st.multiselect("Product", sorted(df["Product"].unique()), default=sorted(df["Product"].unique()))
    date_range = st.date_input(
        "Order Date",
        value=(df["Order Date"].min().date(), df["Order Date"].max().date()),
        min_value=df["Order Date"].min().date(),
        max_value=df["Order Date"].max().date(),
    )

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = df["Order Date"].min().date()
    end_date = df["Order Date"].max().date()

filtered = df[
    df["Region"].isin(regions)
    & df["Category"].isin(categories)
    & df["Product"].isin(products)
    & (df["Order Date"].dt.date >= start_date)
    & (df["Order Date"].dt.date <= end_date)
]

total_revenue = filtered["Revenue"].sum()
total_profit = filtered["Profit"].sum()
orders = len(filtered)
aov = total_revenue / orders if orders else 0
profit_margin = total_profit / total_revenue if total_revenue else 0

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("Total Profit", f"${total_profit:,.2f}")
kpi3.metric("Orders", f"{orders:,}")
kpi4.metric("Average Order Value", f"${aov:,.2f}")
kpi5.metric("Profit Margin", f"{profit_margin:.1%}")

trend = filtered.groupby("Month", as_index=False)["Revenue"].sum().sort_values("Month")
product = filtered.groupby("Product", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False).head(10)
category = filtered.groupby("Category", as_index=False)[["Revenue", "Profit"]].sum().sort_values("Revenue", ascending=False)
region = filtered.groupby("Region", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)

left, right = st.columns((1.35, 1))
with left:
    st.subheader("Monthly Revenue Trend")
    st.line_chart(trend, x="Month", y="Revenue", use_container_width=True)

with right:
    st.subheader("Revenue by Product")
    st.bar_chart(product, x="Product", y="Revenue", use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Revenue and Profit by Category")
    st.bar_chart(category, x="Category", y=["Revenue", "Profit"], use_container_width=True)

with right:
    st.subheader("Revenue by Region")
    st.bar_chart(region, x="Region", y="Revenue", use_container_width=True)

st.subheader("Business Story")
if not filtered.empty:
    top_category = category.iloc[0]
    top_region = region.iloc[0]
    st.write(
        f"{top_category['Category']} is the strongest category in the selected view, "
        f"while {top_region['Region']} is the highest-revenue region. Protecting these strengths "
        "and using bundles or targeted promotions in lower-performing areas can improve overall growth."
    )
else:
    st.write("No records match the selected filters.")

st.subheader("Filtered Order Detail")
st.dataframe(
    filtered.sort_values("Revenue", ascending=False)[
        ["Order ID", "Order Date", "Region", "Category", "Product", "Quantity", "Revenue", "Profit"]
    ],
    use_container_width=True,
    hide_index=True,
)
