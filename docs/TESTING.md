# Caffeine Lane: Testing

> Test strategy, isolation guarantees, local commands, and CI merge gates.

## Strategy

Caffeine Lane follows the playbook boundary order:

~~~~text
Unit -> Integration -> E2E
~~~~

Each behavior is tested at the lowest reliable boundary. Django and ORM tests
verify application behavior and persistence contracts, Node tests verify the
frontend asset pipeline, and Playwright covers critical user journeys through a
running application.

CI keeps the technical contract explicit through parallel conceptual jobs:

~~~~text
Quality -----\
Tests --------\
E2E -----------> CI Gate
Production ----/
Docker --------/
~~~~

CI Gate is the single stable check intended for the GitHub Ruleset protecting
main. Version-specific runtimes and implementation jobs must not be required
directly by the Ruleset.

## Test layers

| Layer | Purpose | Tool / location |
| --- | --- | --- |
| Unit | Frontend asset transformations and browser-independent JavaScript behavior | Node test runner in tests/frontend/ |
| Integration | Django views, models, forms, services, permissions, search, comments, and management commands | Pytest + pytest-django in apps/**/tests/ |
| E2E | Critical user workflows through a running Django application | Playwright + Chromium in tests/e2e/ |
| Production | Production settings and generated frontend artifact verification | Django checks and asset build in GitHub Actions |
| Docker | Production image build, bundled assets, health endpoint, and public responses | Docker smoke test in GitHub Actions |

The Python suite measures coverage for apps and config with pytest-cov.
Coverage is diagnostic; the project does not enforce an arbitrary global
threshold.

## Test data and dependencies

### Python tests

config.settings.test uses an in-memory SQLite database locally, an in-memory
email backend, isolated uploaded-media storage, and a fast password hasher.
CI sets TEST_DATABASE_URL to a PostgreSQL 18 service so database-specific
behavior is verified against the production database technology.

Tests do not require production databases, APIs, email providers, Cloudinary,
or real credentials.

### Browser tests

Playwright runs Chromium with one worker and retains traces on failure. CI
creates a dedicated SQLite database, applies migrations, seeds deterministic
editorial data, creates the E2E user/comment fixture, and waits for
/healthz/ before executing browser tests.

## Run tests locally

Install locked dependencies first:

~~~~bash
uv sync --locked
pnpm install --frozen-lockfile
~~~~

Run the same fast validation used by the CI Quality and Tests jobs:

~~~~bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --settings=config.settings.test --check --dry-run
uv run pytest
pnpm run build
pnpm test
~~~~

On Windows, pwsh ./scripts/check.ps1 runs this local validation sequence.

## End-to-end verification

Install the browser binary once:

~~~~bash
pnpm exec playwright install chromium
~~~~

Run the browser smoke suite:

~~~~bash
pnpm run build
pnpm run test:e2e
~~~~

The Playwright configuration starts Django automatically and uses the active
local database unless E2E_DATABASE_URL is provided.

## CI and quality gates

.github/workflows/ci.yml runs for pull requests targeting main and pushes
to main. It uses locked dependency installation, minimum read-only
permissions, explicit timeouts, and cancels obsolete runs for the same ref.

The jobs are:

- Quality: Ruff, Django system checks, and migration drift checks.
- Tests: Python tests against PostgreSQL 18 and frontend unit tests.
- E2E: isolated database setup, asset build, and Playwright browser smoke tests.
- Production: frontend production build, Vercel build contract, and Django
  production security checks.
- Docker: production image build, asset integrity, startup, health endpoint,
  static assets, and public response smoke tests.
- CI Gate: fails unless every required job completes successfully.

The repository Ruleset should require exactly CI Gate, with pull requests,
resolved conversations, linear history, squash merging, deletion protection,
and force-push protection enabled. The Ruleset configuration is applied in
GitHub repository settings; the workflow provides the required check.

## Pre-release verification

For a fuller local release check, run:

~~~~bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --settings=config.settings.test --check --dry-run
uv run pytest
pnpm install --frozen-lockfile
pnpm run build
pnpm test
pnpm run test:e2e
docker build -t caffeine-lane-local-check .
~~~~

## Related documentation

- [Development Workflow](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
- CI and Testing Standard (maintained in the engineering playbook)
- GitHub Ruleset Standard (maintained in the engineering playbook)
