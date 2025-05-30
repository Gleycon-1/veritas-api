# src/db/models.py

from sqlalchemy import Column, String, Text, DateTime, func # Importado 'func' aqui
from datetime import datetime
import uuid

# IMPORTANTE: Importe o 'Base' do seu arquivo database.py
# Este 'Base' já está associado ao motor do banco de dados.
from src.db.database import Base # <--- CORRETO!

# Você pode remover a linha abaixo, pois Base será importado
# Base = declarative_base() # <-- Remova esta linha se ainda estiver aí!

class AnalysisModel(Base):
    __tablename__ = "analyses" # Nome da tabela no banco de dados

    # ID como String (UUID), gerado automaticamente
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False) # Usar Text para conteúdos longos
    classification = Column(String, default="pending", nullable=False)
    status = Column(String, default="pending", nullable=False)

    # sources será armazenado como Text (string JSON)
    sources = Column(Text, nullable=True) # Alterado para nullable=True caso não haja fontes

    # Coluna 'message'
    message = Column(Text, nullable=True) # Para armazenar mensagens/justificativas, pode ser nulo

    # Adicionando a coluna 'color'
    color = Column(String, default="⚫", nullable=False) # <--- ADICIONADO!

    # Datas: Usando func.now() para timestamps do banco de dados para maior precisão e consistência
    created_at = Column(DateTime, default=func.now(), nullable=False) # <--- Sugestão: usar func.now()
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True) # <--- Sugestão: usar func.now()
    # onupdate=func.now() fará com que updated_at seja atualizado automaticamente
    # sempre que o registro for modificado.