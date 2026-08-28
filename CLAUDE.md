# elm-backend

FastAPI RBAC backend. MySQL via SQLAlchemy + Alembic. Auth: JWT access token + opaque UUID refresh token, looked up in the `refresh_token` table (`app/oauth2.py`, `app/routers/auth`).

## Tooling
- Dependency manager: `uv` (not pip/virtualenv). `pyproject.toml` + `uv.lock` are the source of truth — `requirements.txt` is gone.
- Run anything with `uv run <cmd>` (e.g. `uv run uvicorn app.main:app --reload`, `uv run alembic upgrade head`).
- Add/remove deps: `uv add <pkg>` / `uv remove <pkg>` — never hand-edit dependency versions in `pyproject.toml`, and always commit `uv.lock` alongside.
- Pinned Python: 3.12 (see `.python-version`). `mysqlclient` needs `pkg-config` + MySQL client headers on the host (see `Setup.md` for the macOS brew fix).
- See [Setup.md](Setup.md) for full local setup, [DB_SCHEMA.md](DB_SCHEMA.md) for the current table structure, [DB_DIAGRAM.md](DB_DIAGRAM.md) for the visual ER diagram.

## Structure
- `app/db/` — SQLAlchemy models (`auth.py`). `app/models.py` just re-exports them.
- `app/schemas/` — Pydantic request/response schemas, mirrors `app/db/` grouping.
- `app/routers/` — FastAPI routers. `root/` holds Root-only routers, one file per domain (currently just `root/user.py`) — every route in every file there is gated by `Depends(require_root)`, both at the router level and as each route's `current_user` param.
- `app/constants.py` — role-name constants (`ROOT_ROLE_NAME`, `SYSTEM_ROLE_NAME`, `ADMIN_ROLE_NAME`, `APP_USER_ROLE_NAME`, `USER_MANAGEMENT_ROLE_NAMES`). Import these rather than hardcoding role-name strings.
- `app/utils/` — shared helpers (auth, http, file, time).
- `alembic/` — migrations. Run `uv run alembic revision --autogenerate -m "..."` after model changes, then `uv run alembic upgrade head`.

## Errors
Every error response (ours, FastAPI's, validation, unhandled) comes out shaped the same:
`{"errors": [{"code", "title", "detail", "status", "instance", "meta"?}]}` — see the handlers in
`app/utils/http.py`, wired up in `app/main.py`. Raise, don't return: call `not_found("message")`,
`forbidden(...)`, `unauthorized(...)`, etc. from `app/utils/http.py` — they raise `HTTPException`
internally, so the call interrupts the request whether or not you `return` it (no more silently
falling through to a 200 if you forget the `return`). Pass `headers={"WWW-Authenticate": "Bearer"}`
for auth challenges, or `code="SOME_CODE"` to override the default status-derived code. Pass a
list instead of a single string/dict to send several errors in one response — each item becomes
its own entry in `errors` and can override its own `"status"`/`"code"`.

## RBAC model
`role` ←→ `user` via `user_role` (many-to-many). `update_password_log` and `refresh_token` are auxiliary to `user`. Full column list in [DB_SCHEMA.md](DB_SCHEMA.md).

There's only one Root account: `app/utils/auth.is_root()` checks a user_id against the `ROOT_USER_ID` env var (`app/config.py`), not a role; `app/oauth2.require_root()` wraps that check as a dependency for everything under `app/routers/root/`. `app/oauth2.require_root_or_admin()` is the equivalent gate for routes Root and Admin both manage.

Root is invisible in listings: `GET /user/all` excludes `ROOT_USER_ID` when set.

Password changes: `POST /user/update-own-password` (any authenticated user, requires current password) and `POST /root/user/update-password` (Root only, resets any user's password without the old one) — both log to `update_password_log`.

`GET /user/all` and `POST /user/info` (for another user) are gated to Root/Admin via `app/utils/auth.can_manage_users()` — anyone else can only look up their own info (`POST /user/info` with their own `user_id`, or `GET /user/me`).

## Commits
Terse commit messages. No `Co-Authored-By` trailer.
