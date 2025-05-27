# src/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ... suas chaves de API LLM
    GEMINI_API_KEY: str
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None
    HUGGINGFACE_MODEL_ID: str = "mistralai/Mistral-7B-Instruct-v0.2"

    SECRET_KEY: str # Chave secreta para JWT
    REDIS_URL: str = "redis://localhost:6379/0" # <-- ADICIONE ESTA LINHA

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()