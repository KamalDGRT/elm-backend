from typing import List
from passlib.context import CryptContext

from sqlalchemy.orm import Session

from app.db.endpoints import Endpoint, EndpointRole
from app.schemas.auth.role import RoleUpdate
from app.utils.http import forbidden, not_found, unauthorized

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    """
    Returns bcrypt hashed string
    """
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


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
