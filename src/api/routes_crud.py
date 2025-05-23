# src/api/routes_crud.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db import crud_operations
from src.models.analysis import Analysis, AnalysisCreate, AnalysisUpdateStatus # Importa os Pydantic schemas
from pydantic import BaseModel # Para a resposta de delete

router = APIRouter()

# --- Pydantic Response Schema for Delete (Opcional, para resposta mais estruturada) ---
class DeleteResponse(BaseModel):
    detail: str

# --- Endpoints CRUD ---

@router.post("/analysis", response_model=Analysis, status_code=201)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova análise no sistema.
    """
    return crud_operations.create_analysis(db=db, analysis_data=payload)

@router.get("/analysis/{analysis_id}", response_model=Analysis)
def get_analysis_by_id_endpoint(analysis_id: str, db: Session = Depends(get_db)): # analysis_id como str
    """
    Retorna uma análise específica pelo seu ID.
    """
    analysis = crud_operations.get_analysis_by_id(db, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.put("/analysis/{analysis_id}/status", response_model=Analysis)
def update_status_endpoint(analysis_id: str, payload: AnalysisUpdateStatus, db: Session = Depends(get_db)): # analysis_id como str
    """
    Atualiza o status de uma análise existente.
    """
    analysis = crud_operations.update_analysis_status(db, analysis_id, payload.new_status)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

@router.delete("/analysis/{analysis_id}", response_model=DeleteResponse)
def delete_analysis_endpoint(analysis_id: str, db: Session = Depends(get_db)): # analysis_id como str
    """
    Deleta uma análise do sistema pelo seu ID.
    """
    deleted = crud_operations.delete_analysis(db, analysis_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"detail": "Analysis deleted successfully"}