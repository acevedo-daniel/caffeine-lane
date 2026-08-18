# Testing

> Test strategy, boundaries, data setup, and release verification gates.

## Strategy

Caffeine Lane combines four complementary test layers to verify domain rules, request lifecycles, frontend asset compilation, responsive browser interactions, and containerized deployment readiness.

## Test Layers

| Layer                    | Purpose                                                                                                                                                                           | Tool / Location                                 |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| **Django & ORM Tests**   | Validate custom user authentication, registration flows, editorial post lifecycle, single-level comment nesting, form validation, management commands, and permission boundaries. | `pytest` / `pytest-django` in `apps/**/tests/`  |
| **Frontend Asset Tests** | Confirm generated CSS existence, JavaScript module mirroring, controller behavior, and asset bundle freshness.                                                                    | Node.js native test runner in `tests/frontend/` |
| **Browser Smoke Tests**  | Validate real browser interactions: Hero carousel autoplay and keyboard controls, language switcher, custom selects, mobile navigation, and comment reply submission.             | Playwright (Chromium) in `tests/e2e/`           |
| **Docker Smoke Test**    | Build production image and verify startup sequence, entrypoint execution, `/healthz/` liveness, static file delivery, and security headers.                                       | Docker in `.github/workflows/ci.yml`            |

## Test Data and Isolation

- **In-Memory Storage:** Test settings (`config.settings.test`) use in-memory email backends and `django.core.files.storage.InMemoryStorage` to eliminate external network calls.
- **Database Isolation:** Unit tests run against an isolated in-memory SQLite database by default, or an ephemeral PostgreSQL 18 service in CI (`TEST_DATABASE_URL`).
- **Browser Test Environment:** Playwright tests utilize an isolated, pre-seeded local database (`E2E_DATABASE_URL`) populated with the standard portfolio fixture and a dedicated test reader account.

## Critical Behaviors Under Test

- **Editorial Access Control:** Unauthenticated users can only view published posts (`is_published=True`).
- **Discussion Invariants:** Comment replies are restricted to a maximum depth of 1 level; replies to replies are rejected at the form and service layers.
- **Search & Pagination:** Full-text queries and category filters persist across page navigation.
- **Contact Resilience:** Simulated provider failures in the contact form return graceful feedback without crashing the application.
- **Security Protections:** Password hashing (Argon2id), CSRF validation, and Content Security Policy enforcement.

## Run Tests

### Python & Backend Tests

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

### Frontend Asset Tests

```bash
pnpm run build
pnpm test
```

### Browser E2E Tests

Install Playwright Chromium:

```bash
pnpm exec playwright install chromium
```

Run browser smoke tests against an isolated prepared database:

```bash
$env:E2E_DATABASE_URL = "sqlite:////tmp/caffeine-lane-e2e.sqlite3"
pnpm run test:e2e
```

## Quality Gates

Before merging changes or releasing to production:

1. **Python Quality:** All `pytest` tests pass, Ruff reports zero lint or formatting issues, and Django checks report zero warnings.
2. **Frontend Quality:** Asset compilation succeeds deterministically and all Node.js asset tests pass.
3. **Browser Smoke:** Critical user flows succeed in Playwright.
4. **Container Readiness:** Docker build succeeds and passes containerized health checks.

## Related Documentation

- [README](../README.md)
- [Development](DEVELOPMENT.md)
- [Architecture](ARCHITECTURE.md)
- [Deployment](DEPLOYMENT.md)
