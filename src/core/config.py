# src/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Configurações Gerais do Projeto ---
    PROJECT_NAME: str = "Veritas API" # Nome do seu projeto, com valor padrão

    # --- Chaves de API das LLMs ---
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL_ID: Optional[str] = None

    # --- Configurações de Autenticação/Segurança ---
    SECRET_KEY: str # Essencial para segurança, deve ser fornecida no .env
    JWT_ALGORITHM: str = "HS256"

    # --- Configurações de Banco de Dados ---
    DATABASE_URL: str # URL do banco de dados, essencial
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")

    # --- Configurações do Celery e Redis ---
    CELERY_BROKER_URL: str # URL do broker do Celery (ex: redis://localhost:6379/0)
    CELERY_RESULT_BACKEND: str # Backend para armazenar resultados (ex: redis://localhost:6379/0)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0" # Pode ser o mesmo do broker se não houver uso separado

settings = Settings()

# Para depuração:
print(f"DEBUG: Configurações carregadas - DATABASE_URL: {settings.DATABASE_URL}")
print(f"DEBUG: Configurações carregadas - CELERY_BROKER_URL: {settings.CELERY_BROKER_URL}")
print(f"DEBUG: Configurações carregadas - GEMINI_API_KEY (existente): {'Sim' if settings.GEMINI_API_KEY else 'Não'}")
print(f"DEBUG: Configurações carregadas - HUGGINGFACE_API_KEY (existente): {'Sim' if settings.HUGGINGFACE_API_KEY else 'Não'}")
print(f"DEBUG: Configurações carregadas - DB_POOL_SIZE: {settings.DB_POOL_SIZE}")
print(f"DEBUG: Configurações carregadas - DB_MAX_OVERFLOW: {settings.DB_MAX_OVERFLOW}")
print(f"DEBUG: Configurações carregadas - PROJECT_NAME: {settings.PROJECT_NAME}")