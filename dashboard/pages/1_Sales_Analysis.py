import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st
import plotly.express as px

from src.analytics_data import load_analytics_data
from dashboard.style import apply_style, header, metric, PALETTE


ROOT = Path(__file__).resolve().parents[2]
ORDERS_PATH = ROOT / "data" / "cleaned" / "olist_orders_dataset.csv"

st.set_page_config(
    page_title="Sales Analysis | CommerceIQ",
    page_icon="◈",
    layout="wide",
)

apply_style()

df = load_analytics_data()

header(
    "Sales analysis",
    "Explore actual revenue, order volume and sales performance across Olist.",
    "ANALYTICS / SALES",
)

# --------------------------------------------------
# DELIVERED SALES METRICS
# --------------------------------------------------

delivered = df[df["order_status"].eq("delivered")].copy()

revenue = delivered["price"].sum()
orders = delivered["order_id"].nunique()
aov = revenue / orders if orders else 0

a, b, c = st.columns(3)

with a:
    metric(
        "DELIVERED SALES REVENUE",
        f"R$ {revenue:,.0f}",
        "Delivered item prices",
    )

with b:
    metric(
        "DELIVERED ORDERS",
        f"{orders:,}",
        "Unique delivered orders",
    )

with c:
    metric(
        "AVERAGE ORDER VALUE",
        f"R$ {aov:,.2f}",
        "Merchandise revenue per order",
    )

# --------------------------------------------------
# MONTHLY REVENUE TREND
# --------------------------------------------------

st.subheader("Monthly revenue trend")

monthly = (
    delivered.groupby("order_purchase_month")["price"]
    .sum()
    .reset_index(name="revenue")
    .sort_values("order_purchase_month")
)

fig = px.line(
    monthly,
    x="order_purchase_month",
    y="revenue",
    markers=True,
)

fig.update_traces(
    line_color=PALETTE["teal"],
    line_width=3,
    marker_size=7,
    hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
)

fig.update_layout(
    height=380,
    margin=dict(l=25, r=25, t=25, b=45),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(
        family="Arial",
        size=13,
        color="#344054",
    ),
    xaxis=dict(
        title="Purchase month",
        tickfont=dict(size=12, color="#344054"),
        showgrid=False,
    ),
    yaxis=dict(
        title="Revenue (BRL)",
        tickfont=dict(size=12, color="#344054"),
        gridcolor="#E5E7EB",
        zeroline=False,
    ),
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# REVENUE BY CATEGORY
# --------------------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("Revenue by category")

    category_sales = (
        delivered.groupby("product_category_name")["price"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    category_fig = px.bar(
        category_sales,
        x="price",
        y="product_category_name",
        orientation="h",
        text_auto=".2s",
    )

    category_fig.update_traces(
        marker_color=PALETTE["teal"],
        textposition="outside",
        cliponaxis=False,
        textfont=dict(size=11, color="#344054"),
        hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
    )

    category_fig.update_layout(
        height=480,
        margin=dict(l=20, r=45, t=25, b=45),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=13,
            color="#344054",
        ),
        xaxis=dict(
            title="Revenue (BRL)",
            tickfont=dict(size=11, color="#344054"),
            gridcolor="#E5E7EB",
        ),
        yaxis=dict(
            title="",
            categoryorder="total ascending",
            tickfont=dict(size=12, color="#344054"),
            automargin=True,
        ),
        showlegend=False,
    )

    st.plotly_chart(category_fig, use_container_width=True)

# --------------------------------------------------
# ORDER STATUS DISTRIBUTION
# --------------------------------------------------

with right:
    st.subheader("Order status distribution")

    if not ORDERS_PATH.exists():
        st.error(
            "Cleaned orders dataset not found. "
            "Run the data cleaning pipeline first."
        )
    else:
        orders_df = pd.read_csv(ORDERS_PATH)

        status_counts = (
            orders_df["order_status"]
            .fillna("unknown")
            .value_counts()
            .rename_axis("status")
            .reset_index(name="orders")
        )

        status_fig = px.pie(
            status_counts,
            names="status",
            values="orders",
            hole=0.55,
        )

        status_fig.update_traces(
            textposition="inside",
            textinfo="percent",
            textfont=dict(
                size=13,
                color="white",
            ),
            hovertemplate=(
                "Status: %{label}<br>"
                "Orders: %{value:,}<br>"
                "Share: %{percent}<extra></extra>"
            ),
        )

        status_fig.update_layout(
            height=480,
            margin=dict(l=20, r=20, t=25, b=35),
            paper_bgcolor="white",
            font=dict(
                family="Arial",
                size=13,
                color="#344054",
            ),
            legend=dict(
                title=dict(
                    text="Order status",
                    font=dict(size=13, color="#344054"),
                ),
                font=dict(
                    size=12,
                    color="#344054",
                ),
                orientation="h",
                yanchor="top",
                y=-0.08,
                xanchor="center",
                x=0.5,
            ),
        )

        st.plotly_chart(status_fig, use_container_width=True)

# --------------------------------------------------
# DATA SOURCE NOTE
# --------------------------------------------------

st.caption(
    "Source: Olist Brazilian E-Commerce Public Dataset. "
    "Revenue represents delivered merchandise item prices in BRL; "
    "freight is excluded. Order status distribution uses the complete "
    "cleaned orders dataset."
)