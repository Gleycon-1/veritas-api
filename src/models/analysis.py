# src/models/analysis.py

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # Se estiver usando PostgreSQL para UUID
from sqlalchemy.types import TypeDecorator, CHAR # Para UUID no SQLite
from sqlalchemy.ext.compiler import compiles # Para UUID no SQLite
from datetime import datetime
from uuid import uuid4, UUID as PyUUID # Importar UUID e PyUUID para IDs (PyUUID é o tipo Python do UUID)

from pydantic import BaseModel, Field, ConfigDict # Importe ConfigDict para Pydantic v2
from typing import Optional, List

# Importe a Base declarativa. ASSUMA que ela está definida em src/models/user.py
# Se não estiver, você precisaria de 'from sqlalchemy.orm import declarative_base; Base = declarative_base()' aqui.
from src.models.user import Base # ASSUMA QUE VOCÊ IMPORTA A BASE GLOBAL DO SEU user.py


# --- Para lidar com UUIDs no SQLite (se necessário) ---
# Se você está usando SQLite, esta classe é importante para o campo 'id'
class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    cache_ok = False # Adicionado para compatibilidade com SQLAlchemy 2.0

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, PyUUID):
                return "%.32x" % PyUUID(value).int # Converte para UUID antes de formatar
            else:
                return "%.32x" % value.int # Já é UUID, formata diretamente

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return PyUUID(value)
        else:
            return PyUUID(value)

# Opcional: Se você estiver usando SQLite e tiver problemas com 'ARRAY(String)'
# O mais simples é usar 'String' para 'sources' e serializar/desserializar manualmente para JSON
# ou usar sqlalchemy.types.JSON para SQLAlchemy >= 1.3
# Por enquanto, vamos usar String e assumir que você lida com JSON ou o database suporta ARRAY
# Se estiver usando PostgreSQL, pode manter ARRAY(String)

# @compiles(GUID, 'sqlite')
# def compile_guid_sqlite(element, compiler, **kw):
#     return "CHAR(32)"
# --- Fim da configuração UUID para SQLite ---


# --- MODELO SQLAlchemy (para o banco de dados) ---
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(GUID(), primary_key=True, default=uuid4) # Use GUID() se for SQLite, ou UUID(as_uuid=True) para PostgreSQL
    content = Column(String, nullable=False)
    classification = Column(String, default="pending")
    status = Column(String, default="pending")
    # Para 'sources', se você usa SQLite, pode mudar para:
    # sources = Column(String, default="[]") # E então faça json.dumps/loads no CRUD
    sources = Column(String, default="[]") # Alterado para String para compatibilidade mais ampla e para o SQLite
    message = Column(String, nullable=True) # NOVO CAMPO: Mensagem da análise
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Analysis(id='{self.id}', status='{self.status}')>"


# --- SCHEMAS Pydantic (para validação de entrada/saída da API) ---

class AnalysisBase(BaseModel):
    # ID não é necessário para a base se ele é gerado pelo BD na criação
    content: str
    classification: str = Field("pending", description="Initial classification status")
    status: str = Field("pending", description="Initial processing status")
    sources: List[str] = Field(default_factory=list) # Pydantic espera lista
    message: Optional[str] = None # Mensagem para o usuário

class AnalysisCreate(AnalysisBase):
    # Ao criar, o ID pode ser gerado ou fornecido, mas é Pydantic.
    # O SQLAlchemy criará o ID real se não for fornecido.
    id: Optional[PyUUID] = Field(default_factory=uuid4)


# Schema para retorno (GET)
# Este é o schema que o routes_analyze.py usará para `response_model`
class AnalyzeResponse(AnalysisBase): # Reutilizando AnalysisBase para campos comuns
    id: PyUUID # O ID retornado será um UUID real
    created_at: datetime
    updated_at: Optional[datetime] = None
    color: str # A cor não é persistida, mas é parte da resposta HTTP (calculada na rota)

    # Configuração para Pydantic v2 (atualizado de Config para model_config)
    model_config = ConfigDict(from_attributes=True)


class AnalysisUpdateStatus(BaseModel):
    status: str = Field(..., description="Novo status da análise (e.g., 'completed', 'failed').")
    message: Optional[str] = Field(None, description="Mensagem adicional sobre a atualização de status.")


# Modelo para feedback (se você estiver usando)
class Feedback(BaseModel):
    analysis_id: PyUUID # Ajustado para PyUUID para consistência
    user_id: PyUUID # Ajustado para PyUUID para consistência
    feedback: str
    created_at: datetime # Ajustado para datetime