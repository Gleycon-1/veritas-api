# src/core/auth.py

from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,  # <-- CORREÇÃO AQUI: Importação direta de BearerTransport
    JWTStrategy,
)

from src.core.config import settings

# A SECRET_KEY é carregada das suas configurações (settings.py que lê o .env)
SECRET = settings.SECRET_KEY

# Define o transporte para o token JWT
# BearerTransport agora é importado diretamente de fastapi_users.authentication
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# Define a estratégia JWT
# O tempo de expiração do token (lifetime_seconds) pode ser ajustado
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600) # Token válido por 1 hora (3600 segundos)

# Define o backend de autenticação
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport, # Usa a instância do transporte definida acima
    get_strategy=get_jwt_strategy, # Usa a função que retorna a estratégia
)