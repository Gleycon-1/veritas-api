# src/models/analysis.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Modelo para a resposta da API (Analysis já existente)
class Analysis(BaseModel):
    # ID como str (UUID), conforme definido no seu AnalysisModel
    id: str
    content: str
    classification: str # Ex: 'fake', 'true', 'satire', 'opinion', 'pending'
    status: str         # Ex: 'pending', 'completed', 'failed', 'processing'
    sources: Optional[List[str]] = None # Lista de strings para fontes (Pydantic lida com isso)
    created_at: datetime # Tipo datetime para datas
    updated_at: Optional[datetime] = None # Tipo datetime para datas

    class Config:
        from_attributes = True # Para Pydantic v2.x. Use orm_mode = True para Pydantic v1.x

# Modelo para a criação de uma nova análise (campos que são enviados na requisição POST)
class AnalysisCreate(BaseModel):
    content: str
    classification: Optional[str] = Field("pending", description="Initial classification status")
    status: Optional[str] = Field("pending", description="Initial processing status")
    sources: Optional[List[str]] = None

# Modelo para atualização de status de uma análise
class AnalysisUpdateStatus(BaseModel):
    new_status: str

# Modelo para feedback (mantido para consistência)
class Feedback(BaseModel):
    analysis_id: str
    user_id: str
    feedback: str
    created_at: datetime # Ajustado para datetime para consistência