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
