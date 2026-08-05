# role_name, show_on_menu
# Order matters: role_id is assigned by insertion order (Root=1, System=2, Admin=3).
# check_permissions() in app/utils/auth.py defaults to role_id=2 ("System"), so
# System must stay second.
roles = [
    ("Root", False),
    ("System", False),
    ("Admin", True),
]

# (full_name, email, password, role_ids, is_deleted, login_allowed)
# Dev-only placeholder accounts. Passwords are hashed on insert (see db.py) —
# rotate these before using outside a local/dev environment.
users = [
    ("Root", "root@elm.dev", "changeme", [1], False, True),
    ("System", "system@elm.dev", "changeme", [2], False, False),
    ("Admin", "admin@elm.dev", "changeme", [3], False, True),
]

# (endpoint_name, method, category, is_common, is_disabled)
# endpoint_name mirrors the router path, matching what check_permissions()
# queries Endpoint.endpoint_name with.
endpoints = [
    ("/endpoint/all", "GET", "Endpoints", False, False),
    ("/endpoint/create", "POST", "Endpoints", False, False),
    ("/endpoint/create-many", "POST", "Endpoints", False, False),
    ("/endpoint/info", "POST", "Endpoints", False, False),
    ("/endpoint/delete", "DELETE", "Endpoints", False, False),
    ("/endpoint/update", "PUT", "Endpoints", False, False),
    ("/login", "POST", "Authentication", True, False),
    ("/refresh-access-token", "POST", "Authentication", True, False),
    ("/role/all", "GET", "Roles", False, False),
    ("/role/create", "POST", "Roles", False, False),
    ("/role/create/many", "POST", "Roles", False, False),
    ("/role/info", "POST", "Roles", False, False),
    ("/role/delete", "DELETE", "Roles", False, False),
    ("/role/update", "PUT", "Roles", False, False),
    ("/user/me", "GET", "Users", True, False),
    ("/user/all", "GET", "Users", False, False),
    ("/user/create", "POST", "Users", False, False),
    ("/user/info", "POST", "Users", False, False),
]

# (endpoint_name, role_id)
# Root and Admin get every non-common endpoint; common endpoints (is_common=True)
# skip the role check entirely so they're omitted here.
endpoint_roles = [
    (endpoint_name, role_id)
    for endpoint_name, _, _, is_common, _ in endpoints
    if not is_common
    for role_id in (1, 3)  # Root, Admin
]
