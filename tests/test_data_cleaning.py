import pandas as pd
import pytest

from src import data_cleaning as cleaning


def test_geolocation_removes_only_exact_duplicates(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "geolocation_zip_code_prefix": [1000, 1000, 2000],
        "geolocation_lat": [10.0, 10.0, 20.0],
        "geolocation_lng": [30.0, 30.0, 40.0],
        "geolocation_city": [" City A ", " City A ", "City B"],
        "geolocation_state": ["SP", "SP", "RJ"],
    })

    source.to_csv(raw_dir / "olist_geolocation_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    result = cleaning.clean_dataset("olist_geolocation_dataset.csv")
    cleaned = pd.read_csv(
        clean_dir / "olist_geolocation_dataset.csv"
    )

    assert result["original_rows"] == 3
    assert result["cleaned_rows"] == 2
    assert result["exact_duplicates_removed"] == 1
    assert len(cleaned) == 2
    assert cleaned["geolocation_city"].tolist() == ["City A", "City B"]


def test_duplicate_primary_key_raises_error(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "customer_id": ["C1", "C1"],
        "customer_unique_id": ["U1", "U2"],
        "customer_zip_code_prefix": [1000, 2000],
        "customer_city": ["City A", "City B"],
        "customer_state": ["SP", "RJ"],
    })

    source.to_csv(raw_dir / "olist_customers_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    with pytest.raises(ValueError, match="duplicate key records"):
        cleaning.clean_dataset("olist_customers_dataset.csv")


def test_review_composite_key_is_validated(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "review_id": ["R1", "R1"],
        "order_id": ["O1", "O2"],
        "review_score": [5, 4],
        "review_comment_title": [None, None],
        "review_comment_message": [None, None],
        "review_creation_date": [
            "2018-01-01 00:00:00",
            "2018-01-02 00:00:00",
        ],
        "review_answer_timestamp": [
            "2018-01-02 00:00:00",
            "2018-01-03 00:00:00",
        ],
    })

    source.to_csv(raw_dir / "olist_order_reviews_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    result = cleaning.clean_dataset("olist_order_reviews_dataset.csv")

    assert result["cleaned_rows"] == 2


def test_duplicate_review_composite_key_raises_error(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "review_id": ["R1", "R1"],
        "order_id": ["O1", "O1"],
        "review_score": [5, 4],
        "review_comment_title": [None, None],
        "review_comment_message": [None, None],
        "review_creation_date": [
            "2018-01-01 00:00:00",
            "2018-01-02 00:00:00",
        ],
        "review_answer_timestamp": [
            "2018-01-02 00:00:00",
            "2018-01-03 00:00:00",
        ],
    })

    source.to_csv(raw_dir / "olist_order_reviews_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    with pytest.raises(ValueError, match="duplicate key records"):
        cleaning.clean_dataset("olist_order_reviews_dataset.csv")


def test_missing_product_category_is_explicitly_unknown(
    tmp_path, monkeypatch
):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "product_id": ["P1"],
        "product_category_name": [None],
        "product_name_lenght": [10],
        "product_description_lenght": [100],
        "product_photos_qty": [2],
        "product_weight_g": [500],
        "product_length_cm": [10],
        "product_height_cm": [5],
        "product_width_cm": [8],
    })

    source.to_csv(raw_dir / "olist_products_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    cleaning.clean_dataset("olist_products_dataset.csv")

    cleaned = pd.read_csv(
        clean_dir / "olist_products_dataset.csv"
    )

    assert cleaned.loc[0, "product_category_name"] == "unknown"


def test_invalid_timestamp_becomes_nat_without_fabrication(
    tmp_path, monkeypatch
):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "order_id": ["O1"],
        "customer_id": ["C1"],
        "order_status": ["delivered"],
        "order_purchase_timestamp": ["invalid-date"],
        "order_approved_at": ["2018-01-01 10:00:00"],
        "order_delivered_carrier_date": ["2018-01-02 10:00:00"],
        "order_delivered_customer_date": ["2018-01-03 10:00:00"],
        "order_estimated_delivery_date": ["2018-01-05 10:00:00"],
    })

    source.to_csv(raw_dir / "olist_orders_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    cleaning.clean_dataset("olist_orders_dataset.csv")

    cleaned = pd.read_csv(
        clean_dir / "olist_orders_dataset.csv"
    )

    assert pd.isna(cleaned.loc[0, "order_purchase_timestamp"])


def test_chronology_flags_detect_anomaly_without_changing_dates(
    tmp_path, monkeypatch
):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    source = pd.DataFrame({
        "order_id": ["O1"],
        "customer_id": ["C1"],
        "order_status": ["delivered"],
        "order_purchase_timestamp": ["2018-01-01 10:00:00"],
        "order_approved_at": ["2018-01-01 09:00:00"],
        "order_delivered_carrier_date": ["2018-01-02 10:00:00"],
        "order_delivered_customer_date": ["2018-01-03 10:00:00"],
        "order_estimated_delivery_date": ["2018-01-05 10:00:00"],
    })

    source.to_csv(raw_dir / "olist_orders_dataset.csv", index=False)

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    cleaning.clean_dataset("olist_orders_dataset.csv")

    cleaned = pd.read_csv(
        clean_dir / "olist_orders_dataset.csv"
    )

    assert bool(cleaned.loc[0, "quality_flag_order_approved_at"]) is True
    assert cleaned.loc[0, "order_approved_at"] == "2018-01-01 09:00:00"


def test_raw_dataset_remains_unchanged(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "cleaned"
    raw_dir.mkdir()

    raw_file = raw_dir / "olist_geolocation_dataset.csv"

    source = pd.DataFrame({
        "geolocation_zip_code_prefix": [1000, 1000],
        "geolocation_lat": [10.0, 10.0],
        "geolocation_lng": [30.0, 30.0],
        "geolocation_city": [" City A ", " City A "],
        "geolocation_state": ["SP", "SP"],
    })

    source.to_csv(raw_file, index=False)
    original_bytes = raw_file.read_bytes()

    monkeypatch.setattr(cleaning, "RAW", raw_dir)
    monkeypatch.setattr(cleaning, "CLEAN", clean_dir)

    cleaning.clean_dataset("olist_geolocation_dataset.csv")

    assert raw_file.read_bytes() == original_bytes
