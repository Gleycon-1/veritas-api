from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Session # Importar Session para a sessão síncrona
from sqlalchemy import create_engine # Para o engine síncrono
from ..core.config import settings # Importação relativa para 'core'
from typing import AsyncGenerator, Generator

DATABASE_URL = settings.DATABASE_URL # Esta linha agora pegará "sqlite+aiosqlite:///./test.db" do settings

Base = declarative_base()

# Motor para operações assíncronas (para FastAPI)
# A URL completa (sqlite+aiosqlite:///) será usada aqui
async_engine = create_async_engine(DATABASE_URL, echo=False)

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
# Para SQLite, o mesmo DATABASE_URL funciona, pois create_engine usará o driver síncrono 'sqlite'
sync_engine = create_engine(DATABASE_URL, echo=False) # Simplificado: usa DATABASE_URL diretamente

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