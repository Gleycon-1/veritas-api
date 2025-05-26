# src/api/routes_auth.py

from fastapi import APIRouter
from src.core.users import fastapi_users
from src.core.auth import auth_backend

# Importa os schemas de usuário da NOVA pasta 'schemas'
from src.schemas.user_schemas import UserRead, UserCreate, UserUpdate # <<-- CORRIGIDO AQUI!


router = APIRouter()

# Roteador para autenticação JWT
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"]
)

# Roteador para registro de novos usuários
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), # <<< CORREÇÃO AQUI
    prefix="/register",
    tags=["auth"]
)

# Roteador para redefinição de senha
router.include_router(
    fastapi_users.get_reset_password_router(), # <<< CORREÇÃO AQUI (se precisar de schemas, adicione-os)
    prefix="/reset-password",
    tags=["auth"]
)

# Roteador para verificação de e-mail (se ativado)
router.include_router(
    fastapi_users.get_verify_router(UserRead), # <<< CORREÇÃO AQUI
    prefix="/verify",
    tags=["auth"]
)

# Roteador para gerenciar usuários (requer superuser)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate), # <<< CORREÇÃO AQUI
    prefix="/users",
    tags=["users"]
)