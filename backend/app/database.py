import sqlite3
import json
import os

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
        (catalog_id, original_text, detected_language, product_name, category, subcategory, attributes, confidence, processing_time_ms, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        catalog["status"]
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
            "created_at": r["created_at"]
        })
    conn.close()
    return history

def update_status(catalog_id, status, updated_attributes=None, product_name=None, category=None, subcategory=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if updated_attributes:
        cursor.execute("""
            UPDATE catalogs 
            SET status = ?, attributes = ?, product_name = ?, category = ?, subcategory = ?
            WHERE catalog_id = ?
        """, (status, json.dumps(updated_attributes), product_name, category, subcategory, catalog_id))
    else:
        cursor.execute("UPDATE catalogs SET status = ? WHERE catalog_id = ?", (status, catalog_id))
    conn.commit()
    conn.close()

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
        "language_distribution": lang_dist,
        "category_distribution": cat_dist,
        "status_distribution": status_dist
    }
