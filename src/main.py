import sys
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager

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

# IMPORTANTE: Importa o Base, engine, AsyncSessionLocal E create_db_and_tables
# do seu arquivo database.py. create_db_and_tables é a função que garante a criação das tabelas.
from src.db.database import Base, engine, AsyncSessionLocal, create_db_and_tables 

# Importa as configurações da API (onde você define o modelo da LLM)
from src.core.config import settings

# --- Context Manager para o ciclo de vida da aplicação ---
# Esta é a ÚNICA definição de lifespan que deve existir.
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("INFO: Criando tabelas do banco de dados...")
    try:
        # Chama a função que contém a lógica de criação de tabelas
        await create_db_and_tables() 
        print("INFO: Tabelas do banco de dados criadas ou já existentes.")
    except Exception as e:
        # Se ocorrer um erro na criação das tabelas, imprime o erro e re-lança a exceção
        print(f"ERROR: Erro ao criar tabelas do banco de dados: {e}")
        raise # Isso fará com que o FastAPI falhe ao iniciar se as tabelas não puderem ser criadas
    yield # O código após o 'yield' será executado no desligamento da aplicação
    print("INFO: Aplicação desligada.")

# --- Instância da aplicação FastAPI ---
# Esta é a ÚNICA instância de FastAPI que deve existir.
app = FastAPI(
    title="Veritas API",
    description="API para análise de conteúdo com múltiplas LLMs e verificação de fontes.",
    version="0.1.0", 
    lifespan=lifespan # Associa o lifespan definido acima à sua aplicação FastAPI
)

# Debug: Configurações das APIs (Opcional, mas útil para verificar)
print(f"DEBUG: Gemini API configurada. {'Sim' if settings.GEMINI_API_KEY else 'Não'}")
print(f"DEBUG: OpenAI API configurada. {'Sim' if settings.OPENAI_API_KEY else 'Não'}")
print(f"DEBUG: Hugging Face API configurada para o modelo: \"{settings.HUGGINGFACE_MODEL_ID}\"")

# --- Rota de Verificação (Opcional) ---
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à Veritas API! Acesse /docs para a documentação interativa."}

# --- Inclusão dos roteadores da API ---
app.include_router(crud_router)
app.include_router(analyze_router)
app.include_router(status_router)
app.include_router(feedback_router)
app.include_router(history_router)
app.include_router(auth_router)

# O bloco if __name__ == "__main__": não é necessário com uvicorn src.main:app
# e pode causar o reloader a rodar duas vezes.
# A forma correta de iniciar é `uvicorn src.main:app --reload` no terminal.