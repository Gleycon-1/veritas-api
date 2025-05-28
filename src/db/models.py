# src/db/models.py
from sqlalchemy import Column, String, Text, DateTime #, func, JSON
from datetime import datetime
import uuid

# IMPORTANTE: Importe o 'Base' do seu arquivo database.py
# Este 'Base' já está associado ao motor do banco de dados.
from src.db.database import Base # <--- MUDANÇA CRÍTICA AQUI!

# Você pode remover a linha abaixo, pois Base será importado
# Base = declarative_base() # <-- REMOVA ESTA LINHA!

class AnalysisModel(Base):
    __tablename__ = "analyses" # Nome da tabela no banco de dados

    # ID como String (UUID), gerado automaticamente
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False) # Usar Text para conteúdos longos
    classification = Column(String, default="pending", nullable=False)
    status = Column(String, default="pending", nullable=False)

    # sources será armazenado como Text (string JSON)
    sources = Column(Text, nullable=True) # Alterado para nullable=True caso não haja fontes

    # AQUI ESTÁ A MUDANÇA: Adicionando a coluna 'message'
    message = Column(Text, nullable=True) # Para armazenar mensagens/erros, pode ser nulo

    # Datas:
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    # onupdate=datetime.utcnow fará com que updated_at seja atualizado automaticamente
    # sempre que o registro for modificado.

    # Se você quiser o func.now() do SQLAlchemy para carimbos de data/hora do banco de dados,
    # Você precisaria importar 'func' e mudar as defaults:
    # from sqlalchemy import func
    # created_at = Column(DateTime, default=func.now(), nullable=False)
    # updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    # Para o teste, datetime.utcnow() deve funcionar, mas func.now() é geralmente preferido.