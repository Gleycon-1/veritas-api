from pydantic import BaseModel, Field, ConfigDict, computed_field
from datetime import datetime
from typing import Optional, List
import json

class AnalysisCreate(BaseModel):
    content: str = Field(..., example="É verdade que comer chocolate ajuda na memória?")
    sources: Optional[List[str]] = Field(default_factory=list)
    preferred_llm: str = Field("gemini", example="gemini")


class AnalyzeResponse(BaseModel):
    id: str
    content: str
    classification: str = "pending"
    status: str = "pending"
    sources_raw: Optional[str] = Field(None, alias="sources")
    message: Optional[str] = None
    preferred_llm: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    color: str = "⚫"

    @computed_field
    @property
    def sources(self) -> List[str]:
        if self.sources_raw:
            try:
                return json.loads(self.sources_raw)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    model_config = ConfigDict(from_attributes=True)


class AnalysisStatus(BaseModel):
    id: str
    status: str
    classification: str
    color: str


class AnalysisMessage(BaseModel):
    new_message: str


class AnalysisResult(BaseModel):
    id: str
    content: str
    status: str
    classification: str
    message: Optional[str]
    preferred_llm: Optional[str]
    sources_raw: Optional[str] = Field(None, alias="sources")
    created_at: datetime
    updated_at: datetime
    color: str

    @computed_field
    @property
    def sources(self) -> List[str]:
        if self.sources_raw:
            try:
                return json.loads(self.sources_raw)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    model_config = ConfigDict(from_attributes=True)
