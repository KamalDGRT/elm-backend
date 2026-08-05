from typing import Tuple, List

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Endpoint, EndpointRole, Role, User, UserRole
from app.utils.auth import hash
from setup.db_data import endpoint_roles, endpoints, roles, users

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


def setup_users() -> User:
    """Creates (or reuses) all seed users, returns the Root user (needed as created_by/updated_by on Endpoint)."""
    root_user = None
    for user_data in users:
        created = create_user(user_data)
        if user_data[3][0] == 1:  # Root role
            root_user = created
    print("Users Setup ✓")
    return root_user


def setup_endpoints(created_by: int):
    existing_names = {endpoint.endpoint_name for endpoint in db.query(Endpoint).all()}
    for endpoint_name, method, category, is_common, is_disabled in endpoints:
        if endpoint_name in existing_names:
            continue
        db.add(
            Endpoint(
                endpoint_name=endpoint_name,
                method=method,
                category=category,
                is_common=is_common,
                is_disabled=is_disabled,
                created_by=created_by,
                updated_by=created_by,
            )
        )
        db.commit()
    print("Endpoints Setup ✓")


def setup_endpoint_roles():
    endpoint_ids_by_name = {
        endpoint.endpoint_name: endpoint.endpoint_id for endpoint in db.query(Endpoint).all()
    }
    existing_pairs = {
        (endpoint_role.endpoint_id, endpoint_role.role_id)
        for endpoint_role in db.query(EndpointRole).all()
    }
    for endpoint_name, role_id in endpoint_roles:
        endpoint_id = endpoint_ids_by_name[endpoint_name]
        if (endpoint_id, role_id) in existing_pairs:
            continue
        db.add(EndpointRole(endpoint_id=endpoint_id, role_id=role_id))
        db.commit()
    print("Endpoint Roles Setup ✓")


def setup_data_for_tables():
    setup_roles()
    root_user = setup_users()
    setup_endpoints(created_by=root_user.user_id)
    setup_endpoint_roles()


if __name__ == "__main__":
    setup_data_for_tables()
