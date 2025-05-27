# src/api/routes_history.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from src.db.database import get_db
from src.db import crud_operations
from src.models.analysis import AnalyzeResponse # Importa o schema Pydantic correto
from src.core.tasks import get_color_from_classification # Importa a função auxiliar de cor

router = APIRouter(
    prefix="/history", # Prefixo para todas as rotas neste arquivo
    tags=["Analysis History"]
)

@router.get("/", response_model=List[AnalyzeResponse]) # Use AnalyzeResponse para a lista!
async def get_all_analyses_endpoint(db: AsyncSession = Depends(get_db)):
    """
    Retorna o histórico de todas as análises realizadas.
    """
    # crud_operations.get_all_analyses precisa ser assíncrona agora
    analyses = await crud_operations.get_all_analyses(db)
    
    if not analyses:
        # Se não houver análises, retorne uma lista vazia, ou um status 204 No Content
        return []

    # Processar cada análise para incluir o campo 'color' e converter para o schema Pydantic
    response_analyses = []
    for analysis in analyses:
        analysis_data = analysis.__dict__
        analysis_data["color"] = get_color_from_classification(analysis.classification)
        response_analyses.append(AnalyzeResponse(**analysis_data))
        
    return response_analyses

# Se você tiver outras rotas neste arquivo, elas também precisarão ser ajustadas.
# Por exemplo, se tiver uma rota para obter uma análise específica por ID aqui,
# ela também deve usar AnalyzeResponse e ser async.