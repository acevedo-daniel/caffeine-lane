# Development

## Requirements

| Tool | Supported version |
|---|---|
| Python | `>=3.13,<3.15` |
| uv | Current version compatible with `uv.lock` |
| Node.js | 22 |
| pnpm | 10.18.3 |
| PostgreSQL | 18 through Docker Compose for the normal local workflow |
| Docker Compose | Current Docker Desktop / Compose release |

## Initial configuration

```bash
git clone https://github.com/acevedo-daniel/caffeine-lane.git
cd caffeine-lane
cp .env.example .env
docker compose up -d db
uv sync --locked
pnpm install --frozen-lockfile
pnpm run build
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
uv run python manage.py seed_portfolio
```

In PowerShell, replace `cp .env.example .env` with `Copy-Item .env.example .env`.

## Environment variables

`.env.example` is the canonical safe local variable list. Do not add secrets to the repository. Local development uses `config.settings.local`, which fixes `DEBUG=True`; `DEBUG` is intentionally not an environment variable.

| Variable | Required | Purpose |
|---|:---:|---|
| `DJANGO_SETTINGS_MODULE` | Local | Use `config.settings.local` for normal development. |
| `SECRET_KEY` | Local | Local Django signing key. |
| `DATABASE_URL` | No locally | Compose PostgreSQL connection. If omitted, local settings deliberately fall back to SQLite. |
| `ALLOWED_HOSTS` | No locally | Hosts accepted by the local server. |
| `CSRF_TRUSTED_ORIGINS` | No locally | Trusted local form origins. |
| `DEBUG_TOOLBAR_ENABLED` | No | Enables Django Debug Toolbar only in local settings. |
| `DEFAULT_FROM_EMAIL` | No locally | Sender shown by local console email. |
| `CONTACT_RECIPIENT_EMAIL` | No locally | Contact recipient used by the local console backend. |
| `CONTACT_RATE_LIMIT` / `CONTACT_RATE_LIMIT_WINDOW` | No | Contact form request limit and its window in seconds. |
| `PASSWORD_RESET_ENABLED` | No | Enables password-reset delivery. Tests enable it; public demo configuration keeps it disabled. |
| Production-only provider and startup variables | No locally | `DIRECT_DATABASE_URL`, `CLOUDINARY_URL`, `RESEND_API_KEY`, `RUN_MIGRATIONS_ON_START`, `SEED_PORTFOLIO_ON_START`, `USE_X_FORWARDED_PROTO`, CSP, and HSTS variables are documented in [Deployment](DEPLOYMENT.md). |

## Run locally

Run the frontend watcher in one terminal:

```bash
pnpm run dev
```

Run Django in another terminal:

```bash
uv run python manage.py runserver
```

Open <http://localhost:8000>. The watcher rebuilds Tailwind CSS and mirrors every JavaScript change from `static/src/js` into `static/dist/js`. It is safe to use on Windows and Linux. `runserver` serves the generated output.

## Main commands

| Command | Purpose |
|---|---|
| `docker compose up -d db` | Start local PostgreSQL 18. |
| `docker compose down` | Stop the local database while retaining its volume. |
| `uv sync --locked` | Install locked Python dependencies. |
| `pnpm install --frozen-lockfile` | Install locked frontend dependencies. |
| `pnpm run dev` | Watch CSS and JavaScript source assets. |
| `pnpm run build` | Produce deterministic production CSS and JavaScript assets. |
| `uv run python manage.py runserver` | Start the local Django server. |
| `uv run python manage.py check` | Run Django system checks with local settings. |
| `uv run python manage.py migrate` | Apply database migrations. |
| `uv run python manage.py seed_portfolio` | Create or update the 3-category, 19-post portfolio dataset. |
| `uv run python manage.py seed_demo` | Create a smaller three-post dataset without images. |
| `uv run python manage.py verify_portfolio_baseline` | Confirm the structural category migration and categories exist. |
| `uv run python manage.py createsuperuser` | Create an administrator interactively in the active local database. |

## Database / migrations

Compose PostgreSQL is the normal local database. SQLite is available only as an intentional isolated fallback: omit `DATABASE_URL` and Django uses `db.sqlite3`.

Before the first migration, run `check_fresh_baseline`. It stops if it finds an `accounts_profile` table because that database does not match the current custom user schema. The command never deletes data; create a fresh database or local volume after backing up anything that must be retained.

Run `seed_portfolio` after migrations for the full local catalogue. It creates or updates three structural categories and nineteen published posts, uploads the bundled WebP covers to the active local media storage, and creates only a non-privileged author with an unusable password. Run it deliberately: it can update the sample posts it owns.

## Relevant structure

```text
apps/accounts/        Custom users, registration, profiles, password flows
apps/core/            Public pages, contact, health, CSP reports
apps/posts/           Editorial models, search, comments, commands
assets/portfolio/     Source images consumed by seed_portfolio
config/settings/      Base, local, test, and production settings
docker/               Production startup entrypoint
static/src/           Authored CSS and JavaScript
static/dist/          Generated runtime frontend assets
templates/            Shared layouts, components, and page templates
```

## Common problems

| Problem | Resolution |
|---|---|
| JavaScript change is not visible | Keep `pnpm run dev` running. It regenerates `static/dist/js`; do not edit that generated directory. |
| No posts appear locally | Run migrations and then `uv run python manage.py seed_portfolio`. |
| Migration check reports `accounts_profile` | Use a fresh compatible local database or volume; do not force migrations over that schema. |
| Local email seems not to send | Local settings use Django's console backend. Read the terminal output instead of expecting external delivery. |
| Debug Toolbar is absent | Set `DEBUG_TOOLBAR_ENABLED=true` in `.env`, restart `runserver`, and visit from `127.0.0.1`. |

Local behavior intentionally differs from production: it uses `DEBUG=True`, filesystem media, console email, optional Debug Toolbar, and Compose PostgreSQL or SQLite. Production uses `DEBUG=False`, Cloudinary media, Resend, WhiteNoise, Neon, and Gunicorn; see [Deployment](DEPLOYMENT.md).
