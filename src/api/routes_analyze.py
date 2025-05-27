# src/api/routes_status.py

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db import crud_operations
from src.core.users import current_active_user
from src.models.user import User # Importa o modelo de usuário
from src.models.analysis import AnalyzeResponse # Importa o schema Pydantic de resposta
from src.core.tasks import get_color_from_classification # Importa a função auxiliar de cor

# Define o APIRouter com um prefixo e tags
router = APIRouter(
    prefix="/analysis", # Prefixo mais descritivo
    tags=["Analysis Status & Details"]
)

@router.get("/{analysis_id}", response_model=AnalyzeResponse)
async def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(current_active_user)
):
    """
    Retorna o status e detalhes de uma análise específica.
    Este endpoint requer autenticação.
    """
    # Busca a análise no banco de dados
    analysis = crud_operations.get_analysis_by_id(db, analysis_id)

    # Se a análise não for encontrada, retorna 404
    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Análise não encontrada.")

    # Converte o objeto do SQLAlchemy para o schema Pydantic AnalyzeResponse
    # Mapeamos explicitamente os campos para garantir compatibilidade
    response_data = AnalyzeResponse(
        id=str(analysis.id), # Garante que o ID é uma string para o Pydantic
        content=analysis.content,
        classification=analysis.classification,
        status=analysis.status,
        sources=analysis.sources, # As fontes já devem vir deserializadas do crud_operations
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        color=get_color_from_classification(analysis.classification), # Calcula a cor com base na classificação
        message=analysis.message
    )
    return response_data