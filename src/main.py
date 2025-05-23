# src/main.py

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI # Importa FastAPI primeiro

# Cria a instância da aplicação FastAPI
# Ela deve ser criada antes de incluir qualquer roteador
app = FastAPI(title="Veritas API", description="Combatendo a desinformação com IA", version="1.0")

# Importa os roteadores da API
# Importar depois que 'app' for definida
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
# Certifique-se de que cada router seja incluído UMA VEZ com seu prefixo apropriado
app.include_router(crud_router) # Se routes_crud.py já define os prefixos /analysis, /analysis/{id}
                                # então não precisa de prefixo aqui, ou defina um prefixo base como /api/v1
                                # Se routes_crud.py tem endpoints como /analysis, eles serão /analysis
                                # Se você quer que eles sejam /api/v1/analysis, adicione prefix="/api/v1"
                                # Ex: app.include_router(crud_router, prefix="/api/v1")

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

# Execução direta com uvicorn (para uso em ambiente de desenvolvimento)
# É melhor usar o comando uvicorn diretamente no terminal como "uvicorn src.main:app --reload"
# O bloco if __name__ == "__main__": é mais comum para scripts standalone, mas funciona.
# No entanto, o comando uvicorn que estamos usando (`uvicorn src.main:app`) já lida com o reload.
# Se você usar este bloco, a string "main:app" se refere ao módulo main.py e à instância 'app'.
if __name__ == "__main__":
    import uvicorn
    # Ajuste o host e port se necessário
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)