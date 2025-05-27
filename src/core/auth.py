# src/core/auth.py

from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from src.core.config import settings # Supondo que suas chaves estão em settings.py

# A SECRET_KEY é carregada das suas configurações (settings.py que lê o .env)
SECRET = settings.SECRET_KEY

# Define o transporte para o token JWT
# CORREÇÃO AQUI: tokenUrl deve corresponder ao caminho real do endpoint de login
# (que é /jwt/login, pois o auth_router tem prefixo "/jwt" e o get_auth_router define "/login")
bearer_transport = BearerTransport(tokenUrl="/jwt/login")

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