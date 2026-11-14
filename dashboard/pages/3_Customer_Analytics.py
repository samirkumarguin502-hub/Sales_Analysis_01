import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import plotly.express as px
import pandas as pd

from src.analytics_data import load_analytics_data
from dashboard.style import apply_style, header, metric, PALETTE


st.set_page_config(
    page_title="Customer Analytics | CommerceIQ",
    layout="wide",
)

apply_style()

df = load_analytics_data()

header(
    "Customer analytics",
    "Understand customer retention, purchasing behaviour and geographic demand across Olist.",
    "ANALYTICS / CUSTOMERS",
)

# --------------------------------------------------
# 1. DELIVERED ORDER DATA
# --------------------------------------------------

delivered = df[
    df["order_status"].eq("delivered")
].copy()

if delivered.empty:
    st.warning("No delivered order records are available.")
    st.stop()

# --------------------------------------------------
# 2. CUSTOMER LEVEL AGGREGATION
# --------------------------------------------------

customers = (
    delivered.groupby("customer_unique_id")
    .agg(
        orders=("order_id", "nunique"),
        revenue=("price", "sum"),
        last_order=("order_purchase_timestamp", "max"),
        city=("customer_city", "first"),
        state=("customer_state", "first"),
    )
    .reset_index()
)

customers["revenue"] = customers["revenue"].round(2)

total_customers = len(customers)

repeat_customers = int(
    (customers["orders"] > 1).sum()
)

repeat_rate = (
    repeat_customers / total_customers
    if total_customers else 0
)

total_revenue = delivered["price"].sum()

average_revenue = (
    total_revenue / total_customers
    if total_customers else 0
)

# --------------------------------------------------
# 3. KPI OVERVIEW
# --------------------------------------------------

st.subheader("Customer performance overview")

a, b, c, d = st.columns(4)

with a:
    metric(
        "UNIQUE CUSTOMERS",
        f"{total_customers:,}",
        "Customers with delivered orders",
    )

with b:
    metric(
        "REPEAT CUSTOMERS",
        f"{repeat_customers:,}",
        f"{repeat_rate:.1%} repeat customer rate",
    )

with c:
    metric(
        "CUSTOMER REVENUE",
        f"R$ {total_revenue:,.0f}",
        "Delivered merchandise value",
    )

with d:
    metric(
        "REVENUE PER CUSTOMER",
        f"R$ {average_revenue:,.2f}",
        "Average delivered merchandise value",
    )

st.divider()

# --------------------------------------------------
# 4. CUSTOMER ORDER FREQUENCY
# 5. REVENUE BY CUSTOMER CITY
# --------------------------------------------------

left, right = st.columns(2, gap="large")

with left:

    st.subheader("Customer order frequency")

    frequency = (
        customers["orders"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    frequency.columns = ["orders", "customers"]

    fig = px.bar(
        frequency,
        x="orders",
        y="customers",
        text="customers",
        labels={
            "orders": "Delivered orders per customer",
            "customers": "Number of customers",
        },
    )

    fig.update_traces(
        marker_color="#147D78",
        texttemplate="%{text:,.0f}",
        textposition="outside",
        cliponaxis=False,
        textfont=dict(
            size=11,
            color="#1F2937",
        ),
    )

    fig.update_layout(
        template="plotly_white",
        height=440,
        margin=dict(
            l=75,
            r=55,
            t=35,
            b=85,
        ),
        font=dict(
            family="Arial",
            size=13,
            color="#1F2937",
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
        xaxis=dict(
            title=dict(
                text="Delivered orders per customer",
                font=dict(size=13, color="#1F2937"),
            ),
            tickfont=dict(
                size=12,
                color="#1F2937",
            ),
            showgrid=False,
            automargin=True,
            dtick=1,
        ),
        yaxis=dict(
            title=dict(
                text="Number of customers",
                font=dict(size=13, color="#1F2937"),
            ),
            tickfont=dict(
                size=12,
                color="#1F2937",
            ),
            showgrid=True,
            gridcolor="#E5E7EB",
            automargin=True,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


with right:

    st.subheader("Revenue by customer city")

    city_revenue = (
        delivered.groupby("customer_city")["price"]
        .sum()
        .nlargest(10)
        .sort_values()
        .reset_index()
    )

    fig = px.bar(
        city_revenue,
        x="price",
        y="customer_city",
        orientation="h",
        text="price",
        labels={
            "price": "Revenue (BRL)",
            "customer_city": "Customer city",
        },
    )

    fig.update_traces(
        marker_color="#147D78",
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        cliponaxis=False,
        textfont=dict(
            size=11,
            color="#1F2937",
        ),
    )

    fig.update_layout(
        template="plotly_white",
        height=440,
        margin=dict(
            l=145,
            r=100,
            t=35,
            b=65,
        ),
        font=dict(
            family="Arial",
            size=13,
            color="#1F2937",
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        showlegend=False,
        xaxis=dict(
            title=dict(
                text="Revenue (BRL)",
                font=dict(size=13, color="#1F2937"),
            ),
            tickfont=dict(
                size=12,
                color="#1F2937",
            ),
            showgrid=True,
            gridcolor="#E5E7EB",
            automargin=True,
        ),
        yaxis=dict(
            title="",
            tickfont=dict(
                size=12,
                color="#1F2937",
            ),
            showgrid=False,
            automargin=True,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

st.divider()

# --------------------------------------------------
# 6. HIGHEST VALUE CUSTOMERS
# --------------------------------------------------

st.subheader("Highest-value customers")

top_customers = (
    customers.sort_values(
        "revenue",
        ascending=False,
    )
    .head(15)
    .copy()
)

top_customers = top_customers.rename(
    columns={
        "customer_unique_id": "Customer ID",
        "orders": "Delivered Orders",
        "revenue": "Revenue (BRL)",
        "last_order": "Last Purchase",
        "city": "City",
        "state": "State",
    }
)

top_customers["Revenue (BRL)"] = (
    top_customers["Revenue (BRL)"]
    .map(lambda value: f"R$ {value:,.2f}")
)

top_customers["Last Purchase"] = (
    pd.to_datetime(
        top_customers["Last Purchase"]
    ).dt.strftime("%d %b %Y")
)

st.dataframe(
    top_customers[
        [
            "Customer ID",
            "City",
            "State",
            "Delivered Orders",
            "Revenue (BRL)",
            "Last Purchase",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

# --------------------------------------------------
# 7. BUSINESS INTERPRETATION
# --------------------------------------------------

st.divider()

st.subheader("Business interpretation")

best_customer = customers.loc[
    customers["revenue"].idxmax()
]

col1, col2 = st.columns(2)

with col1:
    st.info(
        f"**Highest-value customer:** "
        f"{best_customer['customer_unique_id']}"
    )

with col2:
    st.info(
        f"**Repeat customer rate:** {repeat_rate:.1%}"
    )

# --------------------------------------------------
# 8. DATA SOURCE
# --------------------------------------------------

st.caption(
    "Source: Olist Brazilian E-Commerce Public Dataset. "
    "Customer metrics use customer_unique_id. "
    "Revenue represents delivered merchandise item prices in BRL; "
    "freight is excluded. Only delivered orders are included."
)