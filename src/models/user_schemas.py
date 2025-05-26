# src/models/user_schemas.py

from typing import Optional
from pydantic import BaseModel, EmailStr

# Schema para o usuário que é retornado APÓS a criação/leitura (sem a senha, por exemplo)
class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    class Config:
        from_attributes = True # ou orm_mode = True para Pydantic < v2


# Schema para a criação de um NOVO usuário (inclui a senha)
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# Schema para a atualização de um usuário existente
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None