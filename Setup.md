# Local Setup

- Install `uv` (one-time, per machine): `brew install uv` (macOS) or see https://docs.astral.sh/uv/getting-started/installation/
- In the Project Root Directory, run `uv sync`. This reads `pyproject.toml` + `uv.lock`, installs the pinned Python (3.12, see `.python-version`) if missing, creates `.venv`, and installs exact locked dependency versions.
- No manual venv activation needed — prefix commands with `uv run`, e.g. `uv run alembic upgrade head`, `uv run uvicorn app.main:app --reload`. (Or run `source .venv/bin/activate` once if you prefer the old habit.)
- To add a new dependency: `uv add <package>`. To remove one: `uv remove <package>`. Both update `pyproject.toml` and `uv.lock` — commit both.
- Start a MySQL-compatible server:
  - Windows/Linux: Xampp Server (Apache and MySQL)
  - macOS: MariaDB (see [macOS: MariaDB setup](#macos-mariadb-setup) below)
- Create an empty database `database_name`
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
```

- On macOS, `uv sync` may fail building `mysqlclient` with `Can not find valid pkg-config name` if the env vars below aren't set — see [macOS: MariaDB setup](#macos-mariadb-setup).

- now run `uv run alembic upgrade head` in the CLI. This will create the tables.

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
