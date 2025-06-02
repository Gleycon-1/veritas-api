# src/db/crud_operations.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from src.models.analysis import Analysis  # ORM do banco - CORRIGIDO para Analysis
# from src.schemas.analysis_schemas import AnalysisResult # Pydantic schema (para validação) - Descomentar se precisar usar um schema aqui

async def get_all_analyses(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Analysis]:
    """
    Retorna todas as análises com suporte a paginação.
    """
    result = await db.execute(select(Analysis).offset(skip).limit(limit))
    return result.scalars().all()

async def get_analysis_by_id(db: AsyncSession, analysis_id: UUID) -> Optional[Analysis]:
    """
    Retorna uma análise específica pelo seu ID.
    """
    # É uma boa prática converter o UUID para string apenas na comparação, se o DB armazena como string.
    # Se o DB suporta UUID nativamente (PostgreSQL com PG_UUID), o SQLAlchemy pode lidar com isso.
    result = await db.execute(select(Analysis).filter(Analysis.id == analysis_id))
    return result.scalars().first()

async def create_analysis_entry(
    db: AsyncSession,
    id: UUID,
    content: str,          # Alinhado com o modelo Analysis
    classification: str,   # Alinhado com o modelo Analysis
    color: str,
    status: str,
    sources: str,          # Alinhado com o modelo Analysis
    message: str,          # NOVO CAMPO: Alinhado com o modelo Analysis
    created_at: datetime
) -> Analysis: # O tipo de retorno deve ser Analysis, não AnalysisModel
    """
    Cria uma nova entrada de análise no banco de dados.
    """
    new_analysis = Analysis( # Use Analysis, não AnalysisModel
        id=str(id), # Converter UUID para string se o GUID() converter para CHAR(32) no SQLite
        content=content,
        classification=classification,
        color=color, # Adicionado
        status=status,
        sources=sources, # Adicionado
        message=message, # Adicionado
        created_at=created_at
    )
    db.add(new_analysis)
    await db.commit()
    await db.refresh(new_analysis)
    return new_analysis

async def delete_analysis_by_id(db: AsyncSession, analysis_id: UUID) -> bool: # Tipo de analysis_id mudou para UUID
    """
    Deleta uma análise pelo ID. Retorna True se algo foi deletado, False caso contrário.
    """
    result = await db.execute(delete(Analysis).where(Analysis.id == analysis_id))
    await db.commit()
    return result.rowcount > 0 