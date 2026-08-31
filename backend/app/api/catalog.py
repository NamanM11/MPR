from fastapi import APIRouter, HTTPException, Depends
from ..schemas.catalog import ProcessRequest, ApproveRequest
from ..services.catalog_processor import CatalogProcessor
from ..database import save_catalog, update_status
import os

router = APIRouter()
processor_instance = None

def get_processor():
    global processor_instance
    if processor_instance is None:
        norm_path = os.environ.get("NORMALIZATION_PATH", "backend/app/data/normalization.json")
        tax_path = os.environ.get("TAXONOMY_PATH", "backend/app/data/taxonomy.json")
        
        # Relative path fallback if run from different cwd
        if not os.path.exists(norm_path):
            norm_path = "app/data/normalization.json"
        if not os.path.exists(tax_path):
            tax_path = "app/data/taxonomy.json"
            
        processor_instance = CatalogProcessor(norm_path, tax_path)
    return processor_instance

@router.post("/process")
def process_catalog_endpoint(request: ProcessRequest, processor: CatalogProcessor = Depends(get_processor)):
    try:
        # Run inference, normalization, taxonomy mapping
        catalog = processor.process_text(request.text, request.language)
        # Store in sqlite db
        save_catalog(catalog)
        return catalog
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{catalog_id}/approve")
def approve_catalog_endpoint(catalog_id: str, request: ApproveRequest):
    try:
        update_status(
            catalog_id=catalog_id,
            status="Approved",
            updated_attributes=request.attributes,
            product_name=request.product_name,
            category=request.category,
            subcategory=request.subcategory
        )
        return {"status": "success", "message": f"Catalog {catalog_id} marked as Approved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
