from datetime import datetime, timedelta, timezone

from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models, database
from app.config import settings
from app.schemas.auth import token as schema
from app.schemas.auth.user import UserOut
from app.utils.auth import can_manage_users, is_root
from app.utils.fetch import get_roles_of_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
REFRESH_TOKEN_SECRET_KEY = settings.refresh_token_secret_key


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, REFRESH_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(
    token: str, credentials_exception: HTTPException
) -> schema.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("user_id"))

        if user_id is None:
            raise credentials_exception
        token_data = schema.TokenData(user_id=user_id)

    except JWTError:
        raise credentials_exception

    return token_data


def verify_refresh_token(token: str) -> schema.TokenData:
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Refresh Token !!!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, REFRESH_TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = str(payload.get("user_id"))

        if user_id is None:
            raise invalid_token_exception
        token_data = schema.TokenData(user_id=user_id)

    except JWTError:
        raise invalid_token_exception

    return token_data


def get_new_access_token(token: str):
    token_data = verify_refresh_token(token)
    return create_access_token(token_data.model_dump())


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
) -> UserOut:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    user = (
        db.query(models.User).filter(models.User.user_id == token_data.user_id).first()
    )
    return UserOut(
        user_id=user.user_id,
        full_name=user.full_name,
        email=user.email,
        user_name=user.user_name,
        roles=get_roles_of_user(db, user.user_id)
    )


def require_root(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """
    Gate for every router under app/routers/root/ — there's only one Root
    account (see app/utils/auth.is_root), so this is the single place that
    check happens.
    """
    if not is_root(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Root only.",
        )
    return current_user


def require_root_or_admin(current_user: UserOut = Depends(get_current_user)) -> UserOut:
    """
    Gate for routers that Root and Admin both manage — unlike require_root,
    this admits Admin too via can_manage_users().
    """
    if not can_manage_users(current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Root or Admin only.",
        )
    return current_user
