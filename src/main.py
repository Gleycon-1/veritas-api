# src/main.py

import sys
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager # Importar para o lifespan

# Adiciona o diretório pai (raiz do projeto) ao sys.path
# Isso garante que Python possa encontrar os módulos dentro de 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa os roteadores
from src.api.routes_analyze import router as analyze_router
from src.api.routes_status import router as status_router
from src.api.routes_feedback import router as feedback_router
from src.api.routes_history import router as history_router
from src.api.routes_crud import router as crud_router
from src.api.routes_auth import router as auth_router 

# IMPORTANTE: Importa o Base e o engine DO SEU ARQUIVO DE DATABASE.PY
# Isso garante que a conexão assíncrona com PostgreSQL seja usada.
from src.db.database import Base, engine, AsyncSessionLocal # MUDANÇA AQUI!

# Importa as configurações da API (onde você define o modelo da LLM)
from src.core.config import settings

# Debug: Configurações das APIs (Opcional, mas útil para verificar)
print(f"DEBUG: Gemini API configurada. {'Sim' if settings.GEMINI_API_KEY else 'Não'}")
print(f"DEBUG: OpenAI API configurada. {'Sim' if settings.OPENAI_API_KEY else 'Não'}")
print(f"DEBUG: Hugging Face API configurada para o modelo: \"{settings.HUGGINGFACE_MODEL_ID}\"")


# Context manager para o ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Evento de startup: Cria as tabelas do banco de dados
    print("INFO: Criando tabelas do banco de dados...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("INFO: Tabelas do banco de dados criadas ou já existentes.")
    yield
    # Evento de shutdown: (opcional, adicione limpeza aqui se necessário)
    print("INFO: Aplicação desligando.")


app = FastAPI(
    title="Veritas API",
    description="API para análise de conteúdo com múltiplas LLMs e verificação de fontes.",
    version="0.1.0", # Mantive a versão anterior, mas pode ser 1.0 como no seu código
    lifespan=lifespan # Adiciona o lifespan ao aplicativo
)


@app.get("/")
async def read_root(): # Mudado para async def para consistência com FastAPI
    return {"message": "Bem-vindo à Veritas API! Acesse /docs para a documentação interativa."}

# Inclui os roteadores da API
app.include_router(crud_router)
app.include_router(analyze_router)
app.include_router(status_router)
app.include_router(feedback_router)
app.include_router(history_router)
app.include_router(auth_router)


# O bloco if __name__ == "__main__": não é necessário com uvicorn src.main:app
# e pode causar o reloader a rodar duas vezes.
# Se você o tem, pode remover ou garantir que não está executando uvicorn.run diretamente.
# A forma correta de iniciar é `uvicorn src.main:app --reload` no terminal.
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)