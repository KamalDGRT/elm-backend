import secrets
from typing import List

from cryptography.fernet import Fernet
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.config import settings
from app.constants import (
    USER_MANAGEMENT_ROLE_NAMES,
    USERNAME_ADJECTIVES,
    USERNAME_FRUITS_AND_VEGETABLES,
)
from app.db.endpoints import Endpoint, EndpointRole
from app.schemas.auth.role import RoleUpdate
from app.utils.http import forbidden, not_found, unauthorized

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_password_cipher = Fernet(settings.password_encryption_key.encode())


def is_root(user_id: int) -> bool:
    """
    There's only ever one Root account, so it's identified by a fixed
    user_id from config (root_user_id), not by role name/id.
    """
    return settings.root_user_id is not None and user_id == settings.root_user_id


def can_manage_users(user_roles: List[RoleUpdate]) -> bool:
    """
    Root and Admin can see/manage other users (e.g. GET /user/all,
    POST /user/info) — AppUsers can only see their own account, via
    GET /user/me.
    """
    return any(role.role_name in USER_MANAGEMENT_ROLE_NAMES for role in user_roles)


def hash(password: str):
    """
    Returns bcrypt hashed string
    """
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def encrypt_password(plain_password: str) -> str:
    """
    Reversible encryption of the plaintext password, kept alongside the
    bcrypt hash so Root/Admin can read it back to a user who can't be
    expected to manage/recall their own credentials.
    """
    return _password_cipher.encrypt(plain_password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    return _password_cipher.decrypt(encrypted_password.encode()).decode()


def generate_password() -> str:
    """
    One word plus three digits (e.g. 'Mango047') so it's easy to read back
    aloud or write down.
    """
    word = secrets.choice(USERNAME_ADJECTIVES + USERNAME_FRUITS_AND_VEGETABLES)
    digits = f"{secrets.randbelow(1000):03d}"
    return f"{word}{digits}"


def check_permissions(
    db: Session,
    endpoint_name: str,
    role_ids: List[RoleUpdate] = [
        RoleUpdate(role_name="System", show_on_menu=False, role_id=2)
    ],
):
    """
    Check whether the current user has the permission to use
    an endpoint.
    """

    endpoint_query = db.query(Endpoint).filter(Endpoint.endpoint_name == endpoint_name)
    endpoint = endpoint_query.first()

    if endpoint is None:
        return not_found(
            {"message": f"Endpoint with id: { endpoint_name } does not exist!"}
        )

    if endpoint.is_disabled:
        return forbidden({"message": "This resource's usage is currently disabled."})

    if not endpoint.is_common:
        """
        If it is a common endpoint, then no need to check for permissions.
        Else we have to check. That is what we are doing below.
        """
        user_roles = set([role.role_id for role in role_ids])
        endpoint_roles_data = (
            db.query(EndpointRole)
            .filter(EndpointRole.endpoint_id == endpoint.endpoint_id)
            .all()
        )
        endpoint_roles = set([role.role_id for role in endpoint_roles_data])

        common_roles = user_roles.intersection(endpoint_roles)

        if len(common_roles) == 0:
            return unauthorized(
                {
                    "message": "You do not have enough permissions to access this resource."
                }
            )
