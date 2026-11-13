from pathlib import Path
import logging
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "cleaned"
REPORTS = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

DATE_COLUMNS = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": ["shipping_limit_date"],
    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}

PRIMARY_KEYS = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": [
        "product_category_name"
    ],
    "olist_order_items_dataset.csv": [
        "order_id", "order_item_id"
    ],
    "olist_order_reviews_dataset.csv": ["order_id", "review_id"],
}

FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def load_raw(filename):
    path = RAW / filename

    if not path.exists():
        raise FileNotFoundError(path)

    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(
            path, encoding="latin-1", low_memory=False
        )


def clean_dataset(filename):
    logger.info("Cleaning %s", filename)

    df = load_raw(filename)
    original_rows = len(df)

    # Standardize column names.
    df.columns = df.columns.str.strip()

    # Remove leading/trailing whitespace from text fields.
    for col in df.select_dtypes(include=["object", "str"]).columns:
        df[col] = df[col].str.strip()

    # Parse timestamps without inventing missing values.
    for col in DATE_COLUMNS.get(filename, []):
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Remove only exact duplicate geolocation records.
    exact_duplicates_removed = 0

    if filename == "olist_geolocation_dataset.csv":
        exact_duplicates_removed = int(df.duplicated().sum())
        df = df.drop_duplicates().copy()

    # Validate expected business keys.
    keys = PRIMARY_KEYS.get(filename, [])

    if keys:
        duplicate_keys = int(df.duplicated(subset=keys).sum())

        if duplicate_keys:
            raise ValueError(
                f"{filename}: {duplicate_keys} duplicate key records. "
                "Resolve before exporting."
            )

    # Preserve missing product categories explicitly.
    if filename == "olist_products_dataset.csv":
        df["product_category_name"] = (
            df["product_category_name"].astype("string").fillna("unknown")
        )

    # Add chronology anomaly flags without changing timestamps.
    if filename == "olist_orders_dataset.csv":
        pairs = [
            ("order_purchase_timestamp", "order_approved_at"),
            ("order_approved_at", "order_delivered_carrier_date"),
            (
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
            ),
        ]

        for earlier, later in pairs:
            df[f"quality_flag_{later}"] = (
                df[earlier].notna()
                & df[later].notna()
                & (df[later] < df[earlier])
            )

    CLEAN.mkdir(parents=True, exist_ok=True)
    output = CLEAN / filename
    df.to_csv(output, index=False)

    return {
        "dataset": filename,
        "original_rows": original_rows,
        "cleaned_rows": len(df),
        "rows_removed": original_rows - len(df),
        "exact_duplicates_removed": exact_duplicates_removed,
        "remaining_missing_cells": int(df.isna().sum().sum()),
        "status": "SUCCESS",
    }


def run_cleaning():
    CLEAN.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    summaries = []

    for filename in FILES:
        summaries.append(clean_dataset(filename))

    report = pd.DataFrame(summaries)

    report.to_csv(
        REPORTS / "data_cleaning_summary.csv",
        index=False
    )

    print("\n========== CLEANING SUMMARY ==========")
    print(report.to_string(index=False))
    print("\nAll cleaned datasets exported successfully.")


if __name__ == "__main__":
    run_cleaning()
