# DB Diagram

Rendered from [DB_SCHEMA.md](DB_SCHEMA.md). GitHub renders mermaid natively; for other viewers use https://mermaid.live or the VSCode "Markdown Preview Mermaid Support" extension.

```mermaid
erDiagram
    role {
        int role_id PK
        string role_name
        bool show_on_menu
        timestamp created_at
        timestamp updated_at
    }

    user {
        int user_id PK
        string full_name
        string email
        string user_name
        string password
        bool login_allowed
        bool is_deleted
        timestamp created_at
        timestamp updated_at
    }

    refresh_token {
        int refresh_token_id PK
        int user_id FK
        text refresh_token
        timestamp created_at
    }

    user_role {
        int user_role_id PK
        int user_id FK
        int role_id FK
        timestamp created_at
    }

    update_password_log {
        int log_id PK
        int user_id FK
        int updated_by FK
        timestamp updated_at
    }

    endpoint {
        int endpoint_id PK
        string endpoint_name
        bool is_common
        bool is_disabled
        string method
        text category
        timestamp created_at
        int created_by FK
        timestamp updated_at
        int updated_by FK
    }

    endpoint_role {
        int endpoint_role_id PK
        int endpoint_id FK
        int role_id FK
        timestamp created_at
    }

    user ||--o{ refresh_token : "has"
    user ||--o{ user_role : "assigned"
    role ||--o{ user_role : "assigned to"
    user ||--o{ update_password_log : "subject of"
    user ||--o{ update_password_log : "performed by"
    user ||--o{ endpoint : "created"
    user ||--o{ endpoint : "updated"
    endpoint ||--o{ endpoint_role : "grants via"
    role ||--o{ endpoint_role : "grants via"
```

## Reading it
- `user ↔ role` is many-to-many, joined through `user_role`.
- `endpoint ↔ role` is many-to-many, joined through `endpoint_role`. This is the actual permission check: a user can hit an endpoint if any of their roles appears in that endpoint's `endpoint_role` rows — unless `endpoint.is_common` (open to all) or `endpoint.is_disabled` (blocked for all), both checked before the role lookup.
- `update_password_log` has two FKs to `user` (subject + actor) — drawn as two separate relationships above since mermaid ER diagrams can't label a self-referencing pair on one line.

## Content model (draft)

Table proposal for the `elm-plan` product docs — not implemented in `app/db/` yet. Column detail and design rationale in [DB_SCHEMA.md](DB_SCHEMA.md#content-model-draft--not-yet-implemented).

```mermaid
erDiagram
    group {
        int group_id PK
        string name
        int parent_group_id FK
        timestamp created_at
        int created_by FK
        timestamp updated_at
        int updated_by FK
    }

    group_membership {
        int group_membership_id PK
        int group_id FK
        int user_id FK
        int role_id FK
        timestamp created_at
    }

    activity_type {
        int activity_type_id PK
        string name
        timestamp created_at
        int created_by FK
        timestamp updated_at
        int updated_by FK
    }

    activity_version {
        int activity_version_id PK
        int activity_type_id FK
        int version_number
        string header_text
        text activity_file
        text elm_json_file
        text html_file
        text overview_markdown
        string server_config
        timestamp created_at
        int created_by FK
    }

    activity_extra_file {
        int extra_file_id PK
        int activity_version_id FK
        string file_name
        text content
    }

    project_template {
        int project_template_id PK
        string name
        timestamp created_at
        int created_by FK
        timestamp updated_at
        int updated_by FK
    }

    project_template_file {
        int file_id PK
        int project_template_id FK
        int parent_folder_id FK
        string file_name
        bool is_folder
        text initial_code
    }

    project {
        int project_id PK
        string name
        int owner_id FK
        int project_template_id FK
        timestamp created_at
        int created_by FK
        timestamp updated_at
        int updated_by FK
    }

    project_folder {
        int folder_id PK
        int project_id FK
        int parent_folder_id FK
        string name
        timestamp created_at
        int created_by FK
    }

    module {
        int module_id PK
        string name
        int activity_version_id FK
        int project_id FK
        int folder_id FK
        text code
        timestamp last_modified_time
        int last_modified_by FK
        timestamp last_opened_time
        int last_opened_by FK
        timestamp created_at
        int created_by FK
    }

    resource_type {
        int resource_type_id PK
        string name
    }

    resource_access_override {
        int override_id PK
        int resource_type_id FK
        int resource_id
        int group_id FK
        int user_id FK
        string access_level
        timestamp created_at
        int created_by FK
    }

    group ||--o{ group_membership : "has members"
    role ||--o{ group_membership : "grants role in group"
    group ||--o{ group : "parent of"
    activity_type ||--o{ activity_version : "has versions"
    activity_version ||--o{ activity_extra_file : "includes"
    activity_version ||--o{ module : "seeds"
    project_template ||--o{ project_template_file : "scaffolds"
    project_template_file ||--o{ project_template_file : "nests"
    project_template ||--o{ project : "instantiated as"
    user ||--o{ project : "owns"
    project ||--o{ project_folder : "contains"
    project_folder ||--o{ project_folder : "nests"
    project ||--o{ module : "contains"
    project_folder ||--o{ module : "contains"
    group ||--o{ resource_access_override : "granted via"
    user ||--o{ resource_access_override : "granted directly"
    resource_type ||--o{ resource_access_override : "typed by"
```

### Reading it
- `group ||--o{ group : "parent of"` is the subgroup self-reference (`parent_group_id`) — a group can have child groups.
- `group_membership` is where per-Group role lives (`Admin`/`Member`/`Mentor`/`Not in group`, reusing the auth `role` table) — a user's role is per-Group, there is no flat `user.role` for content permissions.
- `module.activity_version_id` pins a module to the exact activity version it was created from, not just the activity type — new versions never retroactively change existing modules (versioning decision from [Activity Types](../elm-plan/05-activity-types.md)).
- `module.project_id` nullable: null means it's a personal "My Elm Modules" module; set means it lives only inside that project's namespace, never in the creator's personal list.
- `resource_access_override` is intentionally one generic table (`resource_type_id` + `resource_id`, polymorphic) rather than a separate override table per resource — covers activity types, activity versions, project templates, projects, and modules alike. A direct `user_id` grant/deny always wins over anything derived from `group_id`/role.
- `resource_type` is a lookup table, not a hardcoded enum — new overridable resource types are a row insert, no migration.
