from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session


from app import models, oauth2
from app.database import get_db
from app.schemas.auth import token as schema
from app.utils.auth import verify
from app.utils.http import not_found, unauthorized
from app.utils.time import get_current_time

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schema.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(
            or_(
                models.User.email == user_credentials.username,
                models.User.user_name == user_credentials.username,
            )
        )
        .first()
    )

    if not user:
        return not_found("Invalid Credentials !!!")

    # if the passwords do not match
    if not verify(user_credentials.password, user.password):
        return unauthorized("Invalid Credentials !!!")

    # Checking if there is already a refresh token in the DB for that user.
    # If it exists, we remove it.
    refresh_token_check = db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user.user_id
    )
    if refresh_token_check.first():
        refresh_token_check.delete()
        db.commit()

    # Create Tokens to return them
    access_token = oauth2.create_access_token(data={"user_id": user.user_id})
    refresh_token = oauth2.create_refresh_token()

    # Saving Refresh Token in the Database
    refresh_token_dict = {
        "user_id": user.user_id,
        "refresh_token": refresh_token,
        "created_at": get_current_time(),
    }
    refresh_token_db_data = models.RefreshToken(**refresh_token_dict)
    db.add(refresh_token_db_data)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
    }


@router.post("/refresh-access-token", response_model=schema.Token)
def refresh_user_access_token(
    request_body: schema.RefreshTokenInput, db: Session = Depends(get_db)
):
    refresh_token_row = (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.refresh_token == request_body.refresh_token)
        .first()
    )

    if not refresh_token_row:
        return not_found("Invalid Refresh Token !!", {"WWW-Authenticate": "Bearer"})

    expires_at = refresh_token_row.created_at + timedelta(
        minutes=oauth2.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    # created_at comes back tz-naive from MySQL (it stores the wall-clock
    # value get_current_time() wrote, not a tz-aware TIMESTAMP), so drop
    # tzinfo here too before comparing.
    if get_current_time().replace(tzinfo=None) > expires_at:
        db.delete(refresh_token_row)
        db.commit()
        return unauthorized(
            "Refresh Token has expired !!", {"WWW-Authenticate": "Bearer"}
        )

    new_access_token = oauth2.create_access_token(
        data={"user_id": refresh_token_row.user_id}
    )
    return {
        "access_token": new_access_token,
        "refresh_token": request_body.refresh_token,
        "token_type": "Bearer",
    }
