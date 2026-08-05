# Local Setup

- Install `uv` (one-time, per machine): `brew install uv` (macOS) or see https://docs.astral.sh/uv/getting-started/installation/
- In the Project Root Directory, run `uv sync`. This reads `pyproject.toml` + `uv.lock`, installs the pinned Python (3.12, see `.python-version`) if missing, creates `.venv`, and installs exact locked dependency versions.
- No manual venv activation needed — prefix commands with `uv run`, e.g. `uv run alembic upgrade head`, `uv run uvicorn app.main:app --reload`. (Or run `source .venv/bin/activate` once if you prefer the old habit.)
- To add a new dependency: `uv add <package>`. To remove one: `uv remove <package>`. Both update `pyproject.toml` and `uv.lock` — commit both.
- Start a MySQL-compatible server:
  - Windows/Linux: Xampp Server (Apache and MySQL)
  - macOS: MariaDB (see [macOS: MariaDB setup](#macos-mariadb-setup) below)
- Create an empty database `database_name`
- Create a dedicated DB user for the app — do **not** put `root` in `.env` (see [Database user: don't use root](#database-user-dont-use-root) below)
- Setup the `.env` with appropriate values. Sample config is below.

```r
DATABASE_HOSTNAME=localhost
DATABASE_PORT=3306
DATABASE_USERNAME= database_username
DATABASE_PASSWORD= database_password
DATABASE_NAME=database_name
SECRET_KEY=randomTextWithAlpaNumericChars
REFRESH_TOKEN_SECRET_KEY=anotherRandomTextWithAlpaNumericChars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DEPLOYMENT_ENV=dev
CORS_ORIGINS=http://localhost:3000
```

`CORS_ORIGINS` is comma-separated (e.g. `http://localhost:3000,https://elm.example.com`) — add the frontend's deployed origin here on the VPS too, or API calls from the browser will be silently blocked by CORS.

- On macOS, `uv sync` may fail building `mysqlclient` with `Can not find valid pkg-config name` if the env vars below aren't set — see [macOS: MariaDB setup](#macos-mariadb-setup).

- now run `uv run alembic upgrade head` in the CLI. This will create the tables.

- Seed default data (roles, endpoints, endpoint-role mappings, dev-only Root/System/Admin users): `uv run python -m setup.db`. Data lives in `setup/db_data.py`, insert logic in `setup/db.py`. Safe to re-run — it skips rows that already exist (by role name, user email, endpoint name, endpoint+role pair) instead of duplicating.

- Start the API server : `uv run uvicorn app.main:app --reload`

- In one of the browser tab, open this url: http://127.0.0.1:8000/docs`

## macOS: MariaDB setup

Assumes fresh install (no existing MySQL/MariaDB on the machine).

```bash
brew install bison cmake fmt pkg-config
brew install mariadb
mysql.server start
brew services start mariadb
mysql
```

Add to your shell config (`.bashrc` / `.zshrc` / `.fishrc` / etc) — needed for `mysqlclient` (the Python package) to build against MariaDB:

```sh
# If you need to have bison first in your PATH, run:
export PATH="/opt/homebrew/opt/bison/bin:$PATH"

# For pkg-config to find mariadb you may need to set:
export PKG_CONFIG_PATH="/opt/homebrew/opt/mariadb/lib/pkgconfig"

# compiler flags: bison lib + openssl (merged, second export would've clobbered the first)
export LDFLAGS="-L/opt/homebrew/opt/bison/lib -L$(brew --prefix openssl)/lib"
export CPPFLAGS="-I$(brew --prefix openssl)/include"
```

Reload your shell (`source ~/.zshrc` or open a new tab) before running `uv sync`.

## Database user: don't use root

MariaDB (and stock MySQL on most Linux distros too) sets `root@localhost` up with the `unix_socket`/`auth_socket` plugin by default. That plugin ignores whatever password you give it and only lets you in if you're logged into the OS as a matching user — so `DATABASE_USERNAME=root` + any password in `.env` fails with `MySQLdb.OperationalError: (1698, "Access denied for user 'root'@'localhost'")`, always, no matter what you put in `DATABASE_PASSWORD`.

Fix: connect as your OS admin user (that's who `unix_socket` actually authenticates as) and create a real password-auth user scoped to just this app's DB:

```bash
mysql -e "
  CREATE DATABASE IF NOT EXISTS elm;
  CREATE USER IF NOT EXISTS 'elm_app'@'localhost' IDENTIFIED BY 'CHANGE_ME';
  GRANT ALL PRIVILEGES ON elm.* TO 'elm_app'@'localhost';
  FLUSH PRIVILEGES;
"
```

Then in `.env`:

```r
DATABASE_USERNAME=elm_app
DATABASE_PASSWORD=CHANGE_ME
DATABASE_NAME=elm
```

**On a VPS this is the same fix, same reason** — a fresh MySQL/MariaDB install on Linux ships with the same `auth_socket`/`unix_socket` default for `root`. Don't put server root creds in the app's `.env` there either; SSH in, run the same `CREATE USER` / `GRANT` against the prod DB name, and put that dedicated user + a real generated password into the VPS's `.env`. Scope the `GRANT` to that one database, not `*.*`.

### Known dependency issue: bcrypt vs passlib

`passlib==1.7.4` (pinned via `uv.lock`) breaks against `bcrypt>=4.1` — `hash()` in `app/utils/auth.py` fails with `AttributeError: module 'bcrypt' has no attribute '__about__'` or `ValueError: password cannot be longer than 72 bytes`. If `uv sync` ever pulls a newer bcrypt (e.g. after a lockfile refresh), re-pin it:

```bash
uv add "bcrypt<4.1"
```
