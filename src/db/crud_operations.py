# src/db/crud_operations.py

from sqlalchemy.ext.asyncio import AsyncSession # Importa AsyncSession para operações assíncronas
from sqlalchemy import select # Importa select para construir queries assíncronas
from src.db.models import AnalysisModel # Assumindo que seu modelo SQLAlchemy AnalysisModel está aqui
from src.models import analysis as schemas # Importa os schemas Pydantic
from datetime import datetime
import json
from typing import Optional, List
from uuid import uuid4 # Importar uuid4 para gerar IDs se necessário

# --- Funções CRUD para o modelo Analysis ---

async def get_analysis_by_id(db: AsyncSession, analysis_id: str):
    """
    Busca uma análise pelo seu ID (assíncrona).
    """
    result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
    db_analysis = result.scalar_one_or_none()
    
    if db_analysis and db_analysis.sources:
        # Deserializa a string JSON de 'sources' de volta para uma lista
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
    db_analyses = result.scalars().all() # .scalars().all() para obter uma lista de objetos
    
    # Deserializa as fontes para cada análise na lista
    for analysis in db_analyses:
        if analysis.sources:
            try:
                analysis.sources = json.loads(analysis.sources)
            except json.JSONDecodeError:
                analysis.sources = []
    return db_analyses


async def create_analysis(db: AsyncSession, analysis_data: schemas.AnalysisCreate):
    """
    Cria uma nova entrada de análise no banco de dados (assíncrona).
    """
    # Garante que o ID seja uma string e que um novo UUID seja gerado se não fornecido
    analysis_id_str = str(analysis_data.id) if analysis_data.id else str(uuid4())

    # Serializa a lista de 'sources' para uma string JSON antes de salvar
    sources_json = json.dumps(analysis_data.sources if analysis_data.sources is not None else [])

    db_analysis = AnalysisModel(
        id=analysis_id_str,
        content=analysis_data.content,
        classification=analysis_data.classification,
        status=analysis_data.status,
        sources=sources_json,
        message=analysis_data.message,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_analysis)
    await db.commit() # await para commit assíncrono
    await db.refresh(db_analysis) # await para refresh assíncrono

    # Deserializa 'sources' de volta para lista para o objeto retornado (consistência com Pydantic)
    if db_analysis.sources:
        try:
            db_analysis.sources = json.loads(db_analysis.sources)
        except json.JSONDecodeError:
            db_analysis.sources = []
    return db_analysis


async def update_analysis_details(
    db: AsyncSession,
    analysis_id: str,
    classification: str,
    status: str,
    sources: List[str],
    message: Optional[str] = None
):
    """
    Atualiza todos os detalhes de uma análise existente (assíncrona).
    """
    result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if analysis:
        analysis.classification = classification
        analysis.status = status
        analysis.sources = json.dumps(sources)
        analysis.message = message
        analysis.updated_at = datetime.utcnow()
        await db.commit() # await para commit assíncrono
        await db.refresh(analysis) # await para refresh assíncrono
        
        # Deserializa 'sources' antes de retornar para consistência
        if analysis.sources:
            try:
                analysis.sources = json.loads(analysis.sources)
            except json.JSONDecodeError:
                analysis.sources = []
        return analysis
    print(f"DEBUG: update_analysis_details - Análise com ID {analysis_id} não encontrada.")
    return None

async def update_analysis_status(db: AsyncSession, analysis_id: str, status: str, message: Optional[str] = None):
    """
    Atualiza o status e opcionalmente a mensagem de uma análise existente (assíncrona).
    """
    result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
    analysis_to_update = result.scalar_one_or_none()

    if analysis_to_update:
        analysis_to_update.status = status
        analysis_to_update.message = message if message is not None else analysis_to_update.message
        analysis_to_update.updated_at = datetime.utcnow()
        await db.commit() # await para commit assíncrono
        await db.refresh(analysis_to_update) # await para refresh assíncrono

        # Deserializa 'sources' antes de retornar para consistência com o schema Pydantic
        if analysis_to_update.sources:
            try:
                analysis_to_update.sources = json.loads(analysis_to_update.sources)
            except json.JSONDecodeError:
                analysis_to_update.sources = []
    return analysis_to_update

async def delete_analysis(db: AsyncSession, analysis_id: str):
    """
    Exclui uma análise do banco de dados pelo seu ID (assíncrona).
    """
    result = await db.execute(select(AnalysisModel).filter(AnalysisModel.id == analysis_id))
    db_analysis = result.scalar_one_or_none()

    if db_analysis:
        await db.delete(db_analysis) # await para delete assíncrono
        await db.commit() # await para commit assíncrono
    return db_analysis