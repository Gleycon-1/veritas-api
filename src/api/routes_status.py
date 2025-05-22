from fastapi import APIRouter, HTTPException
from src.models.analysis import Analysis
from src.db.database import get_analysis_status

router = APIRouter()

@router.get("/status/{id}", response_model=Analysis)
async def get_status(id: str):
    status = await get_analysis_status(id)
    if status is None:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return status