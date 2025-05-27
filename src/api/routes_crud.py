# src/api/routes_crud.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession # Importa a sessão assíncrona
from typing import List

from src.db.database import get_db # get_db fornece AsyncSession
from src.db import crud_operations # Importa o módulo crud_operations
from src.models.analysis import AnalysisCreate, AnalyzeResponse # Importa o schema Pydantic para criação e resposta
from src.core.tasks import analyze_content_task, get_color_from_classification # Importa a tarefa Celery e a função de cor
from celery.result import AsyncResult # Para verificar o status da tarefa Celery
from uuid import UUID # Para validar UUIDs

router = APIRouter(
    prefix="/analyses", # Um prefixo mais genérico para operações CRUD
    tags=["Analysis CRUD"]
)

@router.post("/", response_model=AnalyzeResponse, status_code=status.HTTP_201_CREATED)
async def create_analysis_endpoint(
    analysis_data: AnalysisCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Cria uma nova análise e a envia para processamento assíncrono.
    Retorna os detalhes da análise criada.
    """
    # Cria a análise no banco de dados (o ID será gerado no crud_operations)
    db_analysis = await crud_operations.create_analysis(db, analysis_data)
    
    # Envia a tarefa para o Celery
    # Passamos o ID da análise para a tarefa Celery para que ela possa atualizar o status no DB
    task = analyze_content_task.delay(str(db_analysis.id), db_analysis.content) # Assumindo que task espera ID e content

    # Prepara a resposta Pydantic, adicionando o campo 'color'
    analysis_response_data = db_analysis.__dict__
    analysis_response_data["color"] = get_color_from_classification(db_analysis.classification) # 'pending' por padrão
    
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

    analysis_data = analysis.__dict__
    analysis_data["color"] = get_color_from_classification(analysis.classification)
    
    return AnalyzeResponse(**analysis_data)

# Você pode adicionar outras rotas CRUD aqui (PUT para update, DELETE para delete)
# Lembre-se de usar AnalyzeResponse como response_model e de tornar as funções assíncronas.