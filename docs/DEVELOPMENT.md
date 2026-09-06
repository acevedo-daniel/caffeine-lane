# Caffeine Lane — Development

> Local setup, environment configuration, commands, and database workflow.

## Requirements

| Tool | Version | Source |
| --- | --- | --- |
| Python | `>=3.14,<3.15` | `pyproject.toml` |
| uv | Locked Python package manager | `uv.lock` |
| Node.js | `22.x` | `Dockerfile` / CI |
| pnpm | `10.18.3` | `package.json` |
| Docker Compose | Required for local PostgreSQL 18 | `compose.yaml` |
| PostgreSQL | 18 | `compose.yaml` |

## Setup

```bash
# Copy environment configuration
cp .env.example .env

# Start local PostgreSQL container
docker compose up -d db

# Install locked dependencies and build assets
uv sync --locked
pnpm install --frozen-lockfile
pnpm run build

# Run baseline verification, migrations, and demo seeding
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
uv run python manage.py seed_editorial
```

On Windows PowerShell, use `Copy-Item .env.example .env`.

## Local environment

`.env.example` contains development-safe default values. Local development uses `config.settings.local`, which explicitly enables Django debug mode.

| Variable | Required | Purpose |
| --- | :---: | --- |
| `DJANGO_SETTINGS_MODULE` | Yes | Selects the Django settings module; default is `config.settings.local`. |
| `SECRET_KEY` | Yes | Local signing key. The default value is development-only. |
| `DATABASE_URL` | No | Database connection string. Points to Compose PostgreSQL; omitting it enables the SQLite fallback. |
| `ALLOWED_HOSTS` | No | Allowed hostnames for local requests. |
| `CSRF_TRUSTED_ORIGINS` | No | Trusted origins for local form submissions. |
| `DEBUG_TOOLBAR_ENABLED` | No | Enables Django Debug Toolbar locally. |
| `DEFAULT_FROM_EMAIL` | No | Sender address used by local console email flow. |
| `CONTACT_RECIPIENT_EMAIL` | No | Recipient address when testing contact submissions. |
| `PASSWORD_RESET_ENABLED` | No | Controls whether password-reset UI and routes are enabled. |

Never include real secrets.

## Run locally

Run the frontend asset watcher in one terminal:

```bash
pnpm run dev
```

Run Django in another terminal:

```bash
uv run python manage.py runserver
```

Open:
- Application: `http://localhost:8000`
- Service health: `http://localhost:8000/healthz/`
- Admin interface: `http://localhost:8000/admin/`

The local email backend writes messages directly to the Django server log. Uploaded media is saved to the local filesystem.

Password recovery is disabled by default in local and production-like environments unless `PASSWORD_RESET_ENABLED=true` is explicitly configured. Do not enable it for a hosted environment until the Resend sender domain is verified and delivery has been tested.

The contact form requires CSRF, rejects the hidden honeypot field, limits each input length, and permits five submissions per hour by default. The rate limit uses Django's configured cache and is intentionally a basic best-effort guard in serverless deployments.

## Commands

| Task | Command | Purpose |
| --- | --- | --- |
| Start database | `docker compose up -d db` | Start local PostgreSQL 18 in background. |
| Stop database | `docker compose down` | Stop Compose services while preserving database volume. |
| Install Python deps | `uv sync --locked` | Install locked Python environment dependencies. |
| Install frontend deps | `pnpm install --frozen-lockfile` | Install locked Node.js asset-pipeline packages. |
| Build assets | `pnpm run build` | Build minified CSS and JavaScript into `static/dist/`. |
| Watch assets | `pnpm run dev` | Watch and rebuild frontend assets during development. |
| Run Django | `uv run python manage.py runserver` | Start the local Django development server. |
| Django system check | `uv run python manage.py check` | Validate Django configuration and models. |
| Check migration drift | `uv run python manage.py makemigrations --check --dry-run` | Detect uncommitted model changes without migrations. |
| Apply migrations | `uv run python manage.py migrate` | Apply pending Django migrations. |
| Baseline guard | `uv run python manage.py check_fresh_baseline` | Verify database does not contain legacy profile tables. |
| Verify editorial baseline | `uv run python manage.py verify_editorial_baseline` | Validate that structural categories and editorial constraints are met. |
| Seed editorial dataset | `uv run python manage.py seed_editorial` | Seed reproducible editorial articles and categories. |
| Create administrator | `uv run python manage.py createsuperuser` | Provision a local Django superuser. |
| Python tests | `uv run pytest` | Run Pytest suite with test coverage reporting. |
| Lint Python | `uv run ruff check .` | Run Ruff linter. |
| Format Python check | `uv run ruff format --check .` | Verify Ruff code formatting. |
| Frontend tests | `pnpm test` | Run Node.js asset-pipeline unit tests. |
| Browser tests | `pnpm run test:e2e` | Execute Playwright browser smoke test suite. |

## Database workflow

The copied `.env.example` points local development to the PostgreSQL 18 Compose service:

```bash
docker compose up -d db
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
uv run python manage.py verify_editorial_baseline
```

`check_fresh_baseline` inspects the selected database before migrations. If the legacy `accounts_profile` table exists, the command stops and requires a fresh or reset database rather than attempting to migrate the incompatible legacy authentication schema in place.

If `DATABASE_URL` is omitted, local settings fall back to:

```text
db.sqlite3
```

That fallback is convenient for isolated or offline work, but PostgreSQL is the recommended local path when verifying database-specific behavior such as ranked full-text search.

### Editorial dataset

```bash
uv run python manage.py seed_editorial --dry-run
uv run python manage.py seed_editorial
```

The editorial seed populates a curated Spanish-language content set used for local demonstration and automated browser tests. The dry run validates every slug, publication date, category distribution, text field, and bundled image without writing data.

Vercel deployments never seed automatically. Docker startup executes `seed_editorial` only when `SEED_EDITORIAL_ON_START=true` is explicitly provided.

### Vercel build contract

Vercel installs the Python environment from `pyproject.toml` and `uv.lock` automatically. Keep the Vercel project **Install Command** at its default. Because the repository also needs pnpm dependencies for Tailwind and the JavaScript asset copy, use this Vercel **Build Command**:

```bash
pnpm install --frozen-lockfile --prod=false && pnpm run build
```

The repository's `pyproject.toml` build hook remains `pnpm run build` for CI. If the Vercel build reports `ModuleNotFoundError: No module named 'django'`, remove the custom pnpm-only Install Command and redeploy so Vercel can restore the Python installation.

## Generated frontend assets

Authored frontend files live in:

```text
static/src/
```

Compiled distribution assets live in:

```text
static/dist/
```

Use:

```bash
pnpm run build
```

or during development:

```bash
pnpm run dev
```

Do not edit files inside `static/dist/` manually.

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| CSS or JS changes do not appear | Run `pnpm run dev` or rebuild with `pnpm run build`; never edit `static/dist/` directly. |
| No editorial content is visible | Apply migrations with `uv run python manage.py migrate` and run `uv run python manage.py seed_editorial`. |
| `check_fresh_baseline` fails | The active database contains incompatible legacy profile tables; switch to a clean database or reset disposable local data. |
| Local emails are not delivered externally | By design: local development settings route emails to Django's console backend. |
| Resend rejects hosted email | Keep password reset disabled until a Resend domain is verified; use the documented test recipient for controlled checks. |

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
