# src/api/routes_status.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession # Importe AsyncSession
from src.schemas.analysis_schemas import AnalysisStatus, AnalysisMessage
from src.db.crud_operations import get_analysis_by_id, update_analysis_status_sync # <--- Manter sync_crud_operations se Celery for sync
from src.db.database import get_db_session_async # <--- CORRIGIDO: Importe get_db_session_async

router = APIRouter()

@router.get("/status/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(
    analysis_id: str,
    db: AsyncSession = Depends(get_db_session_async) # <--- CORRIGIDO: Use AsyncSession e get_db_session_async
):
    db_analysis = await get_analysis_by_id(db, analysis_id)
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    return AnalysisStatus(
        id=db_analysis.id,
        status=db_analysis.status,
        classification=db_analysis.classification,
        color=db_analysis.color
    )

@router.put("/status/{analysis_id}/message", response_model=AnalysisStatus, status_code=status.HTTP_200_OK)
async def update_analysis_message(
    analysis_id: str,
    analysis_message: AnalysisMessage,
    db: AsyncSession = Depends(get_db_session_async) # <--- CORRIGIDO: Use AsyncSession e get_db_session_async
):
    # ATENÇÃO: update_analysis_status_sync é uma função SÍNCRONA
    # Você precisará decidir se esta rota deve ser síncrona ou se a função CRUD deve ser assíncrona.
    # Por agora, vou assumir que update_analysis_status_sync está em src/db/sync_crud_operations.py
    # e que essa rota pode (temporariamente) chamar uma função síncrona dentro de uma async.
    # Idealmente, teríamos um update_analysis_message_async em crud_operations.py
    db_analysis = update_analysis_status_sync(db, analysis_id, analysis_message.new_message) # <--- Chame a função síncrona
    
    if db_analysis is None:
        raise HTTPException(status_code=404, detail="Análise não encontrada")
    
    return AnalysisStatus(
        id=db_analysis.id,
        status=db_analysis.status,
        classification=db_analysis.classification,
        color=db_analysis.color
    )

# ... (outras rotas se houver)