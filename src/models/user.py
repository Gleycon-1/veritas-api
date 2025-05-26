# src/models/user.py

from typing import Optional
from fastapi import Depends

# Importação da classe base de usuário específica para SQLAlchemy do pacote dedicado
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# IMPORTANTE: Definindo a Base aqui para garantir que ela seja a mesma que em main.py
# Se você já tem sua classe 'Base' DeclarativeBase em 'src/db/database.py',
# você DEVE comentar a linha 'class Base(DeclarativeBase): pass' abaixo
# e, em vez disso, importar a Base do seu arquivo de database:
# from src.db.database import Base # (Descomente/adicione se for o caso)
class Base(DeclarativeBase):
    pass


# Definição do modelo User.
# Ele herda de SQLAlchemyBaseUserTable (que já inclui o IntegerIDMixin internamente)
# e da sua própria Base Declarative.
class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user" # Nome da tabela no banco de dados

    # Definição das colunas da tabela de usuário
    # NOTE: O 'id' não precisa ser explicitamente mapeado se SQLAlchemyBaseUserTable[int]
    # já cuidar dele, mas manter é seguro.
    id: Mapped[int] = mapped_column(Integer, primary_key=True) # Exemplo para garantir o ID como int
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

# Configurações do Banco de Dados para a sessão assíncrona
# É uma boa prática ter esta URL em um arquivo de configuração (settings.py ou config.py)
DATABASE_URL = "sqlite+aiosqlite:///./veritas.db"
engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependência para obter a sessão assíncrona do banco de dados
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# Dependência para obter a instância do banco de dados de usuário para o FastAPIUsers
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    # SQLAlchemyUserDatabase agora é importado de fastapi_users_db_sqlalchemy
    yield SQLAlchemyUserDatabase(session, User)