# Caffeine Lane — Testing

> Test strategy, data boundaries, browser verification, and CI quality gates.

## Strategy

Caffeine Lane separates verification by boundary:

- Django/ORM tests cover application behavior and domain rules.
- Node.js tests verify the authored/generated frontend asset pipeline.
- Playwright exercises important browser interactions against a locally served Django application.
- CI validates production settings and the production Docker image in addition to the application suites.

The project reports Python coverage through `pytest-cov`, but it does not currently enforce a minimum coverage percentage.

## Test layers

| Layer | Purpose | Tool / location |
| --- | --- | --- |
| Django / ORM | Accounts, permissions, forms, editorial lifecycle, comments, search behavior, management commands, and settings-sensitive behavior | Pytest + pytest-django under `apps/**/tests/` |
| Frontend assets | Build output and JavaScript asset behavior | Node.js test runner under `tests/frontend/` |
| Browser smoke | User-facing browser interactions against a local Django server | Playwright / Chromium under `tests/e2e/` |
| Production settings check | Validate Django's production configuration with `check --deploy` | GitHub Actions |
| Docker smoke | Build and start the production image; verify health/public/static endpoints and generated assets | Docker in GitHub Actions |

## Test data and dependencies

### Django tests

`config.settings.test` uses:

- SQLite in memory by default;
- Django's in-memory email backend;
- in-memory uploaded-media storage;
- a fast MD5 password hasher for test execution.

CI overrides the database with `TEST_DATABASE_URL`, so the Python test suite runs against a PostgreSQL 18 service on Python 3.14.

This distinction is intentional: the default suite stays easy to run locally, while CI verifies database-sensitive behavior against PostgreSQL.

### Browser tests

Playwright starts a Django server at:

```text
http://127.0.0.1:8000
```

and waits for:

```text
/healthz/
```

The configuration uses Chromium, one worker, and retained traces on failure.

Locally, the browser suite can use the normal development database. CI instead prepares a dedicated SQLite database, applies migrations, seeds portfolio content, and creates browser-test records before running Playwright.

## Critical behavior

The suites protect behavior such as:

- email-based authentication and account/profile flows;
- draft vs published editorial visibility;
- post slug and publication validation;
- one-level comment replies and moderation permissions;
- search/filter/pagination behavior;
- image validation;
- management-command safety checks;
- contact-form error handling;
- generated frontend assets and browser interactions.

Production security configuration is checked separately with Django's `check --deploy`; test settings intentionally use simplified password hashing and storage for speed/isolation.

## Run locally

### Python

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest
```

`uv run pytest` includes coverage reporting for `apps` and `config`.

### Frontend assets

```bash
pnpm run build
pnpm test
```

### Browser

Install Chromium once:

```bash
pnpm exec playwright install chromium
```

Then:

```bash
pnpm run test:e2e
```

Playwright starts Django automatically through `playwright.config.mjs`.

If `E2E_DATABASE_URL` is supplied, it takes precedence for the browser-test server; otherwise the Django local environment resolves its normal database configuration.

## CI

`.github/workflows/ci.yml` contains two main jobs.

### Python / application job

For Python 3.14, CI:

1. starts PostgreSQL 18;
2. installs the locked Python environment;
3. runs Ruff lint/format checks;
4. checks for missing Django migrations;
5. runs pytest against PostgreSQL;
6. validates production settings with `manage.py check --deploy`;
7. installs frontend dependencies;
8. builds and tests generated frontend assets;
9. prepares isolated browser data;
10. installs Playwright Chromium;
11. runs the browser smoke suite.

### Docker smoke

A separate job:

1. builds the production Docker image;
2. verifies that a generated JavaScript asset in the image matches the authored source;
3. starts the image with isolated CI configuration;
4. waits for `/healthz/`;
5. checks a public page and generated static assets.

## Pre-release verification

A useful local verification sequence is:

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

The authoritative CI workflow remains `.github/workflows/ci.yml`; do not document a single release command unless the repository actually adds one.

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Deployment](DEPLOYMENT.md)
