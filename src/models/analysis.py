# src/models/analysis.py

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # Para PostgreSQL
from sqlalchemy.types import TypeDecorator, CHAR # Para UUID no SQLite
from sqlalchemy.schema import PrimaryKeyConstraint
import uuid
from datetime import datetime
from src.db.database import Base # Importa a Base declarativa

# Adaptador para UUIDs que funciona tanto com PostgreSQL quanto SQLite
class GUID(TypeDecorator):
    """
    Plataform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value).hex
            return value.hex

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            value = uuid.UUID(value)
        return value

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4) # UUID como PK
    content = Column(String, nullable=False) # O conteúdo (texto/URL) que foi analisado - RENOMEADO DE 'text'
    classification = Column(String, nullable=True) # A classificação de veracidade (ex: "verdadeiro", "fake news") - RENOMEADO DE 'result'
    color = Column(String, default="white") # Cor associada ao resultado (ex: "green", "red", "grey")
    status = Column(String, default="pending") # Status da análise (ex: "pending", "completed", "failed")
    sources = Column(String, nullable=True) # Fontes ou evidências usadas na análise - NOVO CAMPO
    message = Column(String, nullable=True) # Mensagem ou justificativa detalhada da análise do LLM - NOVO CAMPO
    created_at = Column(DateTime, default=datetime.utcnow) # Timestamp da criação

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_analysis_id'),
    )

    def __repr__(self):
        return f"<Analysis(id={self.id}, status='{self.status}', content='{self.content[:30]}...')>" 