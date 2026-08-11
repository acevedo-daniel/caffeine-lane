# Testing

## Strategy

The test strategy combines Django tests for domain and request behavior, frontend asset checks, browser smoke tests for critical interactions, and a Docker smoke test. Together they verify the application rather than only its individual Python modules.

## Levels used

| Level | Purpose | Tool / location |
|---|---|---|
| Django tests | Validate accounts, posts, comments, forms, management commands, settings, health, email, and permissions | `apps/**/tests/`, pytest |
| Frontend asset tests | Confirm generated CSS exists and source JavaScript is mirrored into generated output | `tests/frontend/`, Node test runner |
| Browser smoke tests | Exercise Hero navigation and autoplay, language selection, custom selects, mobile navigation, and comment replies | `tests/e2e/`, Playwright and Chromium |
| Docker smoke test | Verify the production image starts and serves health, a public page, and static assets | GitHub Actions |

## Run tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py check
pnpm run build
pnpm test
```

For browser smoke tests, install Chromium once and prepare a database containing the seed plus the browser-test reader and comment. The CI workflow shows the exact reproducible setup. A local PostgreSQL or SQLite database can be used; point Playwright at it with `E2E_DATABASE_URL`:

```bash
pnpm exec playwright install chromium
E2E_DATABASE_URL=<prepared-database-url> pnpm run test:e2e
```

In PowerShell, set `E2E_DATABASE_URL` with `$env:E2E_DATABASE_URL = "..."` before running `pnpm run test:e2e`.

## Critical behaviors

- Published-only visibility, structural categories, reserved slugs, search, and pagination.
- Registration races, login, profile changes, password-reset availability, and POST logout.
- Comment creation, one-level replies, withdrawal, editing, and moderation permissions.
- Contact failure feedback, upload validation, health responses, CSP reporting, and production settings checks.
- Generated asset freshness and the browser interactions that depend on those assets.

## Test data and external dependencies

Tests isolate external effects: test settings use in-memory email and media storage. The standard pytest configuration uses in-memory SQLite unless `TEST_DATABASE_URL` is provided. CI provides PostgreSQL 18 through GitHub Actions services to run the Django suite against PostgreSQL as well.

Browser smoke tests do not call real provider APIs. They require prepared local data because Playwright starts Django but does not migrate or seed a database. The CI workflow creates an isolated SQLite database, migrates it, runs `seed_portfolio`, and inserts the minimal reader/comment fixture first.

## Quality gates

Before integrating relevant changes:

- Run `uv sync --locked`, then Ruff, migration, pytest, and Django checks.
- Run `pnpm install --frozen-lockfile`, `pnpm run build`, and `pnpm test` after frontend changes.
- Run Playwright after changing critical browser behavior.
- Build the Docker image and run the health/public/static smoke test before changing deployment behavior.

GitHub Actions performs these gates on pushes and pull requests targeting `main` or `modernize/00-baseline`: Python 3.13 and 3.14, PostgreSQL 18, generated assets, browser smoke coverage, production deployment checks, and the Docker smoke test. Coverage is useful evidence, not a substitute for behavioral assertions.
