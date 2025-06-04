import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1" # Adicionado para consistência

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # NOVAS CHAVES DE API - PRECISAM ESTAR AQUI!
    CLAUDE_API_KEY: Optional[str] = None
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: Optional[str] = None
    
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL_ID: Optional[str] = None

    SECRET_KEY: str = "your-super-secret-key" # Certifique-se de que esta chave seja segura em produção
    JWT_ALGORITHM: str = "HS256" # Exemplo de algoritmo JWT

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    PROJECT_NAME: str = "Veritas API"

settings = Settings()
