import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Carrega variáveis de ambiente do .env
load_dotenv()

# Lê a URL do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./test.db"

# Configura argumentos para SQLite, se necessário
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Cria o engine de conexão
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para os modelos ORM
Base = declarative_base()

# Dependency para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
