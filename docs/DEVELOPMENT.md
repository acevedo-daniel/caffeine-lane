# Caffeine Lane — Development

> Local setup, environment configuration, asset workflow, and database lifecycle.

## Requirements

| Tool | Version / requirement | Source |
| --- | --- | --- |
| Python | `>=3.14,<3.15` | `pyproject.toml` |
| uv | Required for the locked Python environment | `uv.lock` / project workflow |
| Node.js | 22.x used by CI and the asset build | CI / Dockerfile |
| pnpm | `10.18.3` | `package.json` |
| Docker Compose | Required for the default local PostgreSQL workflow | `compose.yaml` |
| PostgreSQL | 18 in the provided local Compose service | `compose.yaml` |

## Initial setup

From the repository root:

```powershell
Copy-Item .env.example .env
docker compose up -d db
uv sync --locked
pnpm install --frozen-lockfile
pnpm run build
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
uv run python manage.py seed_portfolio
```

On macOS or Linux, replace `Copy-Item .env.example .env` with:

```bash
cp .env.example .env
```

## Local environment

`.env.example` contains development-safe defaults. Real secrets must stay outside version control.

Local development uses `config.settings.local`, which explicitly enables Django debug mode.

| Variable | Required locally | Purpose |
| --- | :---: | --- |
| `DJANGO_SETTINGS_MODULE` | Yes | Selects the Django settings module; local default is `config.settings.local`. |
| `SECRET_KEY` | Yes | Local signing key. The example value is development-only. |
| `DATABASE_URL` | No | Database connection. The example points to Compose PostgreSQL; omitting it enables the SQLite fallback. |
| `ALLOWED_HOSTS` | No | Allowed local hosts. |
| `CSRF_TRUSTED_ORIGINS` | No | Trusted origins for local form requests. |
| `DEBUG_TOOLBAR_ENABLED` | No | Enables Django Debug Toolbar locally. |
| `DEFAULT_FROM_EMAIL` | No | Sender used by the local console email flow. |
| `CONTACT_RECIPIENT_EMAIL` | No | Recipient used while exercising the contact form. |
| `PASSWORD_RESET_ENABLED` | No | Controls whether the password-reset UI/flow is available. |

Provider credentials and production security settings are documented in [Deployment](DEPLOYMENT.md), not in the local workflow.

## Run locally

Run the frontend asset watcher in one terminal:

```bash
pnpm run dev
```

Run Django in another:

```bash
uv run python manage.py runserver
```

Open:

```text
http://localhost:8000
```

The local email backend writes messages to the Django process output. Uploaded media is stored on the local filesystem.

## Commands

| Task | Command | Purpose |
| --- | --- | --- |
| Start database | `docker compose up -d db` | Start local PostgreSQL 18. |
| Stop database | `docker compose down` | Stop Compose while preserving the named volume. |
| Install Python deps | `uv sync --locked` | Reproduce the locked Python environment. |
| Install frontend deps | `pnpm install --frozen-lockfile` | Reproduce the locked asset-tooling environment. |
| Build assets | `pnpm run build` | Build minified CSS and JavaScript into `static/dist/`. |
| Watch assets | `pnpm run dev` | Rebuild authored frontend assets during development. |
| Run Django | `uv run python manage.py runserver` | Start the development server. |
| Django checks | `uv run python manage.py check` | Run Django system checks. |
| Migration drift | `uv run python manage.py makemigrations --check --dry-run` | Detect model changes without committed migrations. |
| Apply migrations | `uv run python manage.py migrate` | Apply committed Django migrations. |
| Baseline guard | `uv run python manage.py check_fresh_baseline` | Reject a legacy database using the old profile baseline. |
| Seed portfolio | `uv run python manage.py seed_portfolio` | Populate the maintained demo/portfolio dataset. |
| Create admin | `uv run python manage.py createsuperuser` | Create a local Django administrator. |
| Python tests | `uv run pytest` | Run pytest/pytest-django with coverage reporting. |
| Lint | `uv run ruff check .` | Run Ruff lint checks. |
| Format check | `uv run ruff format --check .` | Verify Ruff formatting. |
| Frontend tests | `pnpm test` | Run Node.js asset-pipeline tests. |
| Browser tests | `pnpm run test:e2e` | Run the Playwright browser suite. |

## Database workflow

The copied `.env.example` points local development to the PostgreSQL 18 Compose service:

```bash
docker compose up -d db
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
```

`check_fresh_baseline` inspects the selected database before migrations. If the legacy `accounts_profile` table exists, the command stops and requires a fresh/reset database rather than attempting to migrate the incompatible authentication baseline in place.

If `DATABASE_URL` is omitted, local settings fall back to:

```text
db.sqlite3
```

That fallback is useful for isolated/offline work, but PostgreSQL is the intended local path when verifying database-specific behavior such as ranked search.

## Demo data

```bash
uv run python manage.py seed_portfolio
```

The portfolio seed creates a repeatable content set used for local/demo presentation and automated browser setup.

Production startup does **not** seed by default. The container only runs `seed_portfolio` when `SEED_PORTFOLIO_ON_START=true` is explicitly set.

## Generated frontend assets

Authored frontend files live in:

```text
static/src/
```

Generated runtime assets live in:

```text
static/dist/
```

Use:

```bash
pnpm run build
```

or:

```bash
pnpm run dev
```

Do not edit `static/dist/` manually.

The production Docker image rebuilds these assets in its Node stage before the Django runtime image is assembled.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| CSS/JS changes are missing | Run `pnpm run dev` or rebuild with `pnpm run build`; do not edit `static/dist/`. |
| No editorial content is visible | Apply migrations and run `seed_portfolio` in a disposable/local environment. |
| `check_fresh_baseline` fails | The selected database contains the incompatible legacy profile baseline; use a fresh database or reset disposable local data. |
| Local email is not delivered externally | Expected: local settings use Django's console email backend. |

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
