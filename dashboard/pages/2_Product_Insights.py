import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px
import pandas as pd

from src.analytics_data import load_analytics_data
from dashboard.style import apply_style, header, metric, PALETTE


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Product Insights | CommerceIQ",
    layout="wide",
)

apply_style()

df = load_analytics_data()


# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------

delivered = df[df["order_status"] == "delivered"].copy()

delivered["product_category_name"] = (
    delivered["product_category_name"]
    .fillna("unknown")
    .replace("", "unknown")
)

# Item-level metrics
total_revenue = delivered["price"].sum()
total_units = len(delivered)
unique_products = delivered["product_id"].nunique()

average_unit_price = (
    total_revenue / total_units if total_units else 0
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

header(
    "Product insights",
    "Understand actual product demand, category contribution and pricing patterns.",
    "ANALYTICS / PRODUCTS",
)


# --------------------------------------------------
# KPI METRICS
# --------------------------------------------------

st.markdown("### Product performance overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    metric(
        "PRODUCT REVENUE",
        f"R$ {total_revenue:,.0f}",
        "Delivered merchandise value",
    )

with c2:
    metric(
        "UNITS SOLD",
        f"{total_units:,}",
        "Delivered order items",
    )

with c3:
    metric(
        "UNIQUE PRODUCTS",
        f"{unique_products:,}",
        "Distinct product IDs",
    )

with c4:
    metric(
        "AVERAGE UNIT PRICE",
        f"R$ {average_unit_price:,.2f}",
        "Average delivered item price",
    )


st.divider()


# --------------------------------------------------
# PRODUCT REVENUE ANALYSIS
# --------------------------------------------------

left, right = st.columns([1.2, 1])

with left:

    st.subheader("Top 10 products by revenue")

    top_products = (
        delivered.groupby("product_id")
        .agg(
            revenue=("price", "sum"),
            units=("order_item_id", "count"),
        )
        .nlargest(10, "revenue")
        .sort_values("revenue")
        .reset_index()
    )

    # Short labels for better readability
    top_products["product_label"] = (
        top_products["product_id"].str[:12] + "..."
    )

    product_fig = px.bar(
        top_products,
        x="revenue",
        y="product_label",
        orientation="h",
        text_auto=".2s",
        hover_data={
            "product_id": True,
            "units": True,
            "product_label": False,
        },
    )

    product_fig.update_traces(
        marker_color=PALETTE["teal"],
        textposition="outside",
        cliponaxis=False,
        textfont=dict(
            size=12,
            color="#1F2937",
        ),
        hovertemplate=(
            "Product ID: %{customdata[0]}<br>"
            "Revenue: R$ %{x:,.2f}<br>"
            "<extra></extra>"
        ),
    )

    product_fig.update_layout(
        height=480,
        margin=dict(l=125, r=65, t=25, b=55),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            size=13,
            color="#1F2937",
        ),
        xaxis_title="Revenue (BRL)",
        yaxis_title="Product ID",
        showlegend=False,
        yaxis=dict(
            tickfont=dict(
                size=11,
                color="#1F2937",
            ),
            automargin=True,
        ),
        xaxis=dict(
            tickfont=dict(
                size=11,
                color="#1F2937",
            ),
            gridcolor="#E5E7EB",
        ),
    )

    st.plotly_chart(
        product_fig,
        use_container_width=True,
    )


# --------------------------------------------------
# CATEGORY SALES CONTRIBUTION
# --------------------------------------------------

with right:

    st.subheader("Category sales contribution")

    category_sales = (
        delivered.groupby("product_category_name")["price"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    category_sales.columns = ["category", "revenue"]

    # Top 10 categories + Other
    top_categories = category_sales.head(10).copy()

    other_revenue = category_sales.iloc[10:]["revenue"].sum()

    if other_revenue > 0:
        other_row = pd.DataFrame(
            [{
                "category": "other",
                "revenue": other_revenue,
            }]
        )

        category_sales_chart = pd.concat(
            [top_categories, other_row],
            ignore_index=True,
        )
    else:
        category_sales_chart = top_categories

    category_fig = px.pie(
        category_sales_chart,
        names="category",
        values="revenue",
        hole=0.55,
    )

    category_fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(
            size=12,
            color="#FFFFFF",
        ),
        hovertemplate=(
            "Category: %{label}<br>"
            "Revenue: R$ %{value:,.2f}<br>"
            "Contribution: %{percent}"
            "<extra></extra>"
        ),
    )

    category_fig.update_layout(
        height=480,
        margin=dict(l=25, r=25, t=25, b=110),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            size=12,
            color="#1F2937",
        ),
        legend=dict(
            title=dict(
                text="PRODUCT CATEGORY",
                font=dict(size=12, color="#1F2937"),
            ),
            font=dict(
                size=10,
                color="#1F2937",
            ),
            orientation="h",
            y=-0.22,
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
    )

    st.plotly_chart(
        category_fig,
        use_container_width=True,
    )


st.divider()


# --------------------------------------------------
# PRODUCT PERFORMANCE TABLE
# --------------------------------------------------

st.subheader("Product performance table")

product_table = (
    delivered.groupby(
        ["product_category_name", "product_id"]
    )
    .agg(
        units=("order_item_id", "count"),
        orders=("order_id", "nunique"),
        revenue=("price", "sum"),
        average_unit_price=("price", "mean"),
        freight_value=("freight_value", "sum"),
    )
    .reset_index()
    .sort_values("revenue", ascending=False)
)

product_table = product_table.rename(
    columns={
        "product_category_name": "category",
    }
)

product_table = product_table.head(100).copy()

product_table["revenue"] = product_table["revenue"].map(
    lambda value: f"R$ {value:,.2f}"
)

product_table["average_unit_price"] = (
    product_table["average_unit_price"].map(
        lambda value: f"R$ {value:,.2f}"
    )
)

product_table["freight_value"] = (
    product_table["freight_value"].map(
        lambda value: f"R$ {value:,.2f}"
    )
)

st.dataframe(
    product_table,
    use_container_width=True,
    hide_index=True,
    height=450,
    column_config={
        "category": st.column_config.TextColumn(
            "Category",
            width="medium",
        ),
        "product_id": st.column_config.TextColumn(
            "Product ID",
            width="large",
        ),
        "units": st.column_config.NumberColumn(
            "Units",
            format="%d",
        ),
        "orders": st.column_config.NumberColumn(
            "Orders",
            format="%d",
        ),
    },
)


# --------------------------------------------------
# BUSINESS INTERPRETATION
# --------------------------------------------------

st.divider()

st.subheader("Business interpretation")

if not product_table.empty:

    best_product = (
        delivered.groupby("product_id")["price"]
        .sum()
        .idxmax()
    )

    best_category = (
        category_sales.iloc[0]["category"]
        if not category_sales.empty
        else "N/A"
    )

    a, b = st.columns(2)

    with a:
        st.info(
            f"Top revenue-generating product ID: {best_product}"
        )

    with b:
        st.info(
            f"Highest revenue category: {best_category}"
        )


# --------------------------------------------------
# DATA SOURCE
# --------------------------------------------------

st.caption(
    "Source: Olist Brazilian E-Commerce Public Dataset. "
    "Revenue represents delivered merchandise item prices in BRL; "
    "freight is excluded from merchandise revenue. "
    "Product table displays the top 100 products by revenue."
)