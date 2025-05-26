# src/main.py

import sys
import os
from fastapi import FastAPI

# Adiciona o diretório pai (raiz do projeto) ao sys.path
# Isso garante que Python possa encontrar os módulos dentro de 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa os roteadores
from src.api.routes_analyze import router as analyze_router
from src.api.routes_status import router as status_router
from src.api.routes_feedback import router as feedback_router
from src.api.routes_history import router as history_router
from src.api.routes_crud import router as crud_router
from src.api.routes_auth import router as auth_router # Importa o roteador de autenticação

# Importa o Base e o engine do seu modelo de usuário para criar as tabelas.
# ESTE É O IMPORT CRÍTICO: Certifique-se que src/models/user.py define a Base
# que todos os seus modelos (User, Analysis) herdam.
from src.models.user import Base, engine

app = FastAPI(
    title="Veritas API",
    description="Combatendo a desinformação com IA",
    version="1.0"
)

# Evento de startup para criar as tabelas do banco de dados
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("INFO: Database tables created/checked.")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Veritas API - Combatting Disinformation!"}

# Inclui os roteadores no aplicativo FastAPI.
app.include_router(crud_router)
app.include_router(analyze_router)
app.include_router(status_router)
app.include_router(feedback_router)
app.include_router(history_router)
app.include_router(auth_router) # Inclui as rotas de autenticação


# Exemplo de uma função (fora do contexto da API) que poderia analisar uma URL.
def analisar_url(url: str):
    """
    Função (a ser implementada) que analisa a URL fornecida
    e compara com portais confiáveis para ajudar a detectar fake news.
    """
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)