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
| user_name | varchar(100) | unique, nullable |
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

## Content model (draft — not yet implemented)

Planning pass from `elm-plan` product docs ([raw feature notes](../elm-plan/raw.md), [Data Model](../elm-plan/06-data-model.md), [Activity Types](../elm-plan/05-activity-types.md), [My Projects](../elm-plan/08-my-projects.md), [Project Templates](../elm-plan/13-project-templates.md), [Backend RBAC](../elm-plan/07-backend-rbac.md)). Not modeled in `app/db/` yet — this is a table proposal, not a snapshot.

Design notes:
- Role stays per-`group`, not a flat `user.role` — reuses the existing `role`/`user_role` shape but scoped through `group_membership` instead (per `elm-plan`'s "role is per-Group" decision). The auth `role`/`user_role`/`endpoint_role` tables above are unaffected — they gate API-endpoint access; `group_membership` gates content access.
- One generic `resource_access_override` table, not one override table per resource type — covers the Discord-style "direct grant/deny always wins over role" model for activity types, activity versions, project templates, projects, AND modules, per `elm-plan`'s explicit "generic `resource_type` + `resource_id`, not one table per resource" decision.
- `resource_type` is its own lookup table (FK'd by `resource_type_id`), not a hardcoded enum — adding a new overridable resource later (e.g. `project_folder`) is a row insert, no migration.
- `activity_type` is versioned (`activity_version`); `project_template` is deliberately flat/unversioned — confirmed from the mocks, not an oversight.
- `module.activity_version_id` (not `activity_type_id`) — a module is pinned to the specific version it was created against, so template edits in a new version don't retroactively change existing modules. Whether this ever gets reassigned is an [open conflict](../elm-plan/05-activity-types.md#️-conflict-to-resolve) in the product doc.

### `group`
| column | type | notes |
|---|---|---|
| group_id | int, PK | |
| name | varchar(256) | |
| parent_group_id | int, FK → group.group_id, nullable | self-referencing, for subgroups |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |
| updated_at | timestamptz | |
| updated_by | int, FK → user.user_id | |

### `group_membership`
| column | type | notes |
|---|---|---|
| group_membership_id | int, PK | |
| group_id | int, FK → group.group_id | ON DELETE CASCADE |
| user_id | int, FK → user.user_id | ON DELETE CASCADE |
| role_id | int, FK → role.role_id | reuses existing `role` table (Admin/Member/Mentor/TA); role is per-membership, not per-user |
| created_at | timestamptz | |

### `activity_type`
| column | type | notes |
|---|---|---|
| activity_type_id | int, PK | |
| name | varchar(256) | |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |
| updated_at | timestamptz | |
| updated_by | int, FK → user.user_id | |

### `activity_version`
| column | type | notes |
|---|---|---|
| activity_version_id | int, PK | |
| activity_type_id | int, FK → activity_type.activity_type_id | ON DELETE CASCADE |
| version_number | int | manual bump via explicit "Create Activity Version" action, not auto |
| header_text | varchar(512) | default header shown when a module is created from this version |
| activity_file | text | required; the file with the module's default code sections |
| elm_json_file | text | required; declares this activity's imports/dependencies |
| html_file | text | required; template with `{ elmjs }` / `{ modulename }` placeholders |
| overview_markdown | text | shown to student as instructions |
| server_config | varchar(512) | purpose unconfirmed — see `elm-plan` open question |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |

### `activity_extra_file`
| column | type | notes |
|---|---|---|
| extra_file_id | int, PK | |
| activity_version_id | int, FK → activity_version.activity_version_id | ON DELETE CASCADE |
| file_name | varchar(256) | |
| content | text | optional extra files imported by the main activity file |

### `project_template`
| column | type | notes |
|---|---|---|
| project_template_id | int, PK | |
| name | varchar(256) | |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |
| updated_at | timestamptz | |
| updated_by | int, FK → user.user_id | |

### `project_template_file`
| column | type | notes |
|---|---|---|
| file_id | int, PK | |
| project_template_id | int, FK → project_template.project_template_id | ON DELETE CASCADE |
| parent_folder_id | int, FK → project_template_file.file_id, nullable | self-referencing folder tree; null = template root |
| file_name | varchar(256) | |
| is_folder | bool | folder vs file node |
| initial_code | text, nullable | seed code; null for folder nodes |

### `project`
| column | type | notes |
|---|---|---|
| project_id | int, PK | |
| name | varchar(256) | |
| owner_id | int, FK → user.user_id | |
| project_template_id | int, FK → project_template.project_template_id | scaffold copied in at creation time |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |
| updated_at | timestamptz | |
| updated_by | int, FK → user.user_id | |

### `project_folder`
| column | type | notes |
|---|---|---|
| folder_id | int, PK | |
| project_id | int, FK → project.project_id | ON DELETE CASCADE |
| parent_folder_id | int, FK → project_folder.folder_id, nullable | self-referencing; null = project root; nesting depth capped (default 10, admin-configurable per user) |
| name | varchar(256) | |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |

### `module`
| column | type | notes |
|---|---|---|
| module_id | int, PK | |
| name | varchar(256) | |
| activity_version_id | int, FK → activity_version.activity_version_id | pins module to the version it was created against |
| project_id | int, FK → project.project_id, nullable | null = personal "My Elm Modules"; set = lives only in that project's namespace |
| folder_id | int, FK → project_folder.folder_id, nullable | which folder within the project; null = project root (irrelevant if project_id is null) |
| code | text | the module's Elm source |
| last_modified_time | timestamptz | |
| last_modified_by | int, FK → user.user_id | |
| last_opened_time | timestamptz, nullable | null = never opened by a named user |
| last_opened_by | int, FK → user.user_id, nullable | |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |

### `resource_type`
| column | type | notes |
|---|---|---|
| resource_type_id | int, PK | |
| name | varchar(64), unique | e.g. `activity_type`, `activity_version`, `project_template`, `project`, `module` — lookup table so new resource types are a row insert, not a migration |

### `resource_access_override`
| column | type | notes |
|---|---|---|
| override_id | int, PK | |
| resource_type_id | int, FK → resource_type.resource_type_id | which table `resource_id` points into |
| resource_id | int | polymorphic — points into whichever table `resource_type_id` names |
| group_id | int, FK → group.group_id, nullable | exactly one of `group_id` / `user_id` set |
| user_id | int, FK → user.user_id, nullable | direct-to-user grant; always wins over group/role-derived access |
| access_level | enum('view','edit','deny') | |
| created_at | timestamptz | |
| created_by | int, FK → user.user_id | |
