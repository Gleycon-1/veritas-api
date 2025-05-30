# src/db/crud_operations.py (VERSÃO CORRETA PARA O FASTAPI)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.models import AnalysisModel
from src.schemas.analysis_schemas import AnalysisCreate
from datetime import datetime
import json
from typing import Optional, List
from uuid import uuid4

# --- Funções CRUD para o modelo Analysis (Assíncronas - para FastAPI) ---

async def get_analysis_by_id(db: AsyncSession, analysis_id: str):
    """
    Busca uma análise pelo seu ID (assíncrona).
    """
    result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
    db_analysis = result.scalar_one_or_none()
    
    if db_analysis and db_analysis.sources:
        try:
            db_analysis.sources = json.loads(db_analysis.sources)
        except json.JSONDecodeError:
            db_analysis.sources = []
    return db_analysis

async def get_all_analyses(db: AsyncSession):
    """
    Busca todas as análises no banco de dados (assíncrona).
    """
    result = await db.execute(select(AnalysisModel))
    db_analyses = result.scalars().all()
    
    for analysis in db_analyses:
        if analysis.sources:
            try:
                analysis.sources = json.loads(analysis.sources)
            except json.JSONDecodeError:
                analysis.sources = []
    return db_analyses


async def create_analysis(db: AsyncSession, analysis_data: AnalysisCreate):
    """
    Cria uma nova entrada de análise no banco de dados (assíncrona).
    """
    analysis_id_str = str(uuid4()) # Sempre gera um novo UUID

    sources_json = json.dumps(analysis_data.sources if analysis_data.sources is not None else [])

    db_analysis = AnalysisModel(
        id=analysis_id_str,
        content=analysis_data.content,
        classification="pending",
        status="pending",
        sources=sources_json,
        message=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        color="⚫"
    )
    db.add(db_analysis)
    await db.commit()
    await db.refresh(db_analysis)

    if db_analysis.sources:
        try:
            db_analysis.sources = json.loads(db_analysis.sources)
        except json.JSONDecodeError:
            db_analysis.sources = []
    return db_analysis


async def delete_analysis(db: AsyncSession, analysis_id: str):
    """
    Exclui uma análise do banco de dados pelo seu ID (assíncrona).
    """
    result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
    db_analysis = result.scalar_one_or_none()

    if db_analysis:
        await db.delete(db_analysis)
        await db.commit()
    return db_analysis

# AS FUNÇÕES SÍNCRONAS update_analysis_details_sync e update_analysis_status_sync
# DEVEM ESTAR APENAS EM src/db/sync_crud_operations.py