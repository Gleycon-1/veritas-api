# src/core/config.py

import os
from dotenv import load_dotenv

load_dotenv() # Esta linha é crucial para carregar as variáveis do .env

class Settings:
    # Garanta que esses nomes de variáveis correspondam aos do seu .env
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    # Adicione validação básica se quiser, para avisar se alguma chave está faltando
    if not DATABASE_URL:
        print("WARNING: DATABASE_URL não configurada no .env!")
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY não configurada no .env!")
    if not GEMINI_API_KEY:
        print("WARNING: GEMINI_API_KEY não configurada no .env!")

settings = Settings()