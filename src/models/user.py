# src/models/user.py

from typing import Optional
from sqlalchemy import Column, String, Boolean
# Se você tiver relacionamentos, pode precisar de 'relationship'
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from fastapi_users.db import SQLAlchemyUserDatabase

from src.db.database import Base, get_db_session_async # Importa get_db_session_async

class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Modelo de usuário para o SQLAlchemy, integrando-se com FastAPI Users.
    Usa UUID como tipo de ID.
    """
    # Exemplo de campos adicionais se você quiser estender o modelo de usuário:
    # first_name = Column(String(255), nullable=True)
    # last_name = Column(String(255), nullable=True)
    pass

# Função para obter a sessão do banco de dados para o gerenciador de usuários
async def get_user_db(session: AsyncSession = Depends(get_db_session_async)):
    """
    Dependência para obter o objeto SQLAlchemyUserDatabase.
    """
    yield SQLAlchemyUserDatabase(session, User)