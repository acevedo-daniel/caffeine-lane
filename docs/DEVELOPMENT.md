# Development

> Local setup, environment configuration, database lifecycle, and developer workflow.

## Requirements

| Tool               | Supported / required version             | Source           |
| ------------------ | ---------------------------------------- | ---------------- |
| **Python**         | `>=3.13,<3.15`                           | `pyproject.toml` |
| **uv**             | Current stable version                   | `uv.lock`        |
| **Node.js**        | `22.x`                                   | `package.json`   |
| **pnpm**           | `10.18.3`                                | `package.json`   |
| **PostgreSQL**     | `18`                                     | `compose.yaml`   |
| **Docker Compose** | Current Docker Desktop / Compose release | `compose.yaml`   |

## Initial Setup

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

On Windows PowerShell, replace `cp .env.example .env` with:

```powershell
Copy-Item .env.example .env
```

## Environment Boundary

`.env.example` provides safe local defaults. Never commit secrets to version control. Local development uses `config.settings.local`, which fixes `DEBUG=True` (the `DEBUG` variable is intentionally not an environment flag).

### Local Environment Variables

| Variable                  | Required locally | Purpose                                                                 | Local default                                                           |
| ------------------------- | :--------------: | ----------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| `DJANGO_SETTINGS_MODULE`  |       Yes        | Active settings module.                                                 | `config.settings.local`                                                 |
| `SECRET_KEY`              |       Yes        | Local cryptographic signing key.                                        | `change-me-locally`                                                     |
| `DATABASE_URL`            |        No        | PostgreSQL connection. If omitted, falls back to SQLite (`db.sqlite3`). | `postgresql://caffeine-lane:caffeine-lane@localhost:5432/caffeine-lane` |
| `ALLOWED_HOSTS`           |        No        | Permitted hostnames.                                                    | `localhost,127.0.0.1`                                                   |
| `CSRF_TRUSTED_ORIGINS`    |        No        | Trusted origins for form POST requests.                                 | `http://localhost:8000`                                                 |
| `DEBUG_TOOLBAR_ENABLED`   |        No        | Enables Django Debug Toolbar in local browser sessions.                 | `false`                                                                 |
| `DEFAULT_FROM_EMAIL`      |        No        | Sender email address for console email backend.                         | `noreply@example.com`                                                   |
| `CONTACT_RECIPIENT_EMAIL` |        No        | Recipient email address for contact form testing.                       | `owner@example.com`                                                     |
| `PASSWORD_RESET_ENABLED`  |        No        | Controls password reset flow availability.                              | `false`                                                                 |

### Production Environment Variables

Production environments require managed cloud provider credentials (`DATABASE_URL`, `DIRECT_DATABASE_URL`, `CLOUDINARY_URL`, `RESEND_API_KEY`, `SECRET_KEY`, and security headers) configured via Render. See [Deployment](DEPLOYMENT.md) for full details.

## Run Locally

Run the frontend asset watcher in one terminal:

```bash
pnpm run dev
```

Run the Django development server in another terminal:

```bash
uv run python manage.py runserver
```

Open `http://localhost:8000`. The frontend watcher rebuilds Tailwind CSS 4 and mirrors JavaScript controllers from `static/src/` into `static/dist/`.

## Command Matrix

| Task                    | Command                                   | Description                                                    |
| ----------------------- | ----------------------------------------- | -------------------------------------------------------------- |
| **Start database**      | `docker compose up -d db`                 | Starts the local PostgreSQL 18 container.                      |
| **Stop database**       | `docker compose down`                     | Stops the database container while preserving volume data.     |
| **Install Python deps** | `uv sync --locked`                        | Installs locked Python dependencies via `uv`.                  |
| **Install JS deps**     | `pnpm install --frozen-lockfile`          | Installs locked frontend dependencies via `pnpm`.              |
| **Build assets**        | `pnpm run build`                          | Compiles minified CSS and bundles production JS.               |
| **Watch assets**        | `pnpm run dev`                            | Watches `static/src/` and compiles to `static/dist/`.          |
| **Run server**          | `uv run python manage.py runserver`       | Starts Django HTTP server on port 8000.                        |
| **Format check**        | `uv run ruff format --check .`            | Verifies code formatting with Ruff.                            |
| **Lint**                | `uv run ruff check .`                     | Executes Ruff linter checks.                                   |
| **Django checks**       | `uv run python manage.py check`           | Runs Django system sanity checks.                              |
| **Migrations**          | `uv run python manage.py migrate`         | Applies pending database migrations.                           |
| **Seed portfolio**      | `uv run python manage.py seed_portfolio`  | Creates the 3-category, 19-post demo dataset with WebP covers. |
| **Unit tests**          | `uv run pytest`                           | Runs Django pytest suite with coverage.                        |
| **Frontend tests**      | `pnpm test`                               | Runs Node.js asset pipeline tests.                             |
| **E2E smoke tests**     | `pnpm run test:e2e`                       | Executes Playwright browser smoke test suite.                  |
| **Create admin**        | `uv run python manage.py createsuperuser` | Interactively creates a Django administrator.                  |

## Database Lifecycle & Seeding

- **PostgreSQL 18:** Default local persistence via Docker Compose.
- **SQLite Fallback:** If `DATABASE_URL` is omitted, Django automatically creates a local `db.sqlite3` file for offline development.
- **Fresh Baseline Guard:** `check_fresh_baseline` inspects the active database to ensure compatibility with the modern custom user schema.
- **Portfolio Seed:** `seed_portfolio` is an idempotent content bootstrap that populates the 3 structural categories (`builds`, `guides`, `reviews`) and 19 curated sample posts with local WebP assets.

## Troubleshooting

| Problem                            | Cause                                                | Resolution                                                                  |
| ---------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------- |
| **Styles/JS not updating**         | Asset watcher not running.                           | Run `pnpm run dev` or `pnpm run build`. Never edit `static/dist/` directly. |
| **No posts visible on Home**       | Unseeded database.                                   | Run `uv run python manage.py migrate` followed by `seed_portfolio`.         |
| **`check_fresh_baseline` failure** | Database contains obsolete `accounts_profile` table. | Drop the legacy local database/volume and recreate fresh.                   |
| **Emails not received locally**    | Development uses Django console email backend.       | Check the terminal stdout output running `runserver`.                       |

## Related Documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Testing](TESTING.md)
- [Deployment](DEPLOYMENT.md)
