from sqlalchemy.orm import Session

from app.db.endpoints import Endpoint, EndpointRole
from app.schemas.auth.endpoint import EndpointCreate, EndpointOut
from app.schemas.auth.role import RoleUpdate
from app.utils.http import forbidden
from app.utils.time import get_current_time


def add_role_for_endpoint(db: Session, endpoint_id: int, role_id: int) -> EndpointRole:
    new_role = EndpointRole(
        endpoint_id=endpoint_id,
        role_id=role_id,
        created_at=get_current_time(),
    )

    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


def create_endpoint(db: Session, input: EndpointCreate, user_id: int) -> EndpointOut:
    db_endpoints = (
        db.query(Endpoint).filter(Endpoint.endpoint_name == input.endpoint_name).all()
    )

    if len(db_endpoints) > 0:
        return forbidden(
            {"message": "Failed to create, the endpoint already exists !!!"}
        )

    new_endpoint = Endpoint(
        endpoint_name=input.endpoint_name,
        is_common=input.is_common,
        is_disabled=input.is_disabled,
        method=input.method,
        category=input.category,
        created_at=get_current_time(),
        created_by=user_id,
        updated_at=get_current_time(),
        updated_by=user_id,
    )
    db.add(new_endpoint)
    db.commit()
    db.refresh(new_endpoint)

    new_roles = list()
    for role in input.roles:
        new_role = add_role_for_endpoint(db, new_endpoint.endpoint_id, role.role_id)
        role_data = RoleUpdate(
            role_id=new_role.role_id,
            role_name=new_role.role.role_name,
            show_on_menu=new_role.role.show_on_menu,
        )
        new_roles.append(role_data)

    return EndpointOut(
        endpoint_id=new_endpoint.endpoint_id,
        endpoint_name=new_endpoint.endpoint_name,
        is_common=new_endpoint.is_common,
        is_disabled=new_endpoint.is_disabled,
        method=new_endpoint.method,
        category=new_endpoint.category,
        roles=new_roles,
        created_at=new_endpoint.created_at,
    )
