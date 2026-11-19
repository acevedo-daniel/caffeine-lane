# Caffeine Lane: Testing

> Test strategy, isolation guarantees, local commands, and CI merge gates.

## Strategy

Tests follow this boundary order:

```text
Unit -> Integration -> E2E
```

Each behavior is tested at the lowest reliable boundary. Django and ORM tests
verify application behavior and persistence contracts, Node tests verify the
frontend asset pipeline, and Playwright covers critical user journeys through a
running application.

CI keeps the technical contract explicit through parallel conceptual jobs:

```text
Quality -----\
Tests --------\
E2E -----------> CI Gate
Production ----/
Docker --------/
```

CI Gate is the single stable check required by the GitHub ruleset protecting
`main`. Version-specific runtimes and implementation jobs are not required
directly by the ruleset.

## Test layers

| Layer | Purpose | Tool / location |
| --- | --- | --- |
| Unit | Frontend asset transformations and browser-independent JavaScript behavior | Node test runner in `tests/frontend/` |
| Integration | Django views, models, forms, services, permissions, search, comments, rate limits, and management commands | Pytest + pytest-django in `apps/**/tests/` |
| E2E | Critical user workflows through a running Django application (`tests/e2e/frontend-smoke.spec.mjs`) and text contrast in light and dark themes (`tests/e2e/contrast.spec.mjs`) | Playwright + Chromium in `tests/e2e/` |
| Production | Production settings and generated frontend artifact verification | Django checks and asset build in GitHub Actions |
| Docker | Production image build, bundled assets, health endpoint, and public responses | Docker smoke test in GitHub Actions |

The Python suite measures coverage for `apps` and `config` with pytest-cov.
Coverage is diagnostic; the project does not enforce an arbitrary global
threshold.

## Test data and dependencies

### Python tests

`config.settings.test` uses an in-memory SQLite database locally, an in-memory
email backend, isolated uploaded-media storage, and a fast password hasher.
CI sets `TEST_DATABASE_URL` to a PostgreSQL 18 service so database-specific
behavior is verified against the production database technology.

Tests do not require production databases, APIs, email providers, Cloudinary,
or real credentials.

### Browser tests

Playwright runs Chromium with one worker and retains traces on failure. CI
creates a dedicated SQLite database, applies migrations, seeds deterministic
editorial data, creates the E2E user/comment fixture, and waits for
`/healthz/` before executing browser tests.

## Run tests

Install locked dependencies first:

```bash
uv sync --locked
pnpm install --frozen-lockfile
```

Run the same fast validation used by the CI Quality and Tests jobs:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --settings=config.settings.test --check --dry-run
uv run pytest
pnpm run build
pnpm test
```

On Windows, `.\scripts\check.ps1` runs this sequence, and `.\scripts\verify.ps1`
reproduces CI Gate locally: the same checks against PostgreSQL 18, the
Playwright suite on an isolated database, production settings checks, and a
Docker image build.

## End-to-end verification

Install the browser binary once:

```bash
pnpm exec playwright install chromium
```

Run the browser smoke suite:

```bash
pnpm run build
pnpm run test:e2e
```

The Playwright configuration starts Django automatically. Because the suite
creates users and comments, it never uses `DATABASE_URL`: it uses
`E2E_DATABASE_URL`, or the isolated SQLite file `tmp/e2e.sqlite3` when that
variable is unset. `scripts/prepare-e2e.mjs` migrates that database, seeds the
editorial dataset when it is missing, and creates the E2E accounts. Any
`E2E_DATABASE_URL` that is not SQLite or a local PostgreSQL database is refused.

## Reliability

- **Readiness:** Playwright's `webServer` in `playwright.config.mjs` waits for
  `/healthz/` to answer before any test starts.
- **Budgets:** each Playwright test has 30 seconds and each `expect` 8 seconds.
- **Retries:** CI retries a failed E2E test once; local runs never retry.
  pytest and Node tests never retry.
- **Flaky reporting:** CI reads `playwright-report/results.json`, emits a
  warning for every test that passed only on retry, and lists it in the job
  summary.
- **Waiting:** tests wait for visible state or network responses, never fixed
  sleeps, and do not override the timeout budgets.

## CI and quality gates

`.github/workflows/ci.yml` runs on pull requests targeting `main` and on manual
dispatch; it does not run on pushes to `main`. It uses locked dependency
installation, minimum read-only permissions, explicit timeouts, and cancels
obsolete pull request runs for the same ref.

The jobs are:

- Quality: Ruff, Django system checks, and migration drift checks.
- Tests: Python tests against PostgreSQL 18 and frontend unit tests.
- E2E: isolated database setup, asset build, and Playwright browser smoke and
  contrast tests.
- Production: frontend production build, the `pyproject.toml` Vercel build
  hook, and Django production security checks with CSP enforced.
- Docker: production image build, asset integrity, startup, health endpoint,
  static assets, and public response smoke tests.
- CI Gate: fails unless every required job completes successfully.

The repository ruleset on `main` requires exactly CI Gate and requires the
branch to be up to date with `main` before merging. It also requires pull
requests with resolved conversations, linear history, and squash merging, and
blocks deletion and force pushes.

Release validation before production is described in
[Deployment › Validation](DEPLOYMENT.md#validation).

## Related documentation

- [Development Workflow](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
