# src/api/routes_analysis.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db_session_async
from src.db.crud_operations import get_all_analyses, create_analysis_entry, get_analysis_by_id
from src.models.analysis import Analysis # Importa o modelo ORM diretamente aqui para o Pydantic

from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

# Importa sua instância do Celery e as tarefas
from src.celery_utils import celery_app
from src.core.tasks import analyze_content_task # Nome da tarefa Celery que você criou

router = APIRouter()

# Modelo Pydantic para a requisição de análise (o que o cliente envia)
class AnalysisRequest(BaseModel):
    content: str # Renomeado de 'text' para 'content'
    preferred_llm: Optional[str] = None # NOVO CAMPO: Adicionado e opcional

# Modelo Pydantic para a resposta da análise (o que a API retorna)
class AnalysisResponse(BaseModel):
    id: uuid.UUID
    content: str # Renomeado de 'text' para 'content'
    classification: str # Renomeado de 'result' para 'classification'
    color: str
    status: str
    sources: Optional[str] = None # NOVO CAMPO: Adicionado e opcional
    message: Optional[str] = None # NOVO CAMPO: Adicionado e opcional
    created_at: datetime

    class Config:
        from_attributes = True # Pydantic v2: use from_attributes ao invés de orm_mode = True

# Endpoint para obter todas as análises
@router.get("/all", response_model=List[AnalysisResponse], summary="Obter todas as análises")
async def read_all_analyses(db: AsyncSession = Depends(get_db_session_async)):
    """
    Retorna todas as análises cadastradas no sistema.
    """
    analyses = await get_all_analyses(db)
    return analyses

# Endpoint para iniciar uma nova análise
@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_202_ACCEPTED, summary="Iniciar uma nova análise")
async def analyze_text(request: AnalysisRequest, db: AsyncSession = Depends(get_db_session_async)):
    """
    Recebe um texto para análise, cria uma entrada pendente no banco de dados
    e despacha uma tarefa assíncrona para processamento (via Celery).
    """
    new_analysis_id = uuid.uuid4()
    
    # Cria a entrada inicial no banco de dados com status "pending"
    new_analysis = await create_analysis_entry(
        db,
        id=new_analysis_id,
        content=request.content, # Usando 'content' do request
        classification="pending", # Valor inicial
        color="grey", # Uma cor padrão para status pendente
        status="pending",
        sources="", # Valor inicial vazio
        message="Análise pendente.", # Valor inicial vazio
        created_at=datetime.utcnow()
    )

    # --- Aqui você despacharia a tarefa Celery ---
    try:
        # Pega o preferred_llm da requisição, ou usa "gemini" como padrão se não for fornecido
        preferred_llm_for_task = request.preferred_llm if request.preferred_llm else "gemini" 

        task = analyze_content_task.delay(
            str(new_analysis.id),
            new_analysis.content, # Passando o conteúdo da análise para a tarefa
            preferred_llm_for_task # AGORA PEGA DA REQUISIÇÃO!
        )
        # Opcional: Se o seu modelo Analysis tiver um campo para 'celery_task_id', atualize aqui
        # new_analysis.celery_task_id = task.id
        # await db.commit() # Salve o ID da tarefa Celery
        # await db.refresh(new_analysis)
    except Exception as e:
        # Lidar com erros no despacho da tarefa
        print(f"Erro ao despachar tarefa Celery: {e}")
        # Atualize o status da análise para 'failed' no DB, se quiser
        # new_analysis.status = "failed"
        # new_analysis.message = f"Erro ao iniciar a análise: {str(e)}"
        # await db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Falha ao iniciar a análise.")

    # Retorna a resposta inicial com o status "Accepted" (202)
    return new_analysis

# Endpoint para obter o status de uma análise específica
@router.get("/{analysis_id}", response_model=AnalysisResponse, summary="Obter status de uma análise por ID")
async def get_single_analysis(analysis_id: uuid.UUID, db: AsyncSession = Depends(get_db_session_async)):
    """
    Retorna os detalhes de uma análise específica pelo seu ID.
    """
    analysis = await get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análise não encontrada.")
    return analysis
