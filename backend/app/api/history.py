from fastapi import APIRouter, HTTPException
from ..database import get_history

router = APIRouter()

@router.get("")
def get_catalog_history():
    try:
        history = get_history()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
