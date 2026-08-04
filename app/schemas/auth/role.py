from datetime import datetime
from pydantic import BaseModel


class RoleId(BaseModel):
    role_id: int


class RoleCreate(BaseModel):
    role_name: str
    show_on_menu: bool = False

    class Config:
        from_attributes = True


class RoleUpdate(RoleId, RoleCreate):
    pass


class Role(RoleUpdate):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
