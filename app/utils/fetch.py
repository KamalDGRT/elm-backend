from typing import List
from sqlalchemy.orm import Session

from app.models import UserRole
from app.schemas.auth import user
from app.schemas.auth.role import RoleUpdate


def get_roles_of_user(db: Session, user_id: int) -> List[RoleUpdate]:
    roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    new_roles = list()
    for role_of_user in roles:
        role_data = user.RoleUpdate(
            role_id=role_of_user.role_id,
            role_name=role_of_user.role.role_name,
            show_on_menu=role_of_user.role.show_on_menu,
        )
        new_roles.append(role_data)
    return new_roles
