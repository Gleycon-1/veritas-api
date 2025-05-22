from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
import uuid

from .database import Base  # Usa a Base criada no database.py

class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    classification = Column(String, nullable=False)
    status = Column(String, nullable=False)
    sources = Column(Text, nullable=False)  # Armazena lista como JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
