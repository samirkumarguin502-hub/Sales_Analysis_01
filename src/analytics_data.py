from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
FACT_PATH = ROOT / "data" / "cleaned" / "fact_order_items.csv"


@st.cache_data(show_spinner="Loading Olist analytics data...")
def load_analytics_data():
    if not FACT_PATH.exists():
        raise FileNotFoundError(
            f"Analytics fact table not found: {FACT_PATH}. "
            "Run: python -m src.build_analytics"
        )

    df = pd.read_csv(FACT_PATH, low_memory=False)

    required_columns = [
        "order_id",
        "order_item_id",
        "price",
        "freight_value",
        "order_status",
        "order_purchase_timestamp",
        "product_category_name",
        "customer_unique_id",
        "seller_id",
        "total_payment_value",
        "review_count",
        "average_review_score",
    ]

    missing = sorted(set(required_columns) - set(df.columns))

    if missing:
        raise ValueError(
            f"Fact table is missing required columns: {missing}"
        )

    df["order_purchase_timestamp"] = pd.to_datetime(
        df["order_purchase_timestamp"],
        errors="coerce",
    )

    df["order_purchase_month"] = (
        df["order_purchase_timestamp"]
        .dt.to_period("M")
        .astype("string")
    )

    df["item_revenue"] = df["price"]
    df["gross_item_value"] = df["price"] + df["freight_value"]

    df["product_category_name"] = (
        df["product_category_name"].fillna("unknown")
    )

    return df
