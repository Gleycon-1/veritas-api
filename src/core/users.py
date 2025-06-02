# src/core/users.py

from fastapi import Depends
# REMOVIDO 'schemas' daqui, pois causa importação circular interna do fastapi_users
from fastapi_users import FastAPIUsers, BaseUserManager, exceptions, models 

from typing import Optional

from src.models.user import User, get_user_db # Importa seu modelo de usuário e a dependência de banco de dados
from src.core.auth import auth_backend # Importa o backend de autenticação

# Importa os schemas de usuário para o UserManager
from src.schemas.user_schemas import UserRead, UserCreate, UserUpdate

# Define um UserManager customizado
class UserManager(BaseUserManager[User, int]):
    # Se precisar enviar emails de verificação/reset, configure aqui
    # reset_password_token_secret = SECRET
    # verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[dict] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[dict] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[dict] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    # ESSENCIAL: Implementar parse_id para FastAPI-Users 11+
    # Ele converte o ID do token (string) para o tipo do seu ID de usuário (int)
    # Note: Seu User.id é int, mas se fosse UUID, seria PyUUID(s)
    def parse_id(self, s: str) -> models.ID: # models.ID é o tipo genérico do fastapi_users para IDs
        try:
            return int(s)
        except ValueError:
            raise exceptions.InvalidIDException()


# Dependência para obter a instância do UserManager
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


# Inicializa a instância do FastAPIUsers
fastapi_users = FastAPIUsers[User, int](
    get_user_manager, # <-- Use a nova dependência do UserManager
    [auth_backend],
)

# Função de dependência para pegar o usuário ativo
# Isso já estava lá, mas é bom ter o contexto
current_active_user = fastapi_users.current_user(active=True) 