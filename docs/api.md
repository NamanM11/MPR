# API Documentation

The FastAPI backend runs on port 8000 and serves as the REST service layer.

## Endpoints

### 1. Process Product Catalog
* **URL**: `/api/catalog/process`
* **Method**: `POST`
* **Request Body**:
```json
{
  "text": "लाल रंग की कॉटन टीशर्ट पुरुषों के लिए, साइज L",
  "language": "auto"
}
```
* **Response Body**:
The response retains the existing structured catalog fields and adds product-resolution fields:
`existing_product`, `matched_product_id`, `product_match`, `variant_match`,
`product_resolution_confidence`, `resolution_method`, `matched_variant`,
`requested_variant`, and `resolution_reasons`. Existing-product responses also include trusted
`product_metadata`; for new products those metadata fields are `null` and the existing SLM output
remains available for seller review.

```json
{
  "catalog_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "original_text": "लाल रंग की कॉटन टीशर्ट पुरुषों के लिए, साइज L",
  "detected_language": "Hindi",
  "product_name": "Men's Red Cotton T-Shirt",
  "category": "Clothing",
  "subcategory": "T-Shirts",
  "taxonomy_path": ["Clothing", "Men's Clothing", "T-Shirts"],
  "attributes": {
    "product_type": "T-Shirt",
    "brand": null,
    "color": "Red",
    "material": "Cotton",
    "gender": "Men",
    "size": "L",
    "quantity": null
  },
  "confidence": {
    "product_type": 0.98,
    "brand": 1.0,
    "color": 0.95,
    "material": 0.92,
    "gender": 0.97,
    "size": 0.99,
    "quantity": 1.0,
    "overall": 0.973
  },
  "processing_time_ms": 18,
  "status": "Draft"
}
```

### 2. Product Knowledge Base
* **URL**: `/api/catalog/products`
* **Method**: `GET`
* **Response Body**: Products with trusted metadata and their valid variants.

Products approved from the existing Generate Catalog workflow are added to this knowledge base.

### 3. Approve Catalog
* **URL**: `/api/catalog/{catalog_id}/approve`
* **Method**: `POST`
* **Request Body**:
```json
{
  "product_name": "Men's Red Cotton T-Shirt",
  "category": "Clothing",
  "subcategory": "T-Shirts",
  "attributes": {
    "product_type": "T-Shirt",
    "brand": "Nike",
    "color": "Red",
    "material": "Cotton",
    "gender": "Men",
    "size": "L",
    "quantity": "2"
  }
}
```
* **Response Body**:
```json
{
  "status": "success",
  "message": "Catalog 9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d marked as Approved."
}
```

### 4. Get Catalog History
* **URL**: `/api/catalog/history`
* **Method**: `GET`
* **Response Body**: List of saved catalogs in the database (including status, name, category, and timestamps).

### 5. Browse Taxonomy
* **URL**: `/api/taxonomy`
* **Method**: `GET`
* **Response Body**: Configured category mapping tree.

### 6. Fetch Analytics
* **URL**: `/api/analytics`
* **Method**: `GET`
* **Response Body**: Aggregated catalog performance stats.
The analytics response includes `existing_product_match_rate`, `variant_validation_success_rate`,
`new_product_rate`, and `variant_validation_count`, calculated from catalog records.

### 7. Health & Evaluation
* **URL**: `/api/health`
* **Method**: `GET`
* **URL**: `/api/evaluation/metrics`
* **Method**: `GET`

## SQLite migration

This repository uses SQLite, not Supabase. Apply
[`001_product_knowledge_resolution.sql`](../backend/migrations/001_product_knowledge_resolution.sql)
once to the SQLite file selected by `DATABASE_URL` (or the working-directory
`catalog_history.db` default) before starting the updated backend. The migration adds the product
knowledge table, catalog-resolution history columns, and an example iPhone 15 product with its
valid variants. It is an explicit database migration; application startup does not alter schemas.
