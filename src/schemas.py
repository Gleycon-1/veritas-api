# src/schemas.py

from pydantic import BaseModel
from typing import Optional

class AnalysisRequest(BaseModel):
    content: str
    preferred_llm: Optional[str] = None # 'gemini', 'huggingface', 'openai'

class AnalysisResponse(BaseModel):
    id: str
    content: str
    status: str
    classification: str
    message: str
    color: str # Ex: "🟢", "🔴", "⚪"