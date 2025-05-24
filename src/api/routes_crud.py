# src/api/routes_crud.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from src.db.database import get_db
from src.db import crud_operations
from src.models.analysis import Analysis, AnalysisCreate, AnalysisUpdateStatus
from pydantic import BaseModel, Field

# Define o APIRouter com um prefixo e tags para organizar no Swagger UI
router = APIRouter(
    prefix="/analysis",  # Todos os endpoints aqui terão /analysis antes
    tags=["Analysis CRUD Operations"] # Tag para agrupar no Swagger UI
)

# Schema para resposta de delete
class DeleteResponse(BaseModel):
    detail: str = Field("Analysis deleted successfully", description="Mensagem de confirmação da exclusão.")


@router.post("/", response_model=Analysis, status_code=status.HTTP_201_CREATED)
def create_analysis_endpoint(payload: AnalysisCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova análise no sistema.
    """
    print(f"DEBUG: Recebida solicitação POST /analysis com payload: {payload.dict()}")
    try:
        new_analysis = crud_operations.create_analysis(db=db, analysis_data=payload)
        print(f"DEBUG: Análise criada com sucesso: {new_analysis.id}")
        return new_analysis
    except Exception as e:
        print(f"ERRO: Falha ao criar análise: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Falha ao criar análise: {e}")


@router.get("/{analysis_id}", response_model=Analysis)
def get_analysis_by_id_endpoint(analysis_id: str, db: Session = Depends(get_db)):
    """
    Retorna uma análise específica pelo seu ID.
    """
    print(f"DEBUG: Recebida solicitação GET /analysis/{analysis_id}")
    analysis = crud_operations.get_analysis_by_id(db, analysis_id)
    if not analysis:
        print(f"DEBUG: Análise com ID {analysis_id} não encontrada.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    print(f"DEBUG: Análise com ID {analysis_id} encontrada.")
    return analysis


@router.put("/{analysis_id}/status", response_model=Analysis)
def update_status_endpoint(analysis_id: str, payload: AnalysisUpdateStatus, db: Session = Depends(get_db)):
    """
    Atualiza o status de uma análise existente.
    """
    print(f"DEBUG: Recebida solicitação PUT /analysis/{analysis_id}/status com novo status: {payload.new_status}")
    updated_analysis = crud_operations.update_analysis_status(db, analysis_id, payload.new_status)
    if not updated_analysis:
        print(f"DEBUG: Análise com ID {analysis_id} não encontrada para atualização.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    print(f"DEBUG: Status da análise {analysis_id} atualizado para {payload.new_status}.")
    return updated_analysis


@router.delete("/{analysis_id}", response_model=DeleteResponse)
def delete_analysis_endpoint(analysis_id: str, db: Session = Depends(get_db)):
    """
    Deleta uma análise do sistema pelo seu ID.
    """
    print(f"DEBUG: Recebida solicitação DELETE /analysis/{analysis_id}")
    deleted = crud_operations.delete_analysis(db, analysis_id)
    if not deleted:
        print(f"DEBUG: Análise com ID {analysis_id} não encontrada para exclusão.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    print(f"DEBUG: Análise com ID {analysis_id} deletada com sucesso.")
    return {"detail": "Analysis deleted successfully"}