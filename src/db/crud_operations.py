from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session as SyncSession # Para o Celery (se usado em tarefas síncronas)
from src.db.models import AnalysisModel
from src.schemas.analysis_schemas import AnalysisCreate
from datetime import datetime
import json
from typing import Optional, List
from uuid import uuid4

# --- Funções CRUD para o modelo Analysis ---

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
        updated_at=datetime.utcnow()
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

# --- Funções para serem usadas pelo Celery (síncronas com SyncSession) ---

def update_analysis_details(
    db: SyncSession,
    analysis_id: str,
    classification: str,
    status: str,
    sources: List[str],
    message: Optional[str] = None
) -> Optional[AnalysisModel]: # Adicionei tipo de retorno para clareza
    try:
        # Use o método síncrono para buscar o registro
        analysis = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()

        if analysis:
            analysis.classification = classification
            analysis.status = status
            analysis.sources = json.dumps(sources) # Garante que está serializado
            analysis.message = message
            analysis.updated_at = datetime.utcnow()
            
            db.add(analysis) # Marca o objeto como modificado
            db.commit() # <--- ESSENCIAL: Persiste as mudanças no DB
            db.refresh(analysis) # Recarrega o objeto com os dados atualizados do DB

            # Deserializa 'sources' antes de retornar para consistência
            if analysis.sources:
                try:
                    analysis.sources = json.loads(analysis.sources)
                except json.JSONDecodeError:
                    analysis.sources = []
            return analysis
        else:
            print(f"DEBUG: update_analysis_details - Análise com ID {analysis_id} não encontrada para atualização.")
            return None
    except Exception as e:
        db.rollback() # Em caso de erro, desfaça a transação
        print(f"ERRO: update_analysis_details - Falha ao atualizar análise {analysis_id}: {e}")
        return None

def update_analysis_status(
    db: SyncSession,
    analysis_id: str,
    status: str,
    message: Optional[str] = None
) -> Optional[AnalysisModel]:
    try:
        analysis_to_update = db.query(AnalysisModel).filter(AnalysisModel.id == analysis_id).first()

        if analysis_to_update:
            analysis_to_update.status = status
            # Atualiza a mensagem apenas se uma nova for fornecida
            if message is not None:
                analysis_to_update.message = message
            analysis_to_update.updated_at = datetime.utcnow()
            
            db.add(analysis_to_update) # Marca o objeto como modificado
            db.commit() # <--- ESSENCIAL: Persiste as mudanças no DB
            db.refresh(analysis_to_update) # Recarrega o objeto com os dados atualizados do DB

            # Deserializa 'sources' antes de retornar para consistência com o schema Pydantic
            if analysis_to_update.sources:
                try:
                    analysis_to_update.sources = json.loads(analysis_to_update.sources)
                except json.JSONDecodeError:
                    analysis_to_update.sources = []
            return analysis_to_update
        else:
            print(f"DEBUG: update_analysis_status - Análise com ID {analysis_id} não encontrada para atualização de status.")
            return None
    except Exception as e:
        db.rollback() # Em caso de erro, desfaça a transação
        print(f"ERRO: update_analysis_status - Falha ao atualizar status de análise {analysis_id}: {e}")
        return None

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