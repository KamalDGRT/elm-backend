from typing import List

from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.oauth2 import get_current_user
from app.schemas.auth import user as schema
from app.utils.auth import hash
from app.utils.fetch import get_roles_of_user
from app.utils.time import get_current_time
from app.utils.http import forbidden, not_found

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/me", response_model=schema.UserOut)
def get_current_user(current_user: schema.UserOut = Depends(get_current_user)):
    return current_user


@router.get("/all", response_model=List[schema.UserOut], include_in_schema=False)
def get_users(
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(get_current_user),
):
    db_users = db.query(User.user_id, User.full_name, User.email, User.user_name).all()
    users_json = list()
    for user in db_users:
        # 0 -> user_id, 1 -> full_name, 2 -> email, 3 -> user_name
        user_data = dict()
        user_data["user_id"] = user[0]
        user_data["full_name"] = user[1]
        user_data["email"] = user[2]
        user_data["user_name"] = user[3]
        roles_of_user = get_roles_of_user(db, user[0])
        user_data["roles"] = roles_of_user

        users_json.append(user_data)
    return users_json


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.UserOut,
    include_in_schema=False,
)
def create_user(request_body: schema.UserCreate, db: Session = Depends(get_db)):
    """
    Inserting a new user into the database
    """
    hashed_password = hash(request_body.password)
    request_body.password = hashed_password

    db_users = (
        db.query(User)
        .filter(User.email == request_body.email, User.is_deleted == 0)
        .all()
    )

    if len(db_users) > 0:
        forbidden("Failed to create the User Already Exists !!!")

    if request_body.user_name:
        db_user_names = (
            db.query(User)
            .filter(User.user_name == request_body.user_name, User.is_deleted == 0)
            .all()
        )

        if len(db_user_names) > 0:
            forbidden("Failed to create the User Already Exists !!!")

    new_user = User(
        full_name=request_body.full_name,
        email=request_body.email,
        user_name=request_body.user_name,
        password=request_body.password,
        login_allowed=request_body.login_allowed,
        is_deleted=request_body.is_deleted,
        created_at=get_current_time(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_roles = list()
    for role in request_body.roles:
        new_role = UserRole(
            user_id=new_user.user_id,
            role_id=role.role_id,
            created_at=get_current_time(),
        )

        db.add(new_role)
        db.commit()
        db.refresh(new_role)

        role_data = schema.RoleUpdate(
            role_id=new_role.role_id,
            role_name=new_role.role.role_name,
            show_on_menu=new_role.role.show_on_menu,
        )
        new_roles.append(role_data)

    return {
        "user_id": new_user.user_id,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "user_name": new_user.user_name,
        "roles": new_roles,
    }


@router.post("/info", response_model=schema.User, include_in_schema=False)
def get_user_info(
    request_body: schema.UserId,
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(get_current_user),
):
    user = db.query(User).filter(User.user_id == request_body.user_id).first()
    if not user:
        not_found(f"User with id: { request_body.user_id } does not exist!")

    user_roles = get_roles_of_user(db, request_body.user_id)
    user_data = user.__dict__
    user_data["roles"] = user_roles

    return user_data
