# src/db/models.py
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# Se você estiver usando PostgreSQL e quiser JSONB, use:
# from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class AnalysisModel(Base):
    __tablename__ = "analyses" # Nome da tabela no banco de dados

    # ID como String (UUID), gerado automaticamente
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False) # Usar Text para conteúdos longos
    classification = Column(String, default="pending", nullable=False)
    status = Column(String, default="pending", nullable=False)

    # sources será armazenado como Text (string JSON)
    sources = Column(Text, nullable=True) # Alterado para nullable=True caso não haja fontes

    # Datas:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    # onupdate=datetime.utcnow fará com que updated_at seja atualizado automaticamente
    # sempre que o registro for modificado.