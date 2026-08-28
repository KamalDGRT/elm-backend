from fastapi import status, Depends, APIRouter
from sqlalchemy.orm import Session

from app.constants import (
    APP_USER_ROLE_NAME,
    USERNAME_ADJECTIVES,
    USERNAME_FRUITS_AND_VEGETABLES,
)
from app.database import get_db
from app.models import Role, User, UserRole
from app.schemas.auth import user as schema
from app.utils.auth import encrypt_password, generate_password, hash
from app.utils.http import forbidden
from app.utils.time import get_current_time

router = APIRouter(prefix="/signup", tags=["Signup"])


@router.get(
    "/username-words", response_model=schema.UsernameWords, include_in_schema=False
)
def get_username_words():
    """
    Public word pools for the client to combine into a candidate username
    (adjective + fruit/vegetable, no space) before submitting it here.
    """
    return {
        "adjectives": USERNAME_ADJECTIVES,
        "fruits_and_vegetables": USERNAME_FRUITS_AND_VEGETABLES,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.SignupResponse,
    include_in_schema=False,
)
def signup(request_body: schema.SignupRequest, db: Session = Depends(get_db)):
    """
    Self-service signup: no email, no chosen password. The username is a
    client-generated adjective+fruit/vegetable combo, checked for
    uniqueness here; the password is generated server-side (one word +
    three digits) and returned once.
    """
    existing_user = (
        db.query(User)
        .filter(User.user_name == request_body.user_name, User.is_deleted == 0)
        .first()
    )
    if existing_user:
        return forbidden({"message": "That username is already taken."})

    plain_password = generate_password()

    new_user = User(
        full_name=request_body.full_name,
        user_name=request_body.user_name,
        password=hash(plain_password),
        password_plain=encrypt_password(plain_password),
        login_allowed=True,
        is_deleted=False,
        created_at=get_current_time(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    app_user_role = db.query(Role).filter(Role.role_name == APP_USER_ROLE_NAME).first()
    if app_user_role:
        db.add(
            UserRole(
                user_id=new_user.user_id,
                role_id=app_user_role.role_id,
                created_at=get_current_time(),
            )
        )
        db.commit()

    return {
        "user_id": new_user.user_id,
        "full_name": new_user.full_name,
        "user_name": new_user.user_name,
        "password": plain_password,
    }
