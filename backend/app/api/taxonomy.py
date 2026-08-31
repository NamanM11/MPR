from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

@router.get("")
def get_taxonomy():
    tax_path = os.environ.get("TAXONOMY_PATH", "backend/app/data/taxonomy.json")
    if not os.path.exists(tax_path):
        tax_path = "app/data/taxonomy.json"
        
    if not os.path.exists(tax_path):
        raise HTTPException(status_code=404, detail="Taxonomy configuration not found.")
        
    try:
        with open(tax_path, "r", encoding="utf-8") as f:
            taxonomy = json.load(f)
        return taxonomy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
