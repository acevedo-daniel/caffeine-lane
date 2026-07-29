# Caffeine Lane

> Un blog editorial de motos café racer modernizado como proyecto de portfolio.

**Estado del proyecto:** desarrollo activo. La modernización v2 ya incorpora
configuración por entorno, contenido editorial, comentarios moderados, CI e
imagen Docker; el despliegue público sigue pendiente de validar staging.

## Overview

The Caffeine Lane es una aplicación Django para publicar builds, guías y reseñas
de motocicletas café racer. Permite explorar contenido publicado, buscar por
texto y categoría, comentar con moderación, y gestionar el blog desde Django
Admin.

El proyecto partió de una aplicación académica y se está convirtiendo en una
pieza de portfolio mantenible: separa entornos, usa PostgreSQL, compila sus
assets, valida media, protege los flujos de autenticación y correo, y deja una
base repetible para despliegue con Docker.

## Project Context

| Field               | Details                                                                    |
| ------------------- | -------------------------------------------------------------------------- |
| **Type**            | Personal portfolio project; modernization of an academic project           |
| **Purpose**         | Demonstrate an end-to-end Django modernization and editorial domain design |
| **Role**            | Solo developer                                                             |
| **Started**         | 2025-07                                                                    |
| **Current version** | v2 modernization in progress                                               |

## Key Features

- **Editorial posts:** published/draft workflow, stable slugs, categories,
  featured images, alt text, related posts, pagination and PostgreSQL search.
- **Accounts:** custom user model, email login, registration, profile, avatar,
  password change and password reset.
- **Comments and moderation:** one-level replies, edit/withdraw actions, spam
  honeypot, duplicate protection and moderator hiding without deleting context.
- **Editorial admin:** filters, search, autocompletes, thumbnails and actions
  that publish, unpublish and moderate through the domain services.
- **Production foundations:** CSP report-only mode, secure settings, structured
  logging to stdout, HTML/text emails, validated uploads and Cloudinary media.

## Tech Stack

| Area                   | Technology                                                                  |
| ---------------------- | --------------------------------------------------------------------------- |
| **Language**           | Python 3.13–3.14                                                            |
| **Framework**          | Django 6.0                                                                  |
| **Database**           | PostgreSQL 18 locally; PostgreSQL-compatible managed database in deployment |
| **Package management** | uv and `uv.lock`                                                            |
| **Frontend assets**    | Tailwind CSS 4, pnpm and compiled static files                              |
| **Testing**            | pytest, pytest-django, coverage and factory-boy                             |
| **Quality**            | Ruff and pre-commit                                                         |
| **Infrastructure**     | Docker multi-stage image, Gunicorn, WhiteNoise and Cloudinary               |
| **CI**                 | GitHub Actions on Python 3.13 and 3.14                                      |

## Scope

### Included

- Public editorial site, search, categories and published-post visibility.
- User accounts, email flows, comments and moderation.
- Local Docker Compose database, CI and deployment runbooks.

### Not Included

- A public production deployment or permanent staging environment.
- Real user-data migration from the original academic database.
- Newsletter, payments, social login or a mobile application.

## Getting Started

### Prerequisites

- Python 3.13 or 3.14.
- [uv](https://docs.astral.sh/uv/).
- Node.js 22 and pnpm 10.18.3.
- Docker Desktop with Docker Compose for local PostgreSQL.
- Git.

### Installation

```bash
git clone https://github.com/acevedo-daniel/caffeine-lane.git
cd caffeine-lane
```

Create a private local environment file:

```bash
cp .env.example .env
```

In PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Start PostgreSQL, install Python dependencies and compile the frontend assets:

```bash
docker compose up -d db
uv sync
pnpm install --frozen-lockfile
pnpm run build
```

### Environment Variables

`.env.example` contains safe development values. Do not commit `.env` or real
credentials.

| Variable                                               | Required locally | Description                                              |
| ------------------------------------------------------ | :--------------: | -------------------------------------------------------- |
| `DJANGO_SETTINGS_MODULE`                               |       Yes        | `config.settings.local` for local work                   |
| `SECRET_KEY`                                           |       Yes        | Local Django secret; production must use a unique secret |
| `DATABASE_URL`                                         |       Yes        | PostgreSQL connection string                             |
| `ALLOWED_HOSTS`                                        |       Yes        | Comma-separated allowed hosts                            |
| `CSRF_TRUSTED_ORIGINS`                                 |       Yes        | Trusted form origins including scheme                    |
| `CLOUDINARY_URL`                                       |        No        | Required only by production media storage                |
| `DEFAULT_FROM_EMAIL`                                   |       Yes        | Sender address for application emails                    |
| `CONTACT_RECIPIENT_EMAIL`                              |       Yes        | Recipient for contact messages                           |
| `RESEND_API_KEY`                                        |        No        | Required by the Resend email backend in production       |
| `CSP_ENFORCE`                                          |        No        | Enables enforcing CSP after report-only validation       |

### Database Setup

Apply migrations:

```bash
uv run python manage.py migrate
```

Optional: create idempotent, non-privileged demo content:

```bash
uv run python manage.py seed_demo
```

### Run Locally

```bash
uv run python manage.py runserver
```

The application is available at <http://localhost:8000>.

## Usage

1. Visit `/home/` to browse published posts, categories and search results.
2. Register with an email address, then update the public profile and avatar.
3. Sign in with a staff account to use `/admin/` for editorial publication and
   comment moderation.

The liveness endpoint is available at:

```text
GET /healthz/ → {"status": "ok"}
```

## Available Scripts

| Command                                                       | Description                                      |
| ------------------------------------------------------------- | ------------------------------------------------ |
| `docker compose up -d db`                                     | Starts local PostgreSQL 18.                      |
| `uv sync`                                                     | Creates or updates the local Python environment. |
| `pnpm run build`                                              | Compiles Tailwind CSS and JavaScript assets.     |
| `uv run python manage.py runserver`                           | Starts Django locally.                           |
| `uv run python manage.py migrate`                             | Applies database migrations.                     |
| `uv run pytest`                                               | Runs the automated test suite with coverage.     |
| `uv run ruff check .`                                         | Runs lint checks.                                |
| `uv run ruff format --check .`                                | Verifies formatting.                             |
| `powershell -ExecutionPolicy Bypass -File scripts/check.ps1`  | Runs the standard local quality checks.          |
| `powershell -ExecutionPolicy Bypass -File scripts/format.ps1` | Applies Ruff lint fixes and formatting.          |

## Project Structure

```text
caffeine-lane/
├── apps/
│   ├── accounts/          # Custom user, authentication and profile flows
│   ├── core/              # Landing, contact, health and shared utilities
│   └── posts/             # Editorial domain, search, comments and admin
├── config/settings/       # Base, local, test and production settings
├── docker/                # Runtime entrypoint
├── docs/                  # Audit, import, database and deployment runbooks
├── scripts/               # Asset build and local quality scripts
├── static/                # Design assets, Tailwind source and compiled output
├── templates/             # Shared layouts and components
├── compose.yaml           # Local PostgreSQL service
├── Dockerfile             # Production multi-stage image
├── pyproject.toml         # Python dependencies and tool configuration
├── uv.lock                # Locked Python dependencies
├── package.json           # Frontend asset scripts
└── README.md
```

## Architecture

Django applications are split by responsibility: `accounts` owns identity and
profiles, `posts` owns editorial content and comments, and `core` owns shared
site pages and operational endpoints. Settings are separated by local, test and
production environments.

PostgreSQL is used for relational data and full-text search. Static files are
compiled with Tailwind and served with WhiteNoise in production. Uploaded media
uses the local filesystem in development and Cloudinary in production. The
Docker entrypoint runs `collectstatic`; migrations are an explicit release task.

## Testing

Run all tests:

```bash
uv run pytest
```

The current suite covers authentication, password reset email, contact email,
uploads, editorial rules, search performance, comments, moderation, admin
actions, CSP and the health endpoint. It runs with in-memory services by default
and can target PostgreSQL by setting `TEST_DATABASE_URL`.

```bash
TEST_DATABASE_URL=postgresql://caffeine-lane:caffeine-lane@localhost:5432/caffeine-lane uv run pytest
```

On PowerShell:

```powershell
$env:TEST_DATABASE_URL = "postgresql://caffeine-lane:caffeine-lane@localhost:5432/caffeine-lane"
uv run pytest
Remove-Item Env:TEST_DATABASE_URL
```

## Deployment

The project is not publicly deployed yet. The Docker image compiles assets,
installs runtime-only Python dependencies, runs as a non-root user and starts
Gunicorn. It does not load fixtures, create superusers or run migrations.

```bash
docker build -t caffeine-lane .
docker run --rm -p 8000:8000 --env-file .env caffeine-lane
```

Before a release, run migrations once using the same image and production
environment. See the deployment runbook for the complete process.

## Known Limitations

- A hosting provider and permanent staging environment have not been selected.
- CSP defaults to report-only until violations are observed and reviewed.
- The demo content is intentionally small; selected legacy content must be
  reviewed and imported separately.

## Roadmap

- [x] Modernize to Django 6, uv, pytest, Ruff and pre-commit.
- [x] Add PostgreSQL, editorial domain, comments, Tailwind, security and CI.
- [x] Add a Docker image, deployment runbook and health endpoint.
- [ ] Select and provision a portfolio hosting environment.
- [ ] Validate staging, CSP reports and a rollback before public release.

## Documentation

- [Initial audit](./docs/audit-initial.md)
- [Legacy reproduction](./docs/legacy-reproduction.md)
- [Local PostgreSQL](./docs/local-postgres.md)
- [Content import](./docs/content-import.md)
- [Docker deployment](./docs/deployment.md)
- [Staging rollout](./docs/staging-rollout.md)
- [Render, Neon, Cloudinary and Resend](./docs/render-neon-cloudinary-resend.md)

## License

No license file has been added yet. Reuse terms have not been declared.

## Author

**Daniel Acevedo**

- GitHub: [@acevedo-daniel](https://github.com/acevedo-daniel)
- Repository: [caffeine-lane](https://github.com/acevedo-daniel/caffeine-lane)
