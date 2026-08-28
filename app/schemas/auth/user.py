from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.schemas.auth.role import RoleId, RoleUpdate


class UserId(BaseModel):
    user_id: int


class UserRoleCreate(UserId):
    role_id: int


class UserCreate(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    user_name: Optional[str] = None
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
    email: Optional[EmailStr] = None
    user_name: Optional[str] = None
    roles: List[RoleUpdate]

    class Config:
        from_attributes = True


class User(BaseModel):
    user_id: int
    full_name: str
    email: Optional[EmailStr] = None
    user_name: Optional[str] = None
    created_at: datetime
    roles: List[RoleUpdate]
    login_allowed: bool
    is_deleted: bool

    class Config:
        from_attributes = True


class UpdateOwnPassword(BaseModel):
    current_password: str
    new_password: str


class UpdateUserPassword(BaseModel):
    user_id: int
    new_password: str


class UserSimple(BaseModel):
    full_name: str

    class Config:
        from_attributes = True


class UsernameWords(BaseModel):
    adjectives: List[str]
    fruits_and_vegetables: List[str]


class SignupRequest(BaseModel):
    full_name: str
    user_name: str


class SignupResponse(BaseModel):
    user_id: int
    full_name: str
    user_name: str
    # Shown once at signup so it can be written down; recoverable later via
    # POST /user/password (Root/Admin only).
    password: str


class UserPassword(BaseModel):
    user_id: int
    password: str
