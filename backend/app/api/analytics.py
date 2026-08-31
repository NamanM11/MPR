from fastapi import APIRouter, HTTPException
from ..database import get_db_analytics

router = APIRouter()

@router.get("")
def get_analytics():
    try:
        analytics = get_db_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
