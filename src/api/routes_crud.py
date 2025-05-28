from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID # Para validar UUIDs

from src.db.database import get_db
from src.db import crud_operations
from src.schemas.analysis_schemas import AnalysisCreate, AnalyzeResponse # Ajustado para o caminho correto do schema
from src.core.tasks import analyze_content_task, get_color_from_classification
from src.core.config import settings # <-- ADICIONADO: Para acessar as configurações da LLM

router = APIRouter(
    prefix="/analyses",
    tags=["Analysis CRUD"]
)

@router.post("/", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_endpoint(
    analysis_data: AnalysisCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria uma nova análise e a envia para processamento assíncrono usando uma LLM.
    Retorna os detalhes da análise criada.
    """
    # Cria a análise no banco de dados
    db_analysis = await crud_operations.create_analysis(db, analysis_data)
    
    if not db_analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Análise não pôde ser criada."
        )

    # --- MUDANÇA PRINCIPAL AQUI: Passando o preferred_llm para a tarefa Celery ---
    # Define qual LLM será usada. Aqui, estamos usando a configurada como padrão em settings.
    # Você pode modificar isso para que o usuário escolha a LLM, se quiser no futuro.
    preferred_llm_to_use = settings.HUGGINGFACE_MODEL_ID 
    # Se você quiser que o Gemini seja o padrão, pode usar: settings.GEMINI_API_KEY
    
    # Envia a tarefa para o Celery com todos os argumentos necessários
    task = analyze_content_task.delay(
        str(db_analysis.id), 
        db_analysis.content, 
        preferred_llm_to_use # <-- ARGUMENTO preferred_llm AGORA É PASSADO
    )

    # Prepara a resposta Pydantic, adicionando o campo 'color'
    # db_analysis é um objeto SQLAlchemy, convertemos para dict para construir o AnalyzeResponse
    analysis_response_data = db_analysis.__dict__
    analysis_response_data["color"] = get_color_from_classification(db_analysis.classification)
    
    return AnalyzeResponse(**analysis_response_data)


@router.get("/{analysis_id}", response_model=AnalyzeResponse)
async def get_analysis_details_endpoint(analysis_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtém os detalhes de uma análise específica.
    """
    # Converte o UUID para string para a função CRUD se ela espera string
    analysis_id_str = str(analysis_id)
    analysis = await crud_operations.get_analysis_by_id(db, analysis_id_str)
    
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análise não encontrada.")

    # analysis é um objeto SQLAlchemy, convertemos para dict para construir o AnalyzeResponse
    analysis_data = analysis.__dict__
    analysis_data["color"] = get_color_from_classification(analysis.classification)
    
    return AnalyzeResponse(**analysis_data)

# Você pode adicionar outras rotas CRUD aqui (PUT para update, DELETE para delete)
# Lembre-se de usar AnalyzeResponse como response_model e de tornar as funções assíncronas.