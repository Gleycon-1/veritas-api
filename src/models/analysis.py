from pydantic import BaseModel
from typing import Optional, List

class Analysis(BaseModel):
    id: str
    content: str
    classification: str
    status: str
    sources: List[str]
    created_at: str
    updated_at: Optional[str] = None

class Feedback(BaseModel):
    analysis_id: str
    user_id: str
    feedback: str
    created_at: str