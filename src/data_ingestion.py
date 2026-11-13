from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports"

DATASETS = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_geolocation_dataset.csv": [],
    "olist_order_items_dataset.csv": [],
    "olist_order_payments_dataset.csv": [],
    "olist_order_reviews_dataset.csv": [],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"],
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_csv(path: Path) -> pd.DataFrame:
    """Load one raw CSV without modifying the source file."""
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        logger.warning("UTF-8 decoding failed for %s. Retrying with Latin-1.", path.name)
        return pd.read_csv(path, encoding="latin-1", low_memory=False)


def inspect_dataset(filename: str, primary_keys: list[str]) -> tuple[dict, list[dict]]:
    path = RAW_DIR / filename

    if not path.is_file():
        raise FileNotFoundError(f"Required dataset not found: {path}")

    logger.info("Loading %s", filename)
    df = load_csv(path)

    missing_keys = [key for key in primary_keys if key not in df.columns]
    if missing_keys:
        raise ValueError(f"{filename}: missing expected keys: {missing_keys}")

    duplicate_key_rows = (
        int(df.duplicated(subset=primary_keys).sum())
        if primary_keys else None
    )

    summary = {
        "dataset": filename,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "duplicate_key_rows": duplicate_key_rows,
        "missing_cells": int(df.isna().sum().sum()),
        "missing_percentage": round(
            df.isna().sum().sum() / max(df.size, 1) * 100, 2
        ),
        "memory_mb": round(
            df.memory_usage(index=True, deep=True).sum() / (1024 ** 2), 2
        ),
        "status": "SUCCESS",
    }

    column_profiles = []

    for column in df.columns:
        missing = int(df[column].isna().sum())

        column_profiles.append({
            "dataset": filename,
            "column": column,
            "dtype": str(df[column].dtype),
            "missing_count": missing,
            "missing_percentage": round(
                missing / max(len(df), 1) * 100, 2
            ),
            "unique_values": int(df[column].nunique(dropna=True)),
        })

    logger.info(
        "Completed %s | rows=%s | columns=%s | missing=%s",
        filename, len(df), len(df.columns), summary["missing_cells"]
    )

    return summary, column_profiles


def run_ingestion() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = []
    profiles = []
    failures = []

    for filename, primary_keys in DATASETS.items():
        try:
            summary, profile = inspect_dataset(filename, primary_keys)
            summaries.append(summary)
            profiles.extend(profile)
        except Exception as exc:
            logger.exception("Failed processing %s", filename)
            failures.append({
                "dataset": filename,
                "error": str(exc),
            })

    if summaries:
        pd.DataFrame(summaries).to_csv(
            REPORT_DIR / "data_ingestion_summary.csv", index=False
        )

        pd.DataFrame(profiles).to_csv(
            REPORT_DIR / "column_profile.csv", index=False
        )

    if failures:
        pd.DataFrame(failures).to_csv(
            REPORT_DIR / "data_ingestion_errors.csv", index=False
        )

    logger.info(
        "Ingestion finished: %s successful, %s failed",
        len(summaries), len(failures)
    )

    if failures:
        raise RuntimeError(
            f"Ingestion incomplete: {len(failures)} dataset(s) failed."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Profile the raw Olist e-commerce datasets."
    )
    parser.parse_args()
    run_ingestion()
