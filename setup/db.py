from typing import Tuple, List

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User, UserRole
from app.utils.auth import hash
from setup.db_data import roles, users

# (full_name, email, password, role_ids, is_deleted, login_allowed)
UserData = Tuple[str, str, str, List[int], bool, bool]

db: Session = next(get_db())


def setup_roles():
    existing_names = {role.role_name for role in db.query(Role).all()}
    for role_name, show_on_menu in roles:
        if role_name in existing_names:
            continue
        db.add(Role(role_name=role_name, show_on_menu=show_on_menu))
        db.commit()
    print("Roles Setup ✓")


def create_user(user_data: UserData) -> User:
    full_name, email, password, role_ids, is_deleted, login_allowed = user_data

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user is not None:
        print(f"User -[{full_name}] already exists, skipping.")
        return existing_user

    new_user = User(
        full_name=full_name,
        email=email,
        password=hash(password),
        login_allowed=login_allowed,
        is_deleted=is_deleted,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    for role_id in role_ids:
        db.add(UserRole(user_id=new_user.user_id, role_id=role_id))
        db.commit()

    print(f"User -[{full_name}] created!")
    return new_user


def setup_users():
    for user_data in users:
        create_user(user_data)
    print("Users Setup ✓")


def setup_data_for_tables():
    setup_roles()
    setup_users()


if __name__ == "__main__":
    setup_data_for_tables()
