import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from fastapi import FastAPI

# Importa os roteadores da API
from src.api.routes_analyze import router as analyze_router
from src.api.routes_status import router as status_router
from src.api.routes_feedback import router as feedback_router
from src.api.routes_history import router as history_router

app = FastAPI(title="Veritas API", description="Combatendo a desinformação com IA", version="1.0")

# Rota raiz
@app.get("/")
def read_root():
    return {"message": "Welcome to the Veritas API - Combatting Disinformation!"}

# Inclusão das rotas
app.include_router(analyze_router, prefix="/analyze")
app.include_router(status_router, prefix="/status")
app.include_router(feedback_router, prefix="/feedback")
app.include_router(history_router, prefix="/history")

# Função para análise de URL (placeholder)
def analisar_url(url: str):
    """
    Função (a ser implementada) que analisa a URL fornecida
    e compara com portais confiáveis para ajudar a detectar fake news.
    """
    pass

# Execução direta com uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
