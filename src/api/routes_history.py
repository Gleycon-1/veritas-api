# src/api/routes_history.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.schemas.analysis_schemas import AnalysisResult
from src.db.crud_operations import get_all_analyses, delete_analysis_by_id
from src.db.database import get_db_session_async

router = APIRouter()

@router.get("/history", response_model=List[AnalysisResult])
async def get_history(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session_async)
):
    analyses = await get_all_analyses(db, skip=skip, limit=limit)
    return [AnalysisResult.model_validate(analysis, from_attributes=True) for analysis in analyses]

@router.delete("/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_history_entry(
    analysis_id: str,
    db: AsyncSession = Depends(get_db_session_async)
):
    success = await delete_analysis_by_id(db, analysis_id)
    if not success:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return
    # Retorna 204 No Content, não é necessário retornar nada explicitamente
# O endpoint de delete_history_entry não precisa retornar nada, pois o status 204 No Content já indica sucesso.