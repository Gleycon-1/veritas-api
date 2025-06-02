# src/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.core.config import settings # Caminho corrigido
from src.db.database import Base, sync_engine
from src.api.routes_history import router as history_router # Verifique se este arquivo e o router existem
from src.api.routes_auth import router as auth_router     # Verifique se este arquivo e o router existem
from src.api.routes_analysis import router as analysis_router # Caminho e router corretos

# Esta função será executada antes do aplicativo iniciar e ao desligar
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database...")
    # Cria as tabelas do banco de dados (se não existirem) usando o motor síncrono.
    # Esta operação é síncrona e não deve ser executada no loop de eventos assíncrono.
    Base.metadata.create_all(bind=sync_engine)
    print("Database initialized.")
    yield # O código após o 'yield' será executado no desligamento da aplicação
    print("Application shutdown.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan # Adicione o gerenciador de contexto de ciclo de vida
)

# Inclua os roteadores da API
app.include_router(history_router, prefix="/history", tags=["history"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(analysis_router, prefix="/analysis", tags=["analysis"]) # Prefixo para todas as rotas de análise

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}!"}