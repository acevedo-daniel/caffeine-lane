# Caffeine Lane

<p align="center">
  A portfolio Django application for publishing cafe racer builds, guides, and reviews.
</p>

<p align="center">
  <a href="https://caffeinelane.onrender.com">Live Demo</a>
  ·
  <a href="./docs/deployment.md">Deployment guide</a>
  ·
  <a href="https://github.com/acevedo-daniel/caffeine-lane/issues">Report an Issue</a>
</p>

> [!NOTE]
> **Project status: Active development.** The Render production service is provisioned and its deployment is being validated.

## Overview

The Caffeine Lane is an editorial application for cafe racer enthusiasts. It
provides a public catalogue of builds, guides, and reviews, with search and
categories to make content easy to explore.

The project modernizes an academic Django application into a maintainable
portfolio piece. It separates local, test, and production settings; uses
PostgreSQL for the editorial domain; and includes authentication, moderated
comments, secure uploads, transactional email, and a repeatable Docker-based
deployment.

## Project Context

| Field | Details |
| --- | --- |
| **Type** | Personal portfolio; modernization of an academic project |
| **Purpose** | Demonstrate an end-to-end Django modernization and editorial domain design |
| **Role** | Solo developer |
| **Started** | 2025-07 |
| **Current version** | v2 modernization in progress |

## Key Features

- **Editorial publishing:** drafts, published posts, stable slugs, categories,
  featured images, alt text, related posts, pagination, and PostgreSQL search.
- **Accounts:** custom users, email login, registration, public profiles,
  avatars, password changes, and password reset flows.
- **Comments and moderation:** one-level replies, edit and withdraw actions,
  honeypot spam protection, duplicate prevention, and moderator controls.
- **Editorial administration:** Django Admin filters, search, thumbnails, and
  actions for publication and moderation.
- **Production foundations:** Docker, Gunicorn, WhiteNoise, Cloudinary media,
  Resend email through Anymail, CSP report-only mode, and structured logs.

## Tech Stack

| Area | Technology |
| --- | --- |
| **Language** | Python 3.13-3.14 |
| **Framework** | Django 6.0 |
| **Database** | PostgreSQL 18 locally; Neon PostgreSQL in production |
| **Package management** | uv and `uv.lock` |
| **Frontend assets** | Tailwind CSS 4, Node.js 22, and pnpm |
| **Testing** | pytest, pytest-django, coverage, and factory-boy |
| **Infrastructure** | Docker, Render, Gunicorn, WhiteNoise, Cloudinary, Resend, and Neon |
| **CI** | GitHub Actions on Python 3.13 and 3.14 |

## Scope

### Included

- Public editorial content, search, categories, and published-post visibility.
- Accounts, password flows, comments, and editorial moderation.
- Docker deployment, PostgreSQL migrations, Cloudinary media, and Resend email.

### Not Included

- Migration of real users or unreviewed legacy data.
- Newsletters, payments, social login, or a mobile application.
- A permanent staging environment.

## Getting Started

### Prerequisites

Before installing the project, make sure you have:

- Python 3.13 or 3.14.
- [uv](https://docs.astral.sh/uv/).
- Node.js 22 and pnpm 10.18.3.
- Docker Desktop with Docker Compose for local PostgreSQL.
- Git.

### Installation

Clone the repository:

```bash
git clone https://github.com/acevedo-daniel/caffeine-lane.git
cd caffeine-lane
```

Create a private environment file, start PostgreSQL, and install dependencies:

```bash
cp .env.example .env
docker compose up -d db
uv sync
pnpm install --frozen-lockfile
pnpm run build
```

In PowerShell, create the environment file with:

```powershell
Copy-Item .env.example .env
```

### Environment Variables

`.env.example` contains safe local values. Do not commit `.env` files, API keys,
database URLs, or provider credentials.

| Variable | Required | Description | Safe example |
| --- | :---: | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Yes | Active settings module | `config.settings.local` |
| `SECRET_KEY` | Yes | Django signing key | local value in `.env.example` |
| `DATABASE_URL` | Yes | Local PostgreSQL or Neon pooled connection URL | `postgresql://...` |
| `DIRECT_DATABASE_URL` | Yes | Direct Neon URL used by startup migrations | `postgresql://...` |
| `ALLOWED_HOSTS` | Yes | Comma-separated allowed hosts | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Yes | Trusted form origins with scheme | `http://localhost:8000` |
| `CLOUDINARY_URL` | Production | Cloudinary media-storage credential | provider-issued secret |
| `RESEND_API_KEY` | Production | Resend API key for Anymail | provider-issued secret |
| `DEFAULT_FROM_EMAIL` | Yes | Sender used by application email | `noreply@example.com` |
| `CONTACT_RECIPIENT_EMAIL` | Yes | Recipient for contact messages | `owner@example.com` |
| `USE_X_FORWARDED_PROTO` | Production | Trust the Render HTTPS proxy header | `true` |
| `CSP_ENFORCE` | No | Enable CSP enforcement after report validation | `false` |

> [!IMPORTANT]
> Keep production secrets only in Render. Do not add them to Git, the README,
> `.env.example`, the Dockerfile, or a Render configuration file.

### Database Setup

Apply migrations:

```bash
uv run python manage.py check_fresh_baseline
uv run python manage.py migrate
```

> [!WARNING]
> This branch is a **fresh baseline** and is not compatible with a database
> created from `main`. The original `accounts.0001_initial` used Django's
> `auth.User` plus `accounts.Profile`; this branch uses a custom
> `accounts.User` under the same migration identifier. Do not reuse an old
> SQLite database or PostgreSQL volume. Create a new database, run the command
> above, and then apply all migrations from scratch. The check aborts if it
> detects the legacy `accounts_profile` table; it never deletes data.

Create the idempotent public portfolio dataset after the first migration. It
creates a non-privileged author with an unusable password, three structural
categories, ten published posts, and uploads the bundled WebP cover images to
the active media storage (Cloudinary in production):

```bash
uv run python manage.py seed_portfolio
```

Run it manually once in production; it is safe to repeat but is never part of
the image build or web-process startup.

### Run Locally

Start the development server:

```bash
uv run python manage.py runserver
```

The application is available at <http://localhost:8000>.

## Usage

1. Visit `/home/` to browse published content, categories, and search results.
2. Register or sign in to update a profile and participate in comments.
3. Use `/admin/` with a staff account to publish content and moderate comments.

The liveness endpoint is:

```text
GET /healthz/ -> {"status": "ok"}
```

## Available Scripts

| Command | Description |
| --- | --- |
| `docker compose up -d db` | Starts local PostgreSQL. |
| `uv sync` | Installs the locked Python dependencies. |
| `pnpm run build` | Compiles Tailwind CSS and JavaScript assets. |
| `uv run python manage.py runserver` | Starts the local development server. |
| `uv run python manage.py migrate` | Applies database migrations. |
| `uv run pytest` | Runs the automated test suite with coverage. |
| `uv run ruff check .` | Checks linting rules. |
| `uv run ruff format --check .` | Verifies formatting. |
| `./scripts/release.sh` | Uses Neon direct connection for migrations and verifies the structural taxonomy. |
| `uv run python manage.py seed_portfolio` | Manually creates or updates the public portfolio dataset. |

## Project Structure

<details>
<summary><strong>View directory structure</strong></summary>

```text
caffeine-lane/
├── apps/                 # Accounts, core pages, posts, and tests
├── config/settings/       # Base, local, test, and production settings
├── docker/                # Container runtime entrypoint
├── docs/                  # Audit, deployment, and operational documentation
├── scripts/               # Explicit release helper scripts
├── static/                # Source and compiled frontend assets
├── templates/             # Shared and application templates
├── .env.example           # Safe local environment reference
├── compose.yaml           # Local PostgreSQL service
├── Dockerfile             # Multi-stage production image
├── pyproject.toml         # Python dependencies and tooling
├── uv.lock                # Locked Python dependencies
└── README.md
```

</details>

## Architecture

`accounts` owns identity and profiles, `posts` owns editorial content and
comments, and `core` owns shared pages, contact email, and health endpoints.
Settings are isolated by environment.

In production, Render runs the Docker image. Before Gunicorn starts on Render's
assigned `PORT`, the container verifies the fresh baseline, applies migrations
with `DIRECT_DATABASE_URL`, returns to the pooled `DATABASE_URL`, seeds the
idempotent public portfolio, and collects static files.
WhiteNoise serves static files, Cloudinary stores uploaded media, Neon stores
relational data, and Anymail sends email through Resend.

## Testing

Run the complete test suite:

```bash
uv run pytest
```

Run the standard quality checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
```

The suite covers authentication, password resets, contact email, uploads,
editorial rules, search, comments, moderation, admin actions, CSP, and the
health endpoint. It uses in-memory services by default and can target local
PostgreSQL with `TEST_DATABASE_URL`.

La revisión visual reproducible de las páginas, estados y viewports está en
[docs/ui-visual-checklist.md](./docs/ui-visual-checklist.md).

## Deployment

| Environment | URL | Provider |
| --- | --- | --- |
| **Production (validation in progress)** | <https://caffeinelane.onrender.com> | Render |

Render uses the root `Dockerfile` with these settings:

- **Docker Build Context Directory:** `.`
- **Dockerfile Path:** `./Dockerfile`
- **Docker Command:** leave empty
- **Health Check Path:** `/healthz/`

Required production variables are `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`,
`DATABASE_URL`, `ALLOWED_HOSTS`,
`CSRF_TRUSTED_ORIGINS`, `CLOUDINARY_URL`, `RESEND_API_KEY`,
`DEFAULT_FROM_EMAIL`, `CONTACT_RECIPIENT_EMAIL`, and
`USE_X_FORWARDED_PROTO=true`. Configure the HSTS and CSP variables according to
the environment-variable table above.

The Docker entrypoint is the only web-process startup path. It never loads
fixtures or creates superusers. Because Render Free does not offer an execution
shell, it runs the idempotent migrations and `seed_portfolio` before each web
process start; migrations use `DIRECT_DATABASE_URL` and the application returns
to the pooled `DATABASE_URL`. The service therefore requires both URLs.

> [!NOTE]
> `onboarding@resend.dev` can only send to the email address associated with the
> Resend account. Verify a domain in Resend before sending password-reset email
> to arbitrary visitors.

## Known Limitations

- Production deployment validation is still in progress.
- CSP stays in report-only mode until its reports are reviewed.
- Demo content is intentionally small; legacy content must be reviewed before
  importing it.
- Resend's onboarding sender is limited until a custom domain is verified.

## Roadmap

- [x] Modernize the original application with Django 6, uv, pytest, and Ruff.
- [x] Add editorial content, accounts, comments, security settings, and CI.
- [x] Add Docker, Cloudinary media, Neon configuration, Resend email, and a
  Render health check.
- [ ] Complete production smoke testing and review deployment logs.
- [ ] Validate CSP reports and establish a rollback procedure.

See the [open issues](https://github.com/acevedo-daniel/caffeine-lane/issues)
for planned improvements and known problems.

## Documentation

- [Initial audit](./docs/audit-initial.md)
- [Legacy reproduction](./docs/legacy-reproduction.md)
- [Local PostgreSQL](./docs/local-postgres.md)
- [Content import](./docs/content-import.md)
- [Docker deployment](./docs/deployment.md)
- [Staging rollout](./docs/staging-rollout.md)

## License

No license has been declared. Reuse terms have not been published.

## Author

**Daniel Acevedo**

- GitHub: [@acevedo-daniel](https://github.com/acevedo-daniel)
- Repository: [caffeine-lane](https://github.com/acevedo-daniel/caffeine-lane)
