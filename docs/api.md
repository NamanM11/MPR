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

### 2. Approve Catalog
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

### 3. Get Catalog History
* **URL**: `/api/catalog/history`
* **Method**: `GET`
* **Response Body**: List of saved catalogs in the database (including status, name, category, and timestamps).

### 4. Browse Taxonomy
* **URL**: `/api/taxonomy`
* **Method**: `GET`
* **Response Body**: Configured category mapping tree.

### 5. Fetch Analytics
* **URL**: `/api/analytics`
* **Method**: `GET`
* **Response Body**: Aggregated catalog performance stats.

### 6. Health & Evaluation
* **URL**: `/api/health`
* **Method**: `GET`
* **URL**: `/api/evaluation/metrics`
* **Method**: `GET`
