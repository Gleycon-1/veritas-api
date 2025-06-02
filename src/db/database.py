from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

from src.core.config import settings

# Motor assíncrono para uso com FastAPI (requisições HTTP)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# Motor síncrono para uso com Celery (tarefas em background)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),  # Remove driver async
    echo=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# Sessão assíncrona (usada pelo FastAPI)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Sessão síncrona (usada pelo Celery)
SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)

# Base ORM para os modelos
Base = declarative_base()

# Dependência para FastAPI: injeta sessão assíncrona
async def get_db_session_async():
    async with AsyncSessionLocal() as session:
        yield session
