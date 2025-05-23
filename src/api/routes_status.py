# src/api/routes_status.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db import crud_operations # Importa o módulo crud_operations
from src.models.analysis import Analysis # Importa o schema Pydantic para resposta

router = APIRouter()

@router.get("/{analysis_id}", response_model=Analysis) # Prefix já é /status
def get_status_by_id_endpoint(analysis_id: str, db: Session = Depends(get_db)):
    """
    Consulta o status de uma análise pelo seu ID.
    """
    # Usa a função get_analysis_by_id do crud_operations.py
    analysis = crud_operations.get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis