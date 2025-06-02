from sqlalchemy import Column, String, Text, DateTime, func
from datetime import datetime
import uuid

from src.db.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False)
    classification = Column(String, default="pending", nullable=False)
    status = Column(String, default="pending", nullable=False)

    sources = Column(Text, nullable=True)  # Armazena lista de fontes como JSON string
    message = Column(Text, nullable=True)
    color = Column(String, default="⚫", nullable=False)
    preferred_llm = Column(String, default="gemini", nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
