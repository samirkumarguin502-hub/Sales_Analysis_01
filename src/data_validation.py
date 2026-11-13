from pathlib import Path
import logging
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

def load(name):
    return pd.read_csv(RAW / name, low_memory=False)

def run_validation():
    REPORTS.mkdir(exist_ok=True)

    customers = load("olist_customers_dataset.csv")
    orders = load("olist_orders_dataset.csv")
    items = load("olist_order_items_dataset.csv")
    payments = load("olist_order_payments_dataset.csv")
    reviews = load("olist_order_reviews_dataset.csv")
    products = load("olist_products_dataset.csv")
    sellers = load("olist_sellers_dataset.csv")
    geo = load("olist_geolocation_dataset.csv")
    translations = load("product_category_name_translation.csv")

    results = []

    def record(check, dataset, value, severity, details):
        results.append({
            "check": check,
            "dataset": dataset,
            "value": int(value),
            "severity": severity,
            "details": details
        })

    # 1. Primary key uniqueness
    for df, name, key in [
        (customers, "customers", "customer_id"),
        (orders, "orders", "order_id"),
        (products, "products", "product_id"),
        (sellers, "sellers", "seller_id"),
        (reviews, "reviews", "review_id"),
    ]:
        record(
            "Duplicate primary keys", name,
            df.duplicated(subset=[key]).sum(),
            "WARNING",
            f"Expected unique key: {key}"
        )

    # 2. Composite key validation
    record(
        "Duplicate composite keys",
        "order_items",
        items.duplicated(["order_id", "order_item_id"]).sum(),
        "WARNING",
        "Expected unique combination: order_id + order_item_id"
    )

    # 3. Foreign key integrity
    relationships = [
        (orders, "customer_id", customers, "customer_id", "orders"),
        (items, "order_id", orders, "order_id", "order_items"),
        (items, "product_id", products, "product_id", "order_items"),
        (items, "seller_id", sellers, "seller_id", "order_items"),
        (payments, "order_id", orders, "order_id", "payments"),
        (reviews, "order_id", orders, "order_id", "reviews"),
    ]

    for child, child_key, parent, parent_key, name in relationships:
        orphan_count = (
            ~child[child_key].isin(parent[parent_key].dropna())
            & child[child_key].notna()
        ).sum()

        record(
            "Orphan foreign keys", name,
            orphan_count, "CRITICAL",
            f"{child_key} must match {parent_key}"
        )

    # 4. Missing values
    for name, df in [
        ("orders", orders),
        ("products", products),
        ("reviews", reviews),
        ("customers", customers),
        ("order_items", items),
    ]:
        record(
            "Missing cells", name,
            df.isna().sum().sum(),
            "INFO",
            "Inspect column-level profile before treatment"
        )

    # 5. Review score validation
    invalid_scores = (
        ~reviews["review_score"].between(1, 5)
    ).sum()

    record(
        "Invalid review scores", "reviews",
        invalid_scores, "WARNING",
        "Valid score range: 1 to 5"
    )

    # 6. Order status distribution
    record(
        "Unknown order statuses", "orders",
        (~orders["order_status"].isin([
            "delivered", "shipped", "canceled",
            "unavailable", "invoiced", "processing",
            "created", "approved"
        ])).sum(),
        "WARNING",
        "Check unexpected order_status values"
    )

    # 7. Timestamp consistency
    date_pairs = [
        ("order_purchase_timestamp", "order_approved_at"),
        ("order_approved_at", "order_delivered_carrier_date"),
        ("order_delivered_carrier_date", "order_delivered_customer_date"),
    ]

    for earlier, later in date_pairs:
        a = pd.to_datetime(orders[earlier], errors="coerce")
        b = pd.to_datetime(orders[later], errors="coerce")

        invalid = (a.notna() & b.notna() & (b < a)).sum()

        record(
            "Invalid timestamp sequence",
            "orders", invalid, "WARNING",
            f"{later} should not precede {earlier}"
        )

    # 8. Product category translation coverage
    mapped = set(translations["product_category_name"].dropna())

    unmapped = (
        products["product_category_name"].notna()
        & ~products["product_category_name"].isin(mapped)
    ).sum()

    record(
        "Unmapped product categories",
        "products", unmapped, "WARNING",
        "Categories without English translation"
    )

    # 9. Geolocation duplicate investigation
    record(
        "Exact duplicate rows",
        "geolocation",
        geo.duplicated().sum(),
        "INFO",
        "Investigate before deduplication; no business key assumed"
    )

    report = pd.DataFrame(results)
    report.to_csv(REPORTS / "data_quality_audit.csv", index=False)

    print("\n========== DATA QUALITY AUDIT ==========")
    print(report.to_string(index=False))
    print("\nAudit report saved successfully.")
    print(REPORTS / "data_quality_audit.csv")

    return report


if __name__ == "__main__":
    run_validation()
