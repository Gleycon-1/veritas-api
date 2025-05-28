# src/schemas/analysis_schemas.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Schema para criar uma nova análise (o que o usuário envia)
class AnalysisCreate(BaseModel):
    content: str = Field(..., example="É verdade que comer chocolate ajuda na memória?")
    sources: Optional[List[str]] = Field([], example=["https://example.com/source1", "https://example.com/source2"])

# Schema para a resposta da API (o que a API retorna sobre uma análise)
class AnalyzeResponse(BaseModel):
    id: str = Field(..., example="a1b2c3d4-e5f6-7890-1234-567890abcdef")
    content: str = Field(..., example="É verdade que comer chocolate ajuda na memória?")
    classification: str = Field("pending", example="fake_news")
    status: str = Field("pending", example="completed")
    sources: List[str] = Field([], example=["LLM_analysis", "https://example.com/verificacao"])
    message: Optional[str] = Field(None, example="A alegação é falsa baseada em x, y, z.")
    created_at: datetime
    updated_at: datetime
    color: str = Field("⚫", example="🔴") # Adicionado para a cor visual na UI

    class Config:
        # Isso permite que o Pydantic mapeie campos de modelos SQLAlchemy
        # 'orm_mode' é para Pydantic v1, 'from_attributes' para Pydantic v2
        from_attributes = True