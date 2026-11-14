import pandas as pd
import pytest

from src import build_analytics as analytics


def test_payment_summary_aggregates_by_order(monkeypatch):
    payments = pd.DataFrame({
        "order_id": ["O1", "O1", "O2"],
        "payment_sequential": [1, 2, 1],
        "payment_type": ["credit_card", "voucher", "credit_card"],
        "payment_installments": [2, 1, 3],
        "payment_value": [100.0, 20.0, 50.0],
    })

    monkeypatch.setattr(
        analytics, "load_data", lambda _: payments
    )

    result = analytics.build_payment_summary().set_index("order_id")

    assert result.loc["O1", "total_payment_value"] == 120.0
    assert result.loc["O1", "payment_count"] == 2
    assert result.loc["O1", "max_installments"] == 2
    assert result.loc["O1", "payment_methods"] == "credit_card | voucher"
    assert result.loc["O2", "total_payment_value"] == 50.0


def test_review_summary_aggregates_by_order(monkeypatch):
    reviews = pd.DataFrame({
        "order_id": ["O1", "O1", "O2"],
        "review_score": [5, 3, 4],
    })

    monkeypatch.setattr(
        analytics, "load_data", lambda _: reviews
    )

    result = analytics.build_review_summary().set_index("order_id")

    assert result.loc["O1", "review_count"] == 2
    assert result.loc["O1", "average_review_score"] == 4.0
    assert result.loc["O1", "review_score_min"] == 3
    assert result.loc["O1", "review_score_max"] == 5


def test_review_summary_preserves_missing_scores(monkeypatch):
    reviews = pd.DataFrame({
        "order_id": ["O1"],
        "review_score": [None],
    })

    monkeypatch.setattr(
        analytics, "load_data", lambda _: reviews
    )

    result = analytics.build_review_summary()

    assert result.loc[0, "review_count"] == 0
    assert pd.isna(result.loc[0, "average_review_score"])


def test_fact_table_preserves_rows_and_financial_totals(
    tmp_path, monkeypatch
):
    datasets = {
        "olist_order_items_dataset.csv": pd.DataFrame({
            "order_id": ["O1", "O1", "O2"],
            "order_item_id": [1, 2, 1],
            "product_id": ["P1", "P2", "P1"],
            "seller_id": ["S1", "S1", "S2"],
            "price": [100.0, 50.0, 75.0],
            "freight_value": [10.0, 5.0, 7.0],
        }),
        "olist_orders_dataset.csv": pd.DataFrame({
            "order_id": ["O1", "O2"],
            "customer_id": ["C1", "C2"],
            "order_status": ["delivered", "delivered"],
        }),
        "olist_customers_dataset.csv": pd.DataFrame({
            "customer_id": ["C1", "C2"],
            "customer_unique_id": ["U1", "U2"],
        }),
        "olist_products_dataset.csv": pd.DataFrame({
            "product_id": ["P1", "P2"],
            "product_category_name": ["cat1", "cat2"],
        }),
        "olist_sellers_dataset.csv": pd.DataFrame({
            "seller_id": ["S1", "S2"],
            "seller_city": ["City A", "City B"],
        }),
        "olist_order_payments_dataset.csv": pd.DataFrame({
            "order_id": ["O1", "O1", "O2"],
            "payment_sequential": [1, 2, 1],
            "payment_type": ["credit_card", "voucher", "credit_card"],
            "payment_installments": [2, 1, 3],
            "payment_value": [150.0, 15.0, 82.0],
        }),
        "olist_order_reviews_dataset.csv": pd.DataFrame({
            "order_id": ["O1", "O1", "O2"],
            "review_score": [5, 3, 4],
        }),
    }

    monkeypatch.setattr(
        analytics, "load_data", lambda filename: datasets[filename]
    )
    monkeypatch.setattr(analytics, "DATA", tmp_path / "cleaned")
    monkeypatch.setattr(analytics, "REPORTS", tmp_path / "reports")

    result = analytics.build_fact_table()

    assert len(result) == 3
    assert not result.duplicated(["order_id", "order_item_id"]).any()
    assert result["price"].sum() == 225.0
    assert result["freight_value"].sum() == 22.0

    # Order-level payment values are repeated across their items.
    assert result.loc[result["order_id"] == "O1", "total_payment_value"].tolist() == [
        165.0, 165.0
    ]

    assert (tmp_path / "cleaned" / "fact_order_items.csv").exists()
    assert (tmp_path / "reports" / "analytics_build_audit.csv").exists()


def test_fact_table_rejects_duplicate_item_keys(monkeypatch):
    items = pd.DataFrame({
        "order_id": ["O1", "O1"],
        "order_item_id": [1, 1],
        "product_id": ["P1", "P1"],
        "seller_id": ["S1", "S1"],
        "price": [10.0, 10.0],
        "freight_value": [2.0, 2.0],
    })

    monkeypatch.setattr(
        analytics, "load_data",
        lambda filename: items if filename == "olist_order_items_dataset.csv"
        else pd.DataFrame()
    )

    with pytest.raises(ValueError, match="Duplicate order-item keys"):
        analytics.build_fact_table()
