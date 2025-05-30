# src/api/routes_analyze.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import get_db
from src.schemas.analysis_schemas import AnalysisCreate, AnalyzeResponse # Correção para AnalyzeResponse
from src.db.crud_operations import create_analysis
from src.core.tasks import analyze_content_task

router = APIRouter()

@router.post("/analyses/", response_model=AnalyzeResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_new_analysis(
    analysis_data: AnalysisCreate, db: AsyncSession = Depends(get_db)
):
    db_analysis = await create_analysis(db, analysis_data)
    if not db_analysis:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao criar análise no banco de dados."
        )

    # --- PRINT DE DEPURACAO ADICIONADO AQUI ---
    print(f"DEBUG_FASTAPI: Preferred LLM recebido no endpoint: '{analysis_data.preferred_llm}'")
    # --- FIM PRINT DE DEPURACAO ---
    
    analyze_content_task.delay(
        analysis_id=db_analysis.id,
        content=db_analysis.content,
        preferred_llm=analysis_data.preferred_llm # Passa o preferred_llm dinamicamente
    )
    
    return db_analysis