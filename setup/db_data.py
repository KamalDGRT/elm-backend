# role_name, show_on_menu
# Order matters: role_id is assigned by insertion order (Root=1, System=2, Admin=3).
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
