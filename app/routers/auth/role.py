from typing import List

from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

from app.models import Role
from app.oauth2 import get_current_user
from app.database import get_db
from app.schemas.auth import role as schema
from app.schemas.auth.user import UserOut
from app.utils.remove import delete_response
from app.utils.time import get_current_time
from app.utils.http import not_found

router = APIRouter(prefix="/role", tags=["Roles"])


@router.get("/all", response_model=List[schema.Role], include_in_schema=False)
def get_roles(
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    results = db.query(Role).all()
    return results


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.Role,
    include_in_schema=False,
)
def create_role(
    request_body: schema.RoleCreate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    new_role = Role(**request_body.model_dump(), created_at=get_current_time())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.post(
    "/create/many",
    status_code=status.HTTP_201_CREATED,
    response_model=List[schema.Role],
    include_in_schema=False,
)
def create_many_roles(
    request_body: List[schema.RoleCreate],
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    new_roles = list()
    for role in request_body:
        new_role = Role(**role.model_dump(), created_at=get_current_time())
        db.add(new_role)
        db.commit()
        db.refresh(new_role)
        new_roles.append(new_role)

    return new_roles


@router.post("/info", response_model=schema.Role, include_in_schema=False)
def get_role(
    request_body: schema.RoleId,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    role = db.query(Role).filter(Role.role_id == request_body.role_id).first()

    if not role:
        not_found(f"Role with id: { request_body.role_id } not found!")

    return role


@router.delete(
    "/delete", status_code=status.HTTP_200_OK, include_in_schema=False
)
def delete_role(
    request_body: schema.RoleId,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):
    role_query = db.query(Role).filter(Role.role_id == request_body.role_id)
    role = role_query.first()

    if role is None:
        not_found(f"Role with id: { request_body.role_id } does not exist!")

    role_query.delete(synchronize_session=False)
    db.commit()

    return delete_response()


# make sure to add some body in the postman to check it.
@router.put("/update", response_model=schema.Role, include_in_schema=False)
def update_role(
    request_body: schema.RoleUpdate,
    db: Session = Depends(get_db),
    current_user: UserOut = Depends(get_current_user),
):

    role_query = db.query(Role).filter(Role.role_id == request_body.role_id)
    role = role_query.first()

    if role is None:
        not_found(f"Role with id: { request_body.role_id } does not exist!")

    role_query.update(request_body.model_dump(), synchronize_session=False)
    db.commit()

    # Sending the updated role back to the user
    return role_query.first()
