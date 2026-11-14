import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import plotly.express as px
from dashboard.style import apply_style, metric, PALETTE
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import plotly.express as px

from src.analytics_data import load_analytics_data
from dashboard.style import apply_style, metric, PALETTE


st.set_page_config(
    page_title="CommerceIQ | Business Intelligence",
    page_icon="◈",
    layout="wide",
)

def make_chart_readable(fig):
    fig.update_layout(
        font=dict(family="Arial, sans-serif", size=14, color="#172B4D"),
        legend=dict(font=dict(size=13, color="#172B4D")),
    )
    fig.update_xaxes(
        tickfont=dict(size=13, color="#172B4D"),
        title=dict(font=dict(size=14, color="#172B4D")),
    )
    fig.update_yaxes(
        tickfont=dict(size=13, color="#172B4D"),
        title=dict(font=dict(size=14, color="#172B4D")),
    )
    return fig

apply_style()
df = load_analytics_data()

# Sidebar
st.sidebar.markdown(
    '''
    <div style="padding:10px 4px 24px">
        <div style="font-size:11px;letter-spacing:.16em;color:#7FD6C5;font-weight:800">
            ◈ COMMERCEIQ
        </div>
        <div style="font-family:Manrope;font-size:20px;font-weight:800;color:white;margin-top:6px">
            Business Intelligence
        </div>
        <div style="font-size:11px;color:#AFC0D3;margin-top:5px">
            E-commerce analytics workspace
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

st.sidebar.markdown("### WORKSPACE")

valid_dates = df["order_purchase_timestamp"].dropna()

if valid_dates.empty:
    st.error("No valid order purchase dates found in the fact table.")
    st.stop()

min_date = valid_dates.min().date()
max_date = valid_dates.max().date()

date_range = st.sidebar.date_input(
    "Order purchase date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

categories = sorted(df["product_category_name"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Product categories",
    categories,
    default=categories,
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    '''
    <div style="font-size:11px;color:#91A6BC">DATA SOURCE</div>
    <div style="font-weight:600;margin-top:5px">Olist Brazilian E-Commerce</div>
    <div style="font-size:10px;color:#91A6BC;margin-top:4px">
        Historical dataset · 2016–2018 · Currency BRL
    </div>
    ''',
    unsafe_allow_html=True,
)

# Apply filters
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["order_purchase_timestamp"].dt.date.between(start_date, end_date)
    & df["product_category_name"].isin(selected_categories)
].copy()

if filtered.empty:
    st.warning("No records found for the selected filters.")
    st.stop()

# Delivered-order metrics
delivered = filtered[
    filtered["order_status"].eq("delivered")
].copy()

revenue = delivered["price"].sum()
orders = delivered["order_id"].nunique()
aov = revenue / orders if orders else 0
units = len(delivered)

# Hero
st.markdown(
    f'''
    <div class="hero">
        <div style="font-size:11px;letter-spacing:.15em;font-weight:700;color:#A9E4D8">
            EXECUTIVE OVERVIEW / OLIST DATA
        </div>
        <h1>See the story behind every order.</h1>
        <p>A unified view of revenue performance, product demand and customer behaviour.</p>
        <div style="margin-top:18px">
            <span style="background:#FFFFFF20;border:1px solid #FFFFFF35;border-radius:20px;padding:6px 11px;font-size:11px">
                ● REAL DATASET — OLIST BRAZILIAN E-COMMERCE
            </span>
        </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# KPI cards
c1, c2, c3, c4 = st.columns(4)

with c1:
    metric("DELIVERED SALES REVENUE", f"R$ {revenue:,.0f}", "Delivered item prices")

with c2:
    metric("DELIVERED ORDERS", f"{orders:,}", "Unique delivered orders")

with c3:
    metric("AVERAGE ORDER VALUE", f"R$ {aov:,.2f}", "Merchandise revenue per order")

with c4:
    metric("ITEMS SOLD", f"{units:,}", "Delivered order items")

# Revenue trend and category performance
left, right = st.columns([1.55, 1])

with left:
    st.markdown(
        '<div class="section-head"><h3>Revenue performance</h3>'
        '<span class="tag">MONTHLY TREND</span></div>',
        unsafe_allow_html=True,
    )

    monthly = (
        delivered.groupby("order_purchase_month", dropna=True)["price"]
        .sum()
        .reset_index(name="revenue")
        .sort_values("order_purchase_month")
    )

    fig = px.area(
        monthly,
        x="order_purchase_month",
        y="revenue",
        markers=True,
    )

    fig.update_traces(
        line_color=PALETTE["teal"],
        fillcolor="rgba(15,118,110,.12)",
        hovertemplate="%{x}<br>R$ %{y:,.2f}<extra></extra>",
    )

    fig.update_layout(
        height=320,
        margin=dict(l=5, r=5, t=15, b=5),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=14, color="#172B4D"),
        xaxis_title="",
        yaxis_title="Revenue (BRL)",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#EEF1F5", zeroline=False)

    st.plotly_chart(make_chart_readable(fig), use_container_width=True)

with right:
    st.markdown(
        '<div class="section-head"><h3>Revenue by category</h3></div>',
        unsafe_allow_html=True,
    )

    category_sales = (
        delivered.groupby("product_category_name")["price"]
        .sum()
        .sort_values(ascending=True)
        .tail(10)
        .reset_index()
    )

    fig2 = px.bar(
        category_sales,
        x="price",
        y="product_category_name",
        orientation="h",
        text_auto=".2s",
    )

    fig2.update_traces(
        marker_color=PALETTE["teal"],
        textposition="outside",
        cliponaxis=False,
    )

    fig2.update_layout(
        height=320,
        margin=dict(l=5, r=35, t=15, b=5),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=14, color="#172B4D"),
        xaxis_title="Revenue (BRL)",
        yaxis_title="",
        showlegend=False,
    )

    fig2.update_xaxes(showgrid=True, gridcolor="#EEF1F5")
    fig2.update_yaxes(showgrid=False)

    st.plotly_chart(make_chart_readable(fig2), use_container_width=True)


# Product and customer insights
st.markdown(
    '<div class="section-head"><h3>Product & customer pulse</h3>'
    '<span class="small-muted">Based on current filters</span></div>',
    unsafe_allow_html=True,
)

a, b, c = st.columns(3)

with a:
    top_products = (
        delivered.groupby("product_id")["price"]
        .sum()
        .nlargest(5)
        .sort_values()
        .reset_index()
    )

    f = px.bar(
        top_products,
        x="price",
        y="product_id",
        orientation="h",
        title="Top products by sales",
        text_auto=".2s",
    )
    f.update_layout(
        height=270,
        margin=dict(l=0, r=10, t=45, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=14, color="#172B4D"),
        xaxis_title="Revenue (BRL)",
        yaxis_title="",
    )
    f.update_traces(marker_color="#E5A93D")
    st.plotly_chart(make_chart_readable(f), use_container_width=True)

with b:
    payment_data = (
        filtered.groupby("order_id")
        .agg(payment_methods=("payment_methods", "first"))
        .reset_index()
    )

    payment_data["payment_methods"] = (
        payment_data["payment_methods"]
        .fillna("Unknown")
        .str.split(",")
    )

    payment_data = payment_data.explode("payment_methods")
    payment_counts = payment_data["payment_methods"].value_counts().reset_index()
    payment_counts.columns = ["payment_method", "orders"]

    f = px.pie(
        payment_counts,
        names="payment_method",
        values="orders",
        hole=0.62,
        title="Payment method mix",
    )
    f.update_layout(
        height=270,
        margin=dict(l=0, r=0, t=45, b=0),
        paper_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=14, color="#172B4D"),
        legend_title="",
    )
    st.plotly_chart(make_chart_readable(f), use_container_width=True)

with c:
    city_data = (
        filtered.groupby("customer_city")["order_id"]
        .nunique()
        .nlargest(5)
        .sort_values()
        .reset_index(name="orders")
    )

    f = px.bar(
        city_data,
        x="orders",
        y="customer_city",
        orientation="h",
        title="Top cities by order volume",
        text_auto=True,
    )
    f.update_layout(
        height=270,
        margin=dict(l=0, r=10, t=45, b=0),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", size=14, color="#172B4D"),
        xaxis_title="Orders",
        yaxis_title="",
    )
    f.update_traces(marker_color="#6E8B78")
    st.plotly_chart(make_chart_readable(f), use_container_width=True)

# Latest transactions
st.markdown(
    '<div class="section-head"><h3>Latest transactions</h3>'
    '<span class="tag">OLIST DATA</span></div>',
    unsafe_allow_html=True,
)

show = (
    filtered.sort_values("order_purchase_timestamp", ascending=False)
    .drop_duplicates("order_id")
    .head(8)[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_status",
            "customer_city",
            "price",
        ]
    ]
    .copy()
)

show["order_purchase_timestamp"] = (
    show["order_purchase_timestamp"].dt.strftime("%d %b %Y")
)
show["price"] = show["price"].map(lambda value: f"R$ {value:,.2f}")

st.dataframe(show, hide_index=True, use_container_width=True)

st.caption(
    "Source: Olist Brazilian E-Commerce Public Dataset. "
    "Revenue represents item merchandise prices for delivered order items; "
    "freight is excluded. Orders without item records are not represented."
)
