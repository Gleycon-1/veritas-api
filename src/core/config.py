import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Configurações para carregar variáveis de ambiente do arquivo .env
    # 'extra='ignore'' ignora chaves no .env que não estão definidas nesta classe,
    # evitando erros se você tiver variáveis extras por lá.
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Variáveis de ambiente para as APIs das LLMs
    # Usamos os.getenv com um padrão de string vazia para que a API não falhe ao iniciar
    # se uma chave não estiver definida. A lógica de fallback em llm_integration.py
    # vai lidar com a ausência/validade da chave.
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    HUGGINGFACE_MODEL_ID: str = os.getenv("HUGGINGFACE_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2") # ID padrão para o modelo HF

    # Configuração do banco de dados
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./veritas.db") # Padrão para SQLite local

# Cria uma instância das configurações para ser importada em outras partes da aplicação
settings = Settings()