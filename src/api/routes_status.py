# src/api/routes_status.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession # Importa a sessão assíncrona
from src.db.database import get_db # get_db fornece AsyncSession
from src.db import crud_operations # Importa o módulo crud_operations
from src.models.analysis import AnalyzeResponse # Importa o schema Pydantic de resposta
from src.core.tasks import get_color_from_classification # Importa a função auxiliar de cor

router = APIRouter(
    prefix="/analysis", # Prefixo mais descritivo
    tags=["Analysis Status & Details"]
)

@router.get("/{analysis_id}", response_model=AnalyzeResponse)
async def get_status_by_id_endpoint(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """
    Consulta o status e detalhes de uma análise pelo seu ID.
    Este endpoint requer autenticação.
    """
    # Usa a função get_analysis_by_id do crud_operations.py (agora assíncrona)
    analysis = await crud_operations.get_analysis_by_id(db, analysis_id)

    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análise não encontrada.")

    # Converte o objeto do SQLAlchemy para o schema Pydantic AnalyzeResponse
    # e adiciona o campo 'color' que não está no modelo do banco de dados.
    # O Pydantic com `from_attributes=True` (model_config) fará a maior parte do mapeamento.
    # Precisamos apenas adicionar 'color' manualmente.
    
    # Cria um dicionário com os atributos do objeto ORM
    analysis_data = analysis.__dict__
    # Adiciona o campo 'color' calculado
    analysis_data["color"] = get_color_from_classification(analysis.classification)

    # Cria e retorna a instância do schema Pydantic
    return AnalyzeResponse(**analysis_data)