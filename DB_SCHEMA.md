# DB Schema

Source of truth is `app/db/auth.py` and `app/db/endpoints.py` — this doc is a snapshot for quick reference; regenerate/update it by hand whenever those model files change. Matches the RBAC design sheet.

Visual ER diagram: [DB_DIAGRAM.md](DB_DIAGRAM.md).

## Authentication (`app/db/auth.py`)

### `role`
| column | type | notes |
|---|---|---|
| role_id | int, PK | |
| role_name | varchar(128) | indexed |
| show_on_menu | bool | default false |
| created_at | timestamptz | server default now() |
| updated_at | timestamptz | server default now() |

### `user`
| column | type | notes |
|---|---|---|
| user_id | int, PK | |
| full_name | varchar(300) | |
| email | varchar(200) | unique |
| password | varchar(100) | hashed (bcrypt via passlib) |
| login_allowed | bool | default false |
| is_deleted | bool | default false, soft-delete flag |
| created_at | timestamptz | |
| updated_at | timestamptz | |

### `refresh_token`
| column | type | notes |
|---|---|---|
| refresh_token_id | int, PK | |
| user_id | int, FK → user.user_id | ON DELETE CASCADE |
| refresh_token | text | |
| created_at | timestamptz | |

### `user_role` (many-to-many: user ↔ role)
| column | type | notes |
|---|---|---|
| user_role_id | int, PK | |
| user_id | int, FK → user.user_id | ON DELETE CASCADE |
| role_id | int, FK → role.role_id | ON DELETE CASCADE |
| created_at | timestamptz | |

### `update_password_log`
| column | type | notes |
|---|---|---|
| log_id | int, PK | |
| user_id | int, FK → user.user_id | whose password changed, ON DELETE CASCADE |
| updated_at | timestamptz | |
| updated_by | int, FK → user.user_id | who made the change, ON DELETE CASCADE |

## Endpoint usage permission (`app/db/endpoints.py`)

### `endpoint`
| column | type | notes |
|---|---|---|
| endpoint_id | int, PK | |
| endpoint_name | varchar(256) | unique |
| is_common | bool | accessible regardless of role, if true |
| is_disabled | bool | kill switch for an endpoint |
| method | varchar(10) | HTTP verb |
| category | text | |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | ON DELETE CASCADE |
| updated_at | timestamptz | |
| updated_by | int, FK → user.user_id | ON DELETE CASCADE |

### `endpoint_role` (many-to-many: endpoint ↔ role)
| column | type | notes |
|---|---|---|
| endpoint_role_id | int, PK | |
| endpoint_id | int, FK → endpoint.endpoint_id | ON DELETE CASCADE |
| role_id | int, FK → role.role_id | ON DELETE CASCADE |
| created_at | timestamptz | |

## Relationships at a glance
```
role ──user_role── user ──refresh_token
role ──endpoint_role── endpoint
user ──update_password_log (self-referencing: user_id + updated_by, both → user)
```

A user's effective permissions = union of all endpoints reachable through every role in `user_role` for that user, via `endpoint_role`. `endpoint.is_common` bypasses this check entirely; `endpoint.is_disabled` blocks it entirely regardless of role.
