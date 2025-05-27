# src/schemas/user_schemas.py
from fastapi_users import schemas
from pydantic import ConfigDict # Importar ConfigDict para Pydantic v2

class UserRead(schemas.BaseUser[int]):
    model_config = ConfigDict(from_attributes=True) # <<< ADICIONE ESTA LINHA PARA PYDANTIC V2
    pass # Você pode adicionar campos aqui se quiser que sejam retornados na leitura

class UserCreate(schemas.BaseUserCreate):
    # Não precisa de from_attributes aqui, pois é um schema de entrada
    pass # Você pode adicionar campos aqui para criação

class UserUpdate(schemas.BaseUserUpdate):
    # Não precisa de from_attributes aqui, pois é um schema de entrada/atualização
    pass # Você pode adicionar campos aqui para atualização