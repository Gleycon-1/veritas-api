 # src/db/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine # IMPORTANTE: Importar o create_engine SÍNCRONO
import os
from typing import AsyncGenerator, Generator # Importar Generator para a função síncrona
from sqlalchemy.orm import Session as SyncSessionType # Alias para o tipo de sessão síncrona

# Configuração do banco de dados (DEBUG: REMOVIDO OS.GETENV PARA TESTE)
# Certifique-se que esta é a URL do PostgreSQL e sua senha está correta
DATABASE_URL = "postgresql+asyncpg://postgres:maepai123@localhost/veritas_db"

# Cria o motor de banco de dados assíncrono (para FastAPI)
engine = create_async_engine(DATABASE_URL, echo=True) # echo=True para ver as queries SQL

# Cria uma sessão assíncrona (para FastAPI)
AsyncSessionLocal = sessionmaker(
    autocommit=False, # Não auto-comita as transações
    autoflush=False,  # Não auto-descarrega as alterações
    bind=engine,      # Associa a sessão ao motor
    class_=AsyncSession, # Define a classe da sessão como AsyncSession
    expire_on_commit=False # Não expira objetos após o commit (útil para continuar acessando após commit)
)

# Cria um motor de banco de dados SÍNCRONO (para Celery)
# A URL precisa ser ajustada para o driver síncrono (asyncpg -> psycopg2)
# Usamos .replace para garantir que a base da URL seja a mesma
SYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)

# Cria uma sessão síncrona (para Celery)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)

Base = declarative_base()

# Função para obter uma sessão de banco de dados assíncrona (para FastAPI)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency que fornece uma sessão de banco de dados assíncrona.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() # Garante que a sessão seja fechada

# Função para obter uma sessão de banco de dados SÍNCRONA (para Celery)
def get_db_session_sync() -> Generator[SyncSessionType, None, None]: # Usar o alias SyncSessionType
    """
    Dependency que fornece uma sessão de banco de dados síncrona para Celery.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()