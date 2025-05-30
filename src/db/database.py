# src/db/database.py (VERSÃO FINAL ATUALIZADA)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import create_engine
from src.core.config import settings
from typing import AsyncGenerator, Generator


DATABASE_URL = settings.DATABASE_URL
# Assumindo que settings.DATABASE_URL = "sqlite+aiosqlite:///./test.db"

Base = declarative_base()

# Motor para operações assíncronas (para FastAPI)
async_engine = create_async_engine(DATABASE_URL, echo=False)

# Adicione esta linha para criar o alias 'engine' que main.py espera
engine = async_engine

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Motor para operações síncronas (para Celery Worker ou outras operações síncronas)
# ESTE É O AJUSTE CRUCIAL: GARANTIR QUE O DRIVER É SÍNCRONO
SYNC_DATABASE_URL_CELERY = settings.DATABASE_URL.replace("+aiosqlite", "") # Remove o driver assíncrono '+aiosqlite'
# Exemplo: de "sqlite+aiosqlite:///./test.db" para "sqlite:///./test.db"

sync_engine = create_engine(SYNC_DATABASE_URL_CELERY, echo=False) # Use a URL síncrona aqui

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
    expire_on_commit=False
)

def get_db_session_sync() -> Generator[Session, None, None]:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("INFO: Tabelas criadas ou já existentes no banco de dados.")