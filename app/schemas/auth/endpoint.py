from datetime import datetime
from typing import List
from pydantic import BaseModel

from app.schemas.auth.role import RoleId, RoleUpdate
from app.schemas.auth.user import UserSimple


class EndpointId(BaseModel):
    endpoint_id: int


class EndpointName(BaseModel):
    endpoint_name: str


class EndpointCreate(BaseModel):
    endpoint_name: str
    is_common: bool = False
    is_disabled: bool = False
    method: str
    category: str
    roles: List[RoleId]

    class Config:
        from_attributes = True


class EndpointOut(EndpointId, EndpointName):
    is_common: bool
    is_disabled: bool
    method: str
    category: str
    roles: List[RoleUpdate]
    created_at: datetime

    class Config:
        from_attributes = True


class EndpointUpdateRequest(EndpointId, EndpointCreate):
    pass


class Endpoint(EndpointOut):
    created_at: datetime
    updated_at: datetime
    creator: UserSimple
    updater: UserSimple
    
    class Config:
        from_attributes = True
