from typing import List

from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import UpdatePasswordLog, User, UserRole
from app.oauth2 import get_current_user
from app.schemas.auth import user as schema
from app.utils.auth import can_manage_users, decrypt_password, encrypt_password, hash, verify
from app.utils.fetch import get_roles_of_user
from app.utils.time import get_current_time
from app.utils.http import forbidden, not_found, success_response

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/me", response_model=schema.UserOut)
def get_current_user(current_user: schema.UserOut = Depends(get_current_user)):
    return current_user


@router.get("/all", response_model=List[schema.UserOut], include_in_schema=False)
def get_users(
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(get_current_user),
):
    if not can_manage_users(current_user.roles):
        return forbidden("Only Root/Admin can list users.")

    # Root never shows up in listings — it's the only account with full table
    # access, so leaking it here is the one way this breaks.
    query = db.query(User.user_id, User.full_name, User.email, User.user_name)
    if settings.root_user_id is not None:
        query = query.filter(User.user_id != settings.root_user_id)
    db_users = query.all()
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
    encrypted_password = encrypt_password(request_body.password)
    request_body.password = hash(request_body.password)

    if request_body.email:
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
        password_plain=encrypted_password,
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
    if not can_manage_users(current_user.roles) and current_user.user_id != request_body.user_id:
        return forbidden("Only Root/Admin can look up another user.")

    user = db.query(User).filter(User.user_id == request_body.user_id).first()
    if not user:
        return not_found(f"User with id: { request_body.user_id } does not exist!")

    user_roles = get_roles_of_user(db, request_body.user_id)
    user_data = user.__dict__
    user_data["roles"] = user_roles

    return user_data


@router.post("/update-own-password", include_in_schema=False)
def update_own_password(
    request_body: schema.UpdateOwnPassword,
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(get_current_user),
):
    user = db.query(User).filter(User.user_id == current_user.user_id).first()

    if not verify(request_body.current_password, user.password):
        return forbidden("Current password is incorrect.")

    user.password = hash(request_body.new_password)
    user.password_plain = encrypt_password(request_body.new_password)
    user.updated_at = get_current_time()
    db.add(
        UpdatePasswordLog(
            user_id=user.user_id,
            updated_by=current_user.user_id,
            updated_at=get_current_time(),
        )
    )
    db.commit()

    return success_response({"message": "Password updated successfully."})


@router.post("/password", response_model=schema.UserPassword, include_in_schema=False)
def get_user_password(
    request_body: schema.UserId,
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(get_current_user),
):
    """
    Lets Root/Admin read back a user's actual password (not just reset it)
    — needed for users who can't be expected to manage/recall their own
    credentials, e.g. guiding a child through login.
    """
    if not can_manage_users(current_user.roles):
        return forbidden("Only Root/Admin can view another user's password.")

    user = db.query(User).filter(User.user_id == request_body.user_id).first()
    if not user:
        return not_found(f"User with id: { request_body.user_id } does not exist!")
    if not user.password_plain:
        return not_found("No recoverable password stored for this user.")

    return {"user_id": user.user_id, "password": decrypt_password(user.password_plain)}
