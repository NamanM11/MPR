import sqlite3
from pathlib import Path

import pytest

from backend.app import database
from backend.app.services import catalog_processor as catalog_processor_module
from backend.app.services.catalog_processor import CatalogProcessor


class StubModel:
    def predict(self, _text):
        predictions = {
            "language": "English",
            "category": "Electronics",
            "subcategory": "Mobile Phones",
            "product_type": "Mobile Phones",
            "color": "Black",
            "material": "None",
            "gender": "None",
            "size": "None",
            "brand": "Apple",
            "quantity": "None",
        }
        return predictions, {key: 0.9 for key in predictions}


@pytest.fixture
def processor(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "catalog.sqlite"))
    database.init_db()
    migration_path = Path(__file__).parents[1] / "migrations" / "001_product_knowledge_resolution.sql"
    with sqlite3.connect(database.DB_PATH) as connection:
        connection.executescript(migration_path.read_text(encoding="utf-8"))

    monkeypatch.setattr(catalog_processor_module, "get_model", lambda: StubModel())
    return CatalogProcessor(
        "backend/app/data/normalization.json",
        "backend/app/data/taxonomy.json",
    )


@pytest.mark.parametrize(
    "text",
    [
        "iPhone 15",
        "Apple iPhone 15 128GB Black",
        "iphone fifteen 128gb black",
        "Apple iPhone 15 mobile",
    ],
)
def test_known_iphone_aliases_resolve(processor, text):
    catalog = processor.process_text(text)

    assert catalog["product_match"] is True
    assert catalog["existing_product"] is True
    assert catalog["matched_product_id"] == "IPHONE15"
    assert catalog["product_name"] == "iPhone 15"
    assert catalog["brand"] == "Apple"
    assert catalog["category"] == "Electronics"
    assert catalog["subcategory"] == "Mobile Phones"


def test_requested_valid_variant_is_retrieved(processor):
    catalog = processor.process_text("Apple iPhone 15 128GB Black")

    assert catalog["variant_match"] is True
    assert catalog["matched_variant"] == {"storage": "128GB", "color": "Black"}
    assert catalog["requested_variant"] == {"storage": "128GB", "color": "Black"}
    assert catalog["attributes"]["model"] == "iPhone 15"
    assert catalog["confidence"]["overall"] == pytest.approx(0.9)


def test_fuzzy_product_match_is_used_after_normalized_exact(processor):
    catalog = processor.process_text("iPhon 15 128GB Black")

    assert catalog["existing_product"] is True
    assert catalog["resolution_method"] == "fuzzy"
    assert catalog["product_resolution_confidence"] >= 0.8


def test_unknown_variant_values_are_not_invented(processor):
    catalog = processor.process_text("iPhone 15 2TB Green")

    assert catalog["product_match"] is True
    assert catalog["variant_match"] is False
    assert catalog["matched_variant"] is None
    assert catalog["resolution_reasons"] == [
        "2TB is not a known storage variant",
        "Green is not a known color variant",
    ]


def test_new_product_history_analytics_and_approval_persistence(processor):
    inputs = [
        "iPhone 15",
        "Apple iPhone 15 128GB Black",
        "iphone fifteen 128gb black",
        "iPhone 15 2TB Green",
        "Red cotton handmade saree 6 meter",
    ]
    catalogs = [processor.process_text(text) for text in inputs]
    for catalog in catalogs:
        database.save_catalog(catalog)

    new_catalog = catalogs[-1]
    assert new_catalog["existing_product"] is False
    assert new_catalog["resolution_method"] == "new_product"

    history = database.get_history()
    assert len(history) == 5
    assert history[1]["matched_product_id"] == "IPHONE15"
    assert history[3]["variant_match"] is False
    assert history[4]["existing_product"] is False

    analytics = database.get_db_analytics()
    assert analytics["existing_product_match_rate"] == 80
    assert analytics["variant_validation_success_rate"] == pytest.approx(66.67)
    assert analytics["new_product_rate"] == 20

    database.update_status(
        new_catalog["catalog_id"],
        "Approved",
        updated_attributes=new_catalog["attributes"],
        product_name=new_catalog["product_name"],
        category=new_catalog["category"],
        subcategory=new_catalog["subcategory"],
    )
    database.update_status(
        new_catalog["catalog_id"],
        "Approved",
        updated_attributes=new_catalog["attributes"],
        product_name=new_catalog["product_name"],
        category=new_catalog["category"],
        subcategory=new_catalog["subcategory"],
    )
    products = database.get_products()
    assert len(products) == 2
    assert any(product["product_name"] == new_catalog["product_name"] for product in products)
    assert next(item for item in database.get_history() if item["catalog_id"] == new_catalog["catalog_id"])[
        "seller_decision"
    ] == "Approved"


def test_empty_resolution_metrics_are_zero(processor):
    assert database.get_db_analytics()["existing_product_match_rate"] == 0
