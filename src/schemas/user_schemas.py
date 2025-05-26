# src/schemas/user_schemas.py
from fastapi_users import schemas

class UserRead(schemas.BaseUser[int]):
    pass # Você pode adicionar campos aqui se quiser que sejam retornados na leitura

class UserCreate(schemas.BaseUserCreate):
    pass # Você pode adicionar campos aqui para criação

class UserUpdate(schemas.BaseUserUpdate):
    pass # Você pode adicionar campos aqui para atualização