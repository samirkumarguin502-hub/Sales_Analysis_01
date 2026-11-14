import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import pandas as pd
import plotly.express as px

from src.analytics_data import load_analytics_data
from dashboard.style import apply_style, header, metric, PALETTE


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
CLEANED = ROOT / "data" / "cleaned"

CLEANING_PATH = REPORTS / "data_cleaning_summary.csv"
INGESTION_PATH = REPORTS / "data_ingestion_summary.csv"
ORDERS_PATH = CLEANED / "olist_orders_dataset.csv"

st.set_page_config(
    page_title="Reports | CommerceIQ",
    layout="wide",
)

apply_style()


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_report(path):
    if not path.exists():
        raise FileNotFoundError(f"Report not found: {path}")

    return pd.read_csv(path)


@st.cache_data
def load_complete_orders(path):
    if not path.exists():
        raise FileNotFoundError(f"Orders dataset not found: {path}")

    orders = pd.read_csv(path, low_memory=False)

    orders["order_purchase_timestamp"] = pd.to_datetime(
        orders["order_purchase_timestamp"],
        errors="coerce",
    )

    return orders


try:
    df = load_analytics_data()
    cleaning = load_report(CLEANING_PATH)
    ingestion = load_report(INGESTION_PATH)
    orders = load_complete_orders(ORDERS_PATH)

except Exception as exc:
    st.error(f"Unable to load report data: {exc}")
    st.stop()


# --------------------------------------------------
# PREPARE ANALYTICS DATA
# --------------------------------------------------

delivered = df[df["order_status"] == "delivered"].copy()

if delivered.empty:
    st.error("No delivered order-item records are available.")
    st.stop()

total_revenue = float(delivered["price"].sum())

total_orders = int(
    delivered["order_id"].nunique()
)

total_customers = int(
    delivered["customer_unique_id"].nunique()
)

average_order_value = (
    total_revenue / total_orders
    if total_orders else 0
)

total_units = int(len(delivered))

revenue_per_customer = (
    total_revenue / total_customers
    if total_customers else 0
)

# Order-grain aggregation:
# Do not sum total_payment_value from the item-grain fact table.
delivered_orders = (
    delivered[
        ["order_id", "total_payment_value"]
    ]
    .drop_duplicates(subset=["order_id"])
)

payment_value_total = float(
    delivered_orders["total_payment_value"].sum()
)

# Monthly revenue
monthly_revenue = (
    delivered.groupby("order_purchase_month", as_index=False)
    .agg(
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("order_purchase_month")
)

# Category revenue
category_revenue = (
    delivered.groupby("product_category_name", as_index=False)
    .agg(
        revenue=("price", "sum"),
        units=("order_item_id", "count"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
)

top_categories = category_revenue.head(10).copy()

# State-level customer insights
state_customers = (
    delivered.groupby("customer_state", as_index=False)
    .agg(
        customers=("customer_unique_id", "nunique"),
        revenue=("price", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
)

top_states = state_customers.head(10).copy()

# Customer-level revenue
customer_revenue = (
    delivered.groupby("customer_unique_id", as_index=False)
    .agg(
        orders=("order_id", "nunique"),
        revenue=("price", "sum"),
        last_purchase=("order_purchase_timestamp", "max"),
        city=("customer_city", "first"),
        state=("customer_state", "first"),
    )
    .sort_values("revenue", ascending=False)
)

# Complete order status distribution from cleaned orders table
status_summary = (
    orders["order_status"]
    .fillna("unknown")
    .value_counts()
    .rename_axis("order_status")
    .reset_index(name="orders")
    .sort_values("orders", ascending=False)
)

# --------------------------------------------------
# COMMON CHART STYLE
# --------------------------------------------------

CHART_FONT = {
    "family": "Arial",
    "size": 14,
    "color": "#111827",
}

AXIS_FONT = {
    "size": 13,
    "color": "#111827",
}

GRID_COLOR = "#D9DEE7"


def apply_chart_layout(
    fig,
    height=420,
    left=80,
    right=50,
    bottom=70,
):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(
            l=left,
            r=right,
            t=45,
            b=bottom,
        ),
        font=CHART_FONT,
        paper_bgcolor="white",
        plot_bgcolor="white",
        hoverlabel=dict(
            bgcolor="white",
            font=dict(
                color="#111827",
                size=13,
            ),
        ),
    )

    return fig


def format_horizontal_chart(fig, height=480):
    fig.update_traces(
        textposition="outside",
        textfont=dict(
            size=12,
            color="#111827",
        ),
        cliponaxis=False,
    )

    fig.update_xaxes(
        tickfont=AXIS_FONT,
        title_font=AXIS_FONT,
        gridcolor=GRID_COLOR,
        automargin=True,
        tickformat=",",
    )

    fig.update_yaxes(
        tickfont=dict(
            size=13,
            color="#111827",
        ),
        title="",
        automargin=True,
    )

    return apply_chart_layout(
        fig,
        height=height,
        left=190,
        right=100,
        bottom=65,
    )


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

header(
    "Reports & exports",
    "Executive reporting, business performance and downloadable analytics.",
    "REPORTING / DELIVERABLES",
)

st.caption(
    "Reporting period: September 2016 – September 2018 | "
    "Source: Olist Brazilian E-Commerce dataset"
)


# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------

st.subheader("Executive summary")

a, b, c, d = st.columns(4)

with a:
    metric(
        "DELIVERED REVENUE",
        f"R$ {total_revenue:,.2f}",
        "Item revenue, excluding freight",
    )

with b:
    metric(
        "DELIVERED ORDERS",
        f"{total_orders:,}",
        "Unique delivered orders",
    )

with c:
    metric(
        "AVERAGE ORDER VALUE",
        f"R$ {average_order_value:,.2f}",
        "Revenue / delivered orders",
    )

with d:
    metric(
        "UNIQUE CUSTOMERS",
        f"{total_customers:,}",
        "Delivered-order customers",
    )

a, b = st.columns(2)

with a:
    metric(
        "UNITS SOLD",
        f"{total_units:,}",
        "Delivered order items",
    )

with b:
    metric(
        "REVENUE PER CUSTOMER",
        f"R$ {revenue_per_customer:,.2f}",
        "Delivered revenue / unique customers",
    )

st.divider()


# --------------------------------------------------
# MONTHLY REVENUE TREND
# --------------------------------------------------

st.subheader("Monthly revenue performance")

monthly_fig = px.line(
    monthly_revenue,
    x="order_purchase_month",
    y="revenue",
    markers=True,
    labels={
        "order_purchase_month": "Purchase month",
        "revenue": "Revenue (BRL)",
    },
)

monthly_fig.update_traces(
    line=dict(
        color=PALETTE["teal"],
        width=3,
    ),
    marker=dict(size=7),
    hovertemplate=(
        "Month: %{x}<br>"
        "Revenue: R$ %{y:,.2f}"
        "<extra></extra>"
    ),
)

monthly_fig.update_xaxes(
    tickangle=-35,
    tickfont=dict(size=12, color="#111827"),
    title_font=AXIS_FONT,
    automargin=True,
)

monthly_fig.update_yaxes(
    tickfont=AXIS_FONT,
    title_font=AXIS_FONT,
    gridcolor=GRID_COLOR,
    tickprefix="R$ ",
    tickformat=",.0f",
    automargin=True,
)

monthly_fig = apply_chart_layout(
    monthly_fig,
    height=430,
    left=100,
    right=55,
    bottom=95,
)

st.plotly_chart(
    monthly_fig,
    use_container_width=True,
)

st.caption(
    "Monthly revenue is calculated from delivered item prices. "
    "Freight is excluded."
)

st.divider()


# --------------------------------------------------
# CATEGORY PERFORMANCE
# --------------------------------------------------

st.subheader("Top 10 product categories by revenue")

category_fig = px.bar(
    top_categories.sort_values("revenue"),
    x="revenue",
    y="product_category_name",
    orientation="h",
    text="revenue",
    labels={
        "revenue": "Revenue (BRL)",
        "product_category_name": "Product category",
    },
)

category_fig.update_traces(
    marker_color=PALETTE["teal"],
    texttemplate="R$ %{x:,.0f}",
    textposition="outside",
    textfont=dict(size=12, color="#111827"),
    cliponaxis=False,
    hovertemplate=(
        "Category: %{y}<br>"
        "Revenue: R$ %{x:,.2f}"
        "<extra></extra>"
    ),
)

category_fig.update_xaxes(
    tickfont=AXIS_FONT,
    title_font=AXIS_FONT,
    tickprefix="R$ ",
    tickformat=",.0f",
    gridcolor=GRID_COLOR,
    automargin=True,
)

category_fig.update_yaxes(
    tickfont=dict(size=13, color="#111827"),
    title="",
    automargin=True,
)

category_fig = apply_chart_layout(
    category_fig,
    height=520,
    left=230,
    right=110,
    bottom=65,
)

st.plotly_chart(
    category_fig,
    use_container_width=True,
)

st.dataframe(
    top_categories[
        [
            "product_category_name",
            "revenue",
            "units",
            "orders",
        ]
    ].rename(
        columns={
            "product_category_name": "Category",
            "revenue": "Revenue (BRL)",
            "units": "Units sold",
            "orders": "Orders",
        }
    ),
    hide_index=True,
    use_container_width=True,
)

st.divider()


# --------------------------------------------------
# ORDER STATUS DISTRIBUTION
# --------------------------------------------------

st.subheader("Complete order status distribution")

status_fig = px.bar(
    status_summary.sort_values("orders"),
    x="orders",
    y="order_status",
    orientation="h",
    text="orders",
    labels={
        "orders": "Number of orders",
        "order_status": "Order status",
    },
)

status_fig.update_traces(
    marker_color="#4285A4",
    texttemplate="%{x:,.0f}",
    textposition="outside",
    textfont=dict(size=12, color="#111827"),
    cliponaxis=False,
)

status_fig.update_xaxes(
    tickfont=AXIS_FONT,
    title_font=AXIS_FONT,
    gridcolor=GRID_COLOR,
    tickformat=",",
    automargin=True,
)

status_fig.update_yaxes(
    tickfont=dict(size=13, color="#111827"),
    title="",
    automargin=True,
)

status_fig = apply_chart_layout(
    status_fig,
    height=430,
    left=150,
    right=90,
    bottom=65,
)

st.plotly_chart(
    status_fig,
    use_container_width=True,
)

st.caption(
    "Order status distribution uses the complete cleaned orders dataset, "
    "including orders without order-item records."
)

st.divider()


# --------------------------------------------------
# CUSTOMER INSIGHTS
# --------------------------------------------------

st.subheader("Customer insights by state")

state_fig = px.bar(
    top_states.sort_values("revenue"),
    x="revenue",
    y="customer_state",
    orientation="h",
    text="revenue",
    labels={
        "revenue": "Revenue (BRL)",
        "customer_state": "Customer state",
    },
)

state_fig.update_traces(
    marker_color="#D9A441",
    texttemplate="R$ %{x:,.0f}",
    textposition="outside",
    textfont=dict(size=12, color="#111827"),
    cliponaxis=False,
)

state_fig.update_xaxes(
    tickfont=AXIS_FONT,
    title_font=AXIS_FONT,
    tickprefix="R$ ",
    tickformat=",.0f",
    gridcolor=GRID_COLOR,
    automargin=True,
)

state_fig.update_yaxes(
    tickfont=dict(size=13, color="#111827"),
    title="",
    automargin=True,
)

state_fig = apply_chart_layout(
    state_fig,
    height=480,
    left=100,
    right=110,
    bottom=65,
)

st.plotly_chart(
    state_fig,
    use_container_width=True,
)

st.subheader("Top 15 customers by delivered revenue")

st.dataframe(
    customer_revenue.head(15).rename(
        columns={
            "customer_unique_id": "Customer ID",
            "orders": "Orders",
            "revenue": "Revenue (BRL)",
            "last_purchase": "Last purchase",
            "city": "City",
            "state": "State",
        }
    ),
    hide_index=True,
    use_container_width=True,
)

st.divider()


# --------------------------------------------------
# DATASET AND CLEANING SUMMARY
# --------------------------------------------------

st.subheader("Dataset and cleaning summary")

a, b, c = st.columns(3)

with a:
    metric(
        "SOURCE DATASETS",
        f"{len(ingestion):,}",
        "Olist datasets inspected",
    )

with b:
    metric(
        "SOURCE ROWS",
        f"{int(ingestion['rows'].sum()):,}",
        "Before cleaning",
    )

with c:
    metric(
        "ROWS REMOVED",
        f"{int(cleaning['rows_removed'].sum()):,}",
        "Cleaning pipeline",
    )

cleaning_display = cleaning.copy()

cleaning_display["dataset"] = (
    cleaning_display["dataset"]
    .str.replace("_dataset.csv", "", regex=False)
)

st.dataframe(
    cleaning_display,
    hide_index=True,
    use_container_width=True,
)

st.divider()


# --------------------------------------------------
# KEY BUSINESS FINDINGS
# --------------------------------------------------

st.subheader("Key business findings")

top_category = (
    category_revenue.iloc[0]
    if not category_revenue.empty else None
)

top_state = (
    state_customers.iloc[0]
    if not state_customers.empty else None
)

if top_category is not None:
    st.info(
        f"**Leading category:** {top_category['product_category_name']} "
        f"generated R$ {top_category['revenue']:,.2f} in delivered item revenue."
    )

if top_state is not None:
    st.info(
        f"**Leading customer state:** {top_state['customer_state']} "
        f"generated R$ {top_state['revenue']:,.2f} in delivered item revenue "
        f"from {int(top_state['customers']):,} unique customers."
    )

st.info(
    f"**Customer economics:** Average delivered order value is "
    f"R$ {average_order_value:,.2f}, with "
    f"R$ {revenue_per_customer:,.2f} revenue per unique customer."
)

st.subheader("Business recommendations")

st.markdown(
    """
    - **Category strategy:** Review the highest-revenue categories for
      inventory planning, merchandising and promotional opportunities.
    - **Regional strategy:** Use state-level revenue and customer counts
      to prioritize regional marketing and fulfilment analysis.
    - **Customer retention:** Analyze repeat purchase behaviour and
      customer cohorts before designing retention campaigns.
    - **Operations:** Monitor order status distribution and delivery
      performance to identify operational bottlenecks.
    - **Reporting discipline:** Keep item revenue, freight and
      order-level payment values as separate measures.
    """
)

st.caption(
    "Findings are descriptive and based on the available Olist data. "
    "They do not establish causal relationships."
)

st.divider()


# --------------------------------------------------
# DOWNLOADABLE REPORTS
# --------------------------------------------------

st.subheader("Download reports")

st.write(
    "Export the real Olist analytics outputs for further analysis "
    "or portfolio documentation."
)

monthly_export = monthly_revenue.copy()
category_export = category_revenue.copy()
state_export = state_customers.copy()
customer_export = customer_revenue.copy()

col1, col2 = st.columns(2)

with col1:
    st.download_button(
        "Download monthly revenue CSV",
        data=monthly_export.to_csv(index=False).encode("utf-8"),
        file_name="commerceiq_monthly_revenue.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "Download category performance CSV",
        data=category_export.to_csv(index=False).encode("utf-8"),
        file_name="commerceiq_category_performance.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    st.download_button(
        "Download customer insights CSV",
        data=customer_export.to_csv(index=False).encode("utf-8"),
        file_name="commerceiq_customer_insights.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.download_button(
        "Download state performance CSV",
        data=state_export.to_csv(index=False).encode("utf-8"),
        file_name="commerceiq_state_performance.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "All exports are generated from the cleaned Olist analytics data. "
    "Currency: Brazilian Real (BRL)."
)
