# src/main.py

import sys
import os
from fastapi import FastAPI

# Adiciona o diretório pai (raiz do projeto) ao sys.path
# Isso garante que Python possa encontrar os módulos dentro de 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = FastAPI(
    title="Veritas API",
    description="Combatendo a desinformação com IA",
    version="1.0"
)

# Importa os roteadores DEPOIS de adicionar o diretório pai ao sys.path
from src.api.routes_analyze import router as analyze_router
from src.api.routes_status import router as status_router
from src.api.routes_feedback import router as feedback_router
from src.api.routes_history import router as history_router
from src.api.routes_crud import router as crud_router # Importa o roteador CRUD

@app.get("/")
def read_root():
    return {"message": "Welcome to the Veritas API - Combatting Disinformation!"}

# Inclui os roteadores no aplicativo FastAPI.
# Os prefixos são definidos DENTRO de cada APIRouter nos arquivos de rotas,
# então aqui apenas os incluímos.
app.include_router(crud_router)     # Endpoint: /analysis/...
app.include_router(analyze_router)  # Endpoint: /analyze/... (Este é o da LLM)
app.include_router(status_router)   # Endpoint: /status/...
app.include_router(feedback_router) # Endpoint: /feedback/...
app.include_router(history_router)  # Endpoint: /history/...

# Exemplo de uma função (fora do contexto da API) que poderia analisar uma URL.
# Esta função não está ligada a nenhum endpoint HTTP diretamente.
def analisar_url(url: str):
    """
    Função (a ser implementada) que analisa a URL fornecida
    e compara com portais confiáveis para ajudar a detectar fake news.
    """
    pass

if __name__ == "__main__":
    import uvicorn
    # Executa o aplicativo FastAPI usando Uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)