# src/main.py

import sys
import os
from fastapi import FastAPI # Importa FastAPI primeiro

# Adiciona o diretório pai (raiz do projeto) ao sys.path
# Isso permite que importações como 'from src.db.database import ...' funcionem
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Cria a instância da aplicação FastAPI ANTES de incluir qualquer roteador
app = FastAPI(title="Veritas API", description="Combatendo a desinformação com IA", version="1.0")

# Importa os roteadores da API
# Importar DEPOIS que 'app' for definida
from src.api.routes_analyze import router as analyze_router
from src.api.routes_status import router as status_router
from src.api.routes_feedback import router as feedback_router
from src.api.routes_history import router as history_router
from src.api.routes_crud import router as crud_router # Este é o router com seus endpoints CRUD

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "Welcome to the Veritas API - Combatting Disinformation!"}

# Inclusão das rotas com seus prefixos
# Os roteadores devem ser incluídos após 'app' ser criada.
app.include_router(crud_router) # Se routes_crud.py já define os prefixos /analysis, /analysis/{id}, não precisa de prefixo aqui
app.include_router(analyze_router, prefix="/analyze")
app.include_router(status_router, prefix="/status")
app.include_router(feedback_router, prefix="/feedback")
app.include_router(history_router, prefix="/history")

# Função para análise de URL (placeholder, a ser implementada de verdade)
def analisar_url(url: str):
    """
    Função (a ser implementada) que analisa a URL fornecida
    e compara com portais confiáveis para ajudar a detectar fake news.
    """
    pass

# Execução direta com uvicorn (para ambiente de desenvolvimento)
if __name__ == "__main__":
    import uvicorn
    # A string "src.main:app" aponta para o módulo src/main.py e a instância 'app'
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)