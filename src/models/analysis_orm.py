from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base
import datetime

from src.db.database import Base

class AnalysisORM(Base):
    __tablename__ = "analysis"

    id = Column(String, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    classification = Column(String, nullable=False)
    status = Column(String, nullable=False)
    sources = Column(Text, nullable=False)  # armazenar como JSON string ou lista serializada
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
