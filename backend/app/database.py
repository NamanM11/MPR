import sqlite3
import json
import os
import uuid

DB_PATH = os.environ.get("DATABASE_URL", "catalog_history.db")
if DB_PATH.startswith("sqlite:///"):
    DB_PATH = DB_PATH.replace("sqlite:///", "")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS catalogs (
            catalog_id TEXT PRIMARY KEY,
            original_text TEXT,
            detected_language TEXT,
            product_name TEXT,
            category TEXT,
            subcategory TEXT,
            attributes TEXT,
            confidence TEXT,
            processing_time_ms INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_catalog(catalog):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO catalogs 
        (catalog_id, original_text, detected_language, product_name, category, subcategory, attributes, confidence, processing_time_ms, status,
         existing_product, matched_product_id, variant_match, product_resolution_confidence, matched_variant, requested_variant, resolution_reasons, resolution_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        catalog["catalog_id"],
        catalog["original_text"],
        catalog["detected_language"],
        catalog["product_name"],
        catalog["category"],
        catalog["subcategory"],
        json.dumps(catalog["attributes"]),
        json.dumps(catalog["confidence"]),
        catalog["processing_time_ms"],
        catalog["status"],
        int(catalog["existing_product"]),
        catalog.get("matched_product_id"),
        None if catalog.get("variant_match") is None else int(catalog["variant_match"]),
        catalog["product_resolution_confidence"],
        json.dumps(catalog.get("matched_variant")),
        json.dumps(catalog.get("requested_variant", {})),
        json.dumps(catalog.get("resolution_reasons", [])),
        catalog["resolution_method"]
    ))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalogs ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    history = []
    for r in rows:
        history.append({
            "catalog_id": r["catalog_id"],
            "original_text": r["original_text"],
            "detected_language": r["detected_language"],
            "product_name": r["product_name"],
            "category": r["category"],
            "subcategory": r["subcategory"],
            "attributes": json.loads(r["attributes"]),
            "confidence": json.loads(r["confidence"]),
            "processing_time_ms": r["processing_time_ms"],
            "status": r["status"],
            "existing_product": bool(r["existing_product"]),
            "matched_product_id": r["matched_product_id"],
            "variant_match": None if r["variant_match"] is None else bool(r["variant_match"]),
            "product_resolution_confidence": r["product_resolution_confidence"],
            "matched_variant": json.loads(r["matched_variant"]) if r["matched_variant"] else None,
            "requested_variant": json.loads(r["requested_variant"]),
            "resolution_reasons": json.loads(r["resolution_reasons"]),
            "resolution_method": r["resolution_method"],
            "seller_decision": r["seller_decision"] or r["status"],
            "created_at": r["created_at"]
        })
    conn.close()
    return history

def update_status(catalog_id, status, updated_attributes=None, product_name=None, category=None, subcategory=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalogs WHERE catalog_id = ?", (catalog_id,))
    catalog = cursor.fetchone()
    if catalog is None:
        conn.close()
        raise ValueError(f"Catalog {catalog_id} was not found.")

    if updated_attributes is not None:
        cursor.execute("""
            UPDATE catalogs
            SET status = ?, seller_decision = ?, attributes = ?, product_name = ?, category = ?, subcategory = ?
            WHERE catalog_id = ?
        """, (status, status, json.dumps(updated_attributes), product_name, category, subcategory, catalog_id))
    else:
        cursor.execute(
            "UPDATE catalogs SET status = ?, seller_decision = ? WHERE catalog_id = ?",
            (status, status, catalog_id)
        )

    if (
        status == "Approved"
        and not catalog["existing_product"]
        and catalog["seller_decision"] != "Approved"
    ):
        product_attributes = updated_attributes if updated_attributes is not None else json.loads(catalog["attributes"])
        requested_variant = json.loads(catalog["requested_variant"])
        if not requested_variant:
            requested_variant = {
                key: product_attributes[key]
                for key in ("color", "size", "storage", "length")
                if product_attributes.get(key)
            }
        cursor.execute("""
            INSERT INTO products (product_id, brand, product_name, category, subcategory, attributes, valid_variants)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            f"PRODUCT-{uuid.uuid4().hex.upper()}",
            product_attributes.get("brand"),
            product_name or catalog["product_name"],
            category or catalog["category"],
            subcategory or catalog["subcategory"],
            json.dumps(product_attributes),
            json.dumps([requested_variant] if requested_variant else [])
        ))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM products ORDER BY product_name COLLATE NOCASE").fetchall()
    products = [
        {
            "product_id": row["product_id"],
            "brand": row["brand"],
            "product_name": row["product_name"],
            "category": row["category"],
            "subcategory": row["subcategory"],
            "attributes": json.loads(row["attributes"]),
            "valid_variants": json.loads(row["valid_variants"])
        }
        for row in rows
    ]
    conn.close()
    return products

def get_db_analytics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM catalogs")
    total_products = cursor.fetchone()[0]
    
    if total_products == 0:
        conn.close()
        return {
            "total_products": 0,
            "success_rate": 100,
            "avg_confidence": 0,
            "existing_product_match_rate": 0,
            "variant_validation_success_rate": 0,
            "new_product_rate": 0,
            "variant_validation_count": 0,
            "language_distribution": {},
            "category_distribution": {},
            "status_distribution": {
                "Draft": 0,
                "Needs Review": 0,
                "Approved": 0
            }
        }
        
    cursor.execute("SELECT COUNT(*) FROM catalogs WHERE status = 'Approved'")
    approved = cursor.fetchone()[0]
    success_rate = round((approved / total_products) * 100, 2)

    cursor.execute("SELECT COUNT(*) FROM catalogs WHERE existing_product = 1")
    existing_matches = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM catalogs WHERE existing_product = 0")
    new_products = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM catalogs WHERE variant_match IS NOT NULL")
    variant_checks = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM catalogs WHERE variant_match = 1")
    valid_variants = cursor.fetchone()[0]
    
    # Calculate avg confidence (read overall confidence values)
    cursor.execute("SELECT confidence FROM catalogs")
    confs = cursor.fetchall()
    total_conf = 0
    for r in confs:
        try:
            c = json.loads(r[0])
            total_conf += c.get("overall", 0.0)
        except Exception:
            pass
    avg_confidence = round((total_conf / total_products) * 100, 2)
    
    # Language distribution
    cursor.execute("SELECT detected_language, COUNT(*) FROM catalogs GROUP BY detected_language")
    lang_dist = {r[0]: r[1] for r in cursor.fetchall()}
    
    # Category distribution
    cursor.execute("SELECT category, COUNT(*) FROM catalogs GROUP BY category")
    cat_dist = {r[0]: r[1] for r in cursor.fetchall()}
    
    # Status distribution
    cursor.execute("SELECT status, COUNT(*) FROM catalogs GROUP BY status")
    status_dist = {"Draft": 0, "Needs Review": 0, "Approved": 0}
    for r in cursor.fetchall():
        status_dist[r[0]] = r[1]
        
    conn.close()
    return {
        "total_products": total_products,
        "success_rate": success_rate,
        "avg_confidence": avg_confidence,
        "existing_product_match_rate": round((existing_matches / total_products) * 100, 2),
        "variant_validation_success_rate": round((valid_variants / variant_checks) * 100, 2) if variant_checks else 0,
        "new_product_rate": round((new_products / total_products) * 100, 2),
        "variant_validation_count": variant_checks,
        "language_distribution": lang_dist,
        "category_distribution": cat_dist,
        "status_distribution": status_dist
    }
