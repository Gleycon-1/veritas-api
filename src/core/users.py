# src/core/users.py

from typing import Optional
from fastapi import Depends, Request
# MUDANÇA AQUI: Tentar importar BaseUserManager diretamente de fastapi_users
from fastapi_users import BaseUserManager, FastAPIUsers # <<< BaseUserManager AQUI!
from fastapi_users.schemas import BaseUser # BaseUser vem de schemas

from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase as SQLAlchemyUserDatabaseActual

from src.models.user import User, get_user_db
from src.core.auth import auth_backend

# UserManager personalizado que herda de BaseUserManager
# Ele herda de BaseUserManager[User, int] porque nosso User tem ID int
class CustomUserManager(BaseUserManager[User, int]): # <<< MUDANÇA AQUI: Herdar de BaseUserManager
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

# Dependência para obter o User Manager
async def get_user_manager(user_db: SQLAlchemyUserDatabaseActual = Depends(get_user_db)):
    # O CustomUserManager cuidará do hashing da senha automaticamente
    yield CustomUserManager(user_db)


# Instanciação do FastAPIUsers
fastapi_users = FastAPIUsers[User, int](
    get_user_manager, # Agora passamos a dependência do CustomUserManager
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)