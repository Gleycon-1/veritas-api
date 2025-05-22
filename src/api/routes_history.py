from fastapi import APIRouter, HTTPException
from typing import List
from src.models.analysis import Analysis

router = APIRouter()

# Simulated in-memory storage for analysis history
analysis_history = []

@router.get("/history", response_model=List[Analysis])
async def get_history():
    if not analysis_history:
        raise HTTPException(status_code=404, detail="No analysis history found.")
    return analysis_history

@router.post("/history", response_model=Analysis)
async def add_to_history(analysis: Analysis):
    analysis_history.append(analysis)
    return analysis