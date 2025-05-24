# src/db/init_db.py

import sys
import os
import dotenv # <--- NOVA LINHA AQUI
dotenv.load_dotenv() # <--- NOVA LINHA AQUI - Isso força o carregamento imediatamente

# Adiciona o diretório pai (raiz do projeto) ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# As importações abaixo agora podem confiar que as variáveis de ambiente estão carregadas
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import Base, AnalysisModel
from src.core.config import settings # Configurações que dependem do .env

# --- LINHAS DE DEBUG AQUI (MANTIDAS) ---
print(f"DEBUG: Current Working Directory: {os.getcwd()}")
print(f"DEBUG: DATABASE_URL (via os.getenv directly): {os.getenv('DATABASE_URL')}") # Verificação direta
print(f"DEBUG: DATABASE_URL (via settings object): {settings.DATABASE_URL}") # Verificação via settings
print(f"DEBUG: OPENAI_API_KEY (via settings object): {settings.OPENAI_API_KEY}")
print(f"DEBUG: GEMINI_API_KEY (via settings object): {settings.GEMINI_API_KEY}")
# --- FIM DAS LINHAS DE DEBUG ---

def init_db():
    """
    Inicializa o banco de dados, criando todas as tabelas definidas nos modelos.
    """
    # Acessa a URL do banco de dados das suas configurações
    engine = create_engine(settings.DATABASE_URL)

    # Cria todas as tabelas (Base.metadata.create_all)
    Base.metadata.create_all(bind=engine)
    print(f"Tabelas do banco de dados criadas (ou já existentes) com sucesso no: {settings.DATABASE_URL}")

if __name__ == "__main__":
    init_db()