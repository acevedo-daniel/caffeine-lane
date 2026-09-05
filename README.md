# Caffeine Lane

[![CI](https://github.com/acevedo-daniel/caffeine-lane/actions/workflows/ci.yml/badge.svg)](https://github.com/acevedo-daniel/caffeine-lane/actions/workflows/ci.yml)

> A Django editorial application for cafe racer builds, guides, and reviews.

Caffeine Lane is a publishing and community application for motorcycle builders and enthusiasts. It combines editorial content, search, reader accounts and profiles, moderated discussions, media uploads, and a bilingual interface. It is intentionally not an e-commerce marketplace.

**[Open Live Application](https://caffeinelane.onrender.com)**

## Screenshots

### Public and editorial experience

| Entry experience | Article detail |
| --- | --- |
| ![Caffeine Lane entry experience with editorial hero](docs/screenshots/public-landing.png) | ![Caffeine Lane article detail with long-form editorial content](docs/screenshots/post-detail.png) |

### Editorial home

![Caffeine Lane editorial home with featured motorcycle content](docs/screenshots/public-home.png)

### Discovery and participation

| Search and filtering | Discussion |
| --- | --- |
| ![Caffeine Lane search results with editorial discovery controls](docs/screenshots/search-results.png) | ![Caffeine Lane article discussion with reader comments and replies](docs/screenshots/discussion-thread.png) |

## Key capabilities

- **Editorial publishing:** Create and manage draft or published posts across the structural `builds`, `guides`, and `reviews` categories, with validated image uploads.
- **Content discovery:** Browse categories, search published content, sort and paginate results, and surface related posts.
- **Accounts and profiles:** Authenticate with email-based accounts and maintain reader profile information and avatars.
- **Discussion and moderation:** Comment, reply one level deep, edit or withdraw personal comments, and support permission-based moderation.
- **Localization:** Serve the interface in English or Spanish through Django internationalization.

## Engineering highlights

- **Email-based Django identity.** A custom `accounts.User` model makes email the authentication identifier while retaining Django's authentication and permission system; production password hashing prioritizes Argon2.
- **PostgreSQL-aware search.** Published content uses weighted `SearchVector` and `SearchRank` queries on PostgreSQL, with a simpler text-search fallback when another database backend is used.
- **Discussion rules are enforced before persistence.** Comment creation runs model validation through a service boundary, keeping replies to one level and preserving explicit visible, withdrawn, and moderator-hidden states.
- **Runtime and migration database paths are separated.** Production traffic can use Neon's pooled connection while the container temporarily switches to a direct connection for schema migrations.
- **Verification crosses application and delivery boundaries.** CI tests Python 3.14 against PostgreSQL 18, validates generated frontend assets, runs Playwright browser smoke tests, checks production settings, and smoke-tests the production Docker image.

## Architecture

```text
Browser -> Render container (Gunicorn -> Django)
                              -> Neon PostgreSQL
                              -> Cloudinary media storage
                              -> Resend email

         WhiteNoise serves collected static assets from the Django runtime
```

Django owns routing, authentication, validation, editorial and discussion behavior, internationalization, and server-rendered templates. PostgreSQL persists application data, Cloudinary stores media, Resend delivers transactional emails, and Render runs the containerized Gunicorn service.

## Technology stack

- **Backend:** Python 3.14, Django 6, PostgreSQL, and Gunicorn.
- **Frontend:** Django Templates, Tailwind CSS 4, and JavaScript.
- **Services:** Neon, Cloudinary, Resend through Anymail, WhiteNoise, and Render.
- **Tooling:** uv, pnpm, Pytest, Playwright, Ruff, Docker, and GitHub Actions.

## Repository structure

| Path | Responsibility |
| --- | --- |
| `apps/accounts` | Custom user model, authentication, registration, profiles, and password flows. |
| `apps/core` | Landing/home surfaces, contact flow, image validation, and health endpoints. |
| `apps/posts` | Editorial content, taxonomy, search, comments, moderation, and publishing behavior. |
| `config/settings` | Base, local, test, and production Django settings. |
| `docker/` | Production container startup and migration orchestration. |
| `static/` | Authored frontend source and generated distribution assets. |
| `templates/` | Shared server-rendered layouts and page templates. |
| `tests/` | Frontend asset tests and Playwright browser tests. |

## Local development

Prerequisites: Python 3.14+, uv, Node.js 22, pnpm 10, and Docker Compose.

```bash
# Setup environment and dependencies
cp .env.example .env
docker compose up -d db
uv sync --locked
pnpm install --frozen-lockfile
pnpm run build

# Initialize and seed database
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
uv run python manage.py seed_portfolio
```

On Windows PowerShell, use `Copy-Item .env.example .env`.

Run the frontend asset watcher in one terminal:

```bash
pnpm run dev
```

Run Django in another terminal:

```bash
uv run python manage.py runserver
```

Open `http://localhost:8000`.

## Quality

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest
pnpm run build
pnpm test
pnpm run test:e2e
```

CI runs the Python suite against PostgreSQL 18 on Python 3.14, validates production settings, builds and tests frontend assets, runs Playwright browser smoke tests, and smoke-tests the production Docker image.

## Documentation

- [Project](docs/PROJECT.md) — Product domain, actors, scope, and durable business rules.
- [Architecture](docs/ARCHITECTURE.md) — System topology, component boundaries, and invariants.
- [Development](docs/DEVELOPMENT.md) — Local setup, developer workflow, and database lifecycle.
- [Testing](docs/TESTING.md) — Testing strategy, test layers, and quality gates.
- [Deployment](docs/DEPLOYMENT.md) — Hosting topology, Docker delivery, and release pipeline.
