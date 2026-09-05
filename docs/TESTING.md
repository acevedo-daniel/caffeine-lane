# Caffeine Lane — Testing

> Test strategy, layers, data dependencies, and quality gates.

## Strategy

Caffeine Lane separates verification across distinct boundaries:

- Django and ORM tests cover backend application behavior, services, and domain rules.
- Node.js tests verify the authored and generated frontend asset pipeline.
- Playwright exercises critical user-facing browser interactions against a running Django instance.
- CI validates production security settings and verifies the containerized production Docker image.

Python coverage is measured through `pytest-cov` across `apps` and `config`.

## Test layers

| Layer | Purpose | Tool / location |
| --- | --- | --- |
| Django / ORM | Accounts, permissions, forms, editorial lifecycle, comments, search behavior, and management commands | Pytest + pytest-django in `apps/**/tests/` |
| Frontend assets | Asset pipeline build output, progressive enhancements, and JavaScript modules | Node.js test runner in `tests/frontend/` |
| Browser smoke | End-to-end user workflows against a real running Django server | Playwright / Chromium in `tests/e2e/` |
| Production settings | Validate Django's production security settings with `check --deploy` | GitHub Actions / Django system checks |
| Docker smoke | Build production container, verify bundled assets, and test health/public endpoints | Docker in GitHub Actions |

## Test data and dependencies

### Django tests

`config.settings.test` isolates test execution:

- SQLite in memory by default.
- In-memory email backend.
- In-memory uploaded-media storage.
- Fast MD5 password hasher to optimize test runtimes.

In CI, `TEST_DATABASE_URL` is set so the Python suite executes against a real PostgreSQL 18 service on Python 3.14. This distinction ensures fast local feedback while verifying database-specific behavior (such as PostgreSQL full-text search) in CI.

### Browser tests

Playwright starts an isolated Django test server at:

```text
http://127.0.0.1:8000
```

and waits for the readiness signal:

```text
/healthz/
```

The test runner uses Chromium, single-worker isolation, and retained failure traces. Locally, browser tests can run against the active development database; in CI, `scripts/prepare-e2e.mjs` provisions a dedicated database with migrations and editorial seed data prior to execution.

## Run tests

Execute local test suites:

```bash
# Python linting, format check, and Django system checks
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run

# Python test suite with coverage
uv run pytest

# Frontend asset build and unit tests
pnpm run build
pnpm test
```

## End-to-end verification

### Playwright browser suite

Install the Chromium browser binary (one-time setup):

```bash
pnpm exec playwright install chromium
```

Run browser smoke tests:

```bash
pnpm run test:e2e
```

Playwright automatically spawns and terminates the Django server defined in `playwright.config.mjs`. If `E2E_DATABASE_URL` is provided, it configures the database connection for the browser-test process.

## CI

Automated quality gates are managed in `.github/workflows/ci.yml` across two parallel jobs:

### Application suite

On Python 3.14:
1. Starts a PostgreSQL 18 service container.
2. Synchronizes the locked Python environment with uv.
3. Executes Ruff linting and formatting checks.
4. Verifies database schema for uncommitted migration drift.
5. Runs the Pytest suite against PostgreSQL with coverage.
6. Validates production security configuration via `python manage.py check --deploy`.
7. Installs frontend dependencies and runs Node asset tests.
8. Sets up isolated test data and executes Playwright browser tests.

### Docker smoke

A dedicated container verification job:
1. Builds the production multi-stage Docker image.
2. Verifies that compiled assets inside the image match authored source.
3. Launches the container in an isolated network environment.
4. Waits for `/healthz/` liveness.
5. Verifies public responses, static asset delivery, and HTTP headers.

## Pre-release verification

Recommended local pre-release verification sequence:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest
pnpm run build
pnpm test
pnpm run test:e2e
docker build -t caffeine-lane-local-check .
```

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Deployment](DEPLOYMENT.md)
