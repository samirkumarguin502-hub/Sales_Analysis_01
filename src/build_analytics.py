from pathlib import Path
import logging
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cleaned"
REPORTS = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def load_data(filename):
    path = DATA / filename

    if not path.exists():
        raise FileNotFoundError(path)

    return pd.read_csv(path, low_memory=False)


def build_payment_summary():
    payments = load_data("olist_order_payments_dataset.csv")

    summary = payments.groupby("order_id").agg(
        total_payment_value=("payment_value", "sum"),
        payment_count=("payment_sequential", "count"),
        max_installments=("payment_installments", "max"),
        payment_methods=("payment_type", lambda x: " | ".join(
            sorted(x.dropna().astype(str).unique())
        )),
    ).reset_index()

    return summary


def build_review_summary():
    reviews = load_data("olist_order_reviews_dataset.csv")

    summary = reviews.groupby("order_id").agg(
        review_count=("review_score", "count"),
        average_review_score=("review_score", "mean"),
        review_score_min=("review_score", "min"),
        review_score_max=("review_score", "max"),
    ).reset_index()

    return summary


def build_fact_table():
    logger.info("Loading base order-item data")

    items = load_data("olist_order_items_dataset.csv")
    orders = load_data("olist_orders_dataset.csv")
    customers = load_data("olist_customers_dataset.csv")
    products = load_data("olist_products_dataset.csv")
    sellers = load_data("olist_sellers_dataset.csv")

    original_rows = len(items)
    original_item_revenue = items["price"].sum()
    original_freight = items["freight_value"].sum()

    if items.duplicated(["order_id", "order_item_id"]).any():
        raise ValueError("Duplicate order-item keys detected")

    logger.info("Joining order information")

    fact = items.merge(
        orders,
        on="order_id",
        how="left",
        validate="many_to_one",
        indicator="_orders_merge",
    )

    if not fact["_orders_merge"].eq("both").all():
        raise ValueError("Some order items have no matching order")

    fact = fact.drop(columns="_orders_merge")

    logger.info("Joining customer information")

    fact = fact.merge(
        customers,
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    logger.info("Joining product information")

    fact = fact.merge(
        products,
        on="product_id",
        how="left",
        validate="many_to_one",
    )

    logger.info("Joining seller information")

    fact = fact.merge(
        sellers,
        on="seller_id",
        how="left",
        validate="many_to_one",
    )

    logger.info("Aggregating and joining payments")

    payment_summary = build_payment_summary()

    fact = fact.merge(
        payment_summary,
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    logger.info("Aggregating and joining reviews")

    review_summary = build_review_summary()

    fact = fact.merge(
        review_summary,
        on="order_id",
        how="left",
        validate="many_to_one",
    )

    if len(fact) != original_rows:
        raise ValueError(
            f"Row count changed: {original_rows} -> {len(fact)}"
        )

    if not fact["price"].sum() == original_item_revenue:
        raise ValueError("Item revenue reconciliation failed")

    if not fact["freight_value"].sum() == original_freight:
        raise ValueError("Freight reconciliation failed")

    if fact.duplicated(["order_id", "order_item_id"]).any():
        raise ValueError("Duplicate item keys after joining")

    DATA.mkdir(parents=True, exist_ok=True)
    output = DATA / "fact_order_items.csv"
    fact.to_csv(output, index=False)

    REPORTS.mkdir(parents=True, exist_ok=True)

    audit = pd.DataFrame([
        {"metric": "source_order_items", "value": original_rows},
        {"metric": "final_fact_rows", "value": len(fact)},
        {"metric": "source_item_revenue", "value": original_item_revenue},
        {"metric": "final_item_revenue", "value": fact["price"].sum()},
        {"metric": "source_freight", "value": original_freight},
        {"metric": "final_freight", "value": fact["freight_value"].sum()},
        {"metric": "unique_orders", "value": fact["order_id"].nunique()},
        {"metric": "unique_products", "value": fact["product_id"].nunique()},
        {"metric": "unique_sellers", "value": fact["seller_id"].nunique()},
    ])

    audit.to_csv(REPORTS / "analytics_build_audit.csv", index=False)

    logger.info("Fact table successfully created: %s", output)
    logger.info("Final rows: %s | Columns: %s", len(fact), len(fact.columns))

    return fact


if __name__ == "__main__":
    build_fact_table()
