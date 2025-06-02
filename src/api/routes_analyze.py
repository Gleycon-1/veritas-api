# src/api/routes_analyze.py

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession # <--- Importe AsyncSession
from src.schemas.analysis_schemas import AnalysisCreate, AnalyzeResponse
from src.db.database import get_db_session_async # <--- Use a dependência assíncrona
from src.db.models import Analysis
from src.core.tasks import analyze_content_task
import uuid
from datetime import datetime # Importe datetime
import json # Importe json para serializar sources

router = APIRouter()

@router.post("/analyses/", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_analysis(
    request: AnalysisCreate,
    db: AsyncSession = Depends(get_db_session_async) # <--- Use AsyncSession e get_db_session_async
):
    analysis_id = str(uuid.uuid4())
    
    # Serializa sources para string JSON antes de criar o objeto Analysis
    sources_json = json.dumps(request.sources) if request.sources is not None else "[]"

    # Criar o objeto de análise com os dados iniciais
    db_analysis = Analysis(
        id=analysis_id,
        content=request.content,
        status="pending",
        classification="pending",
        message="Análise pendente.",
        color="⚫", # Cor para 'Indefinido' ou 'Pendente'
        preferred_llm=request.preferred_llm, # Adicione preferred_llm aqui
        sources=sources_json # Armazena como string JSON
    )
    
    db.add(db_analysis)
    await db.commit() # <--- Use await com commit() para AsyncSession

    # O await db.refresh(db_analysis) é apropriado aqui, pois a sessão é assíncrona
    # e você precisa dos timestamps gerados pelo DB para a resposta Pydantic.
    await db.refresh(db_analysis) # <--- Re-adicionado e agora com await

    # Despacha a tarefa Celery
    # Note: Celery tasks são síncronas por padrão ou usam seu próprio pool.
    # A sessão passada para o Celery (em analyze_content_task) deve ser síncrona.
    analyze_content_task.delay(analysis_id, request.content, request.preferred_llm)

    # Retorna o objeto db_analysis. Agora ele deve ter created_at e updated_at
    # preenchidos pelo refresh do DB.
    return db_analysis