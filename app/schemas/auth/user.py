from datetime import datetime
from typing import List

from pydantic import BaseModel, EmailStr

from app.schemas.auth.role import RoleId, RoleUpdate


class UserId(BaseModel):
    user_id: int


class UserRoleCreate(UserId):
    role_id: int


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    roles: List[RoleId]
    login_allowed: bool
    is_deleted: bool


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    roles: List[RoleUpdate]

    class Config:
        from_attributes = True


class User(BaseModel):
    user_id: int
    full_name: str
    email: EmailStr
    created_at: datetime
    roles: List[RoleUpdate]
    login_allowed: bool
    is_deleted: bool

    class Config:
        from_attributes = True


class UserSimple(BaseModel):
    full_name: str

    class Config:
        from_attributes = True
