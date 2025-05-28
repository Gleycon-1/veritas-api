from pydantic_settings import BaseSettings, SettingsConfigDict
import os # Importar os para acessar variáveis de ambiente diretamente se necessário para depuração

class Settings(BaseSettings):
    # Suas chaves de API LLM
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None
    HUGGINGFACE_MODEL_ID: str = "mistralai/Mistral-7B-Instruct-v0.2"

    SECRET_KEY: str # Chave secreta para JWT

    # *** ADICIONE ESTAS LINHAS para as configurações do banco de dados e Celery ***
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Você já tem REDIS_URL como padrão, mas pode ser sobreescrito pelo .env
    REDIS_URL: str = "redis://localhost:6379/0" 

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Crie uma instância das configurações
settings = Settings()

# Para depuração: Verifique se as variáveis estão sendo carregadas
# print(f"DEBUG: Configurações carregadas - DATABASE_URL: {settings.DATABASE_URL}")
# print(f"DEBUG: Configurações carregadas - CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
# print(f"DEBUG: Configurações carregadas - CELERY_RESULT_BACKEND: {settings.CELERY_RESULT_BACKEND}")