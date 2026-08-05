# elm-backend

FastAPI RBAC backend. MySQL via SQLAlchemy + Alembic. Auth: JWT access + refresh tokens (`app/oauth2.py`, `app/routers/auth`).

## Tooling
- Dependency manager: `uv` (not pip/virtualenv). `pyproject.toml` + `uv.lock` are the source of truth — `requirements.txt` is gone.
- Run anything with `uv run <cmd>` (e.g. `uv run uvicorn app.main:app --reload`, `uv run alembic upgrade head`).
- Add/remove deps: `uv add <pkg>` / `uv remove <pkg>` — never hand-edit dependency versions in `pyproject.toml`, and always commit `uv.lock` alongside.
- Pinned Python: 3.12 (see `.python-version`). `mysqlclient` needs `pkg-config` + MySQL client headers on the host (see `Setup.md` for the macOS brew fix).
- See [Setup.md](Setup.md) for full local setup, [DB_SCHEMA.md](DB_SCHEMA.md) for the current table structure, [DB_DIAGRAM.md](DB_DIAGRAM.md) for the visual ER diagram.

## Structure
- `app/db/` — SQLAlchemy models, one file per domain (`auth.py`, `endpoints.py`). `app/models.py` just re-exports them.
- `app/schemas/` — Pydantic request/response schemas, mirrors `app/db/` grouping.
- `app/routers/` — FastAPI routers.
- `app/utils/` — shared helpers (auth, http, file, time).
- `alembic/` — migrations. Run `uv run alembic revision --autogenerate -m "..."` after model changes, then `uv run alembic upgrade head`.

## RBAC model
`role` ←→ `user` via `user_role` (many-to-many). `endpoint` ←→ `role` via `endpoint_role` controls which roles can hit which endpoint. `update_password_log` and `refresh_token` are auxiliary to `user`. Full column list in [DB_SCHEMA.md](DB_SCHEMA.md).

## Commits
Terse commit messages. No `Co-Authored-By` trailer.
