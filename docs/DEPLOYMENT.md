# Caffeine Lane — Deployment

> Vercel runtime, Neon database releases, environment boundaries, and production verification.

## Production topology

```text
Browser
  -> Vercel CDN (static assets)
  -> Vercel Django function (WSGI)
      -> Neon PostgreSQL (pooled connection)
      -> Cloudinary media storage
      -> Resend through Anymail
```

| Component | Platform | Responsibility |
| --- | --- | --- |
| Web runtime | Vercel | Serve the Django application through the Python runtime. |
| Static assets | Vercel CDN | Serve the compiled CSS, JavaScript, fonts, and local static assets. |
| Database | Neon | Persist application data in PostgreSQL. |
| Media storage | Cloudinary | Persist user-uploaded images and avatars. |
| Email service | Resend | Deliver transactional email through Anymail. |

Vercel detects Django from `manage.py` and the WSGI configuration. The build hook in `pyproject.toml` compiles frontend assets with pnpm. No `vercel.json`, Docker image, or `/api` redirect is needed for this application.

## Release flow

```text
Pull request
-> GitHub Actions CI
-> Vercel preview (no production migrations)
-> Review preview
-> Merge to main
-> Explicit Neon release command (direct connection)
-> Vercel production deployment
-> Health and user-flow verification
```

Schema changes are deliberately outside the Vercel build. A preview must never alter the production Neon database.

## Vercel configuration

Set these variables in the Vercel project for the appropriate environment:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | Unique Django cryptographic secret. |
| `DATABASE_URL` | Neon **pooled** connection used by the web runtime. |
| `ALLOWED_HOSTS` | Production and preview hostnames, comma-separated. |
| `CSRF_TRUSTED_ORIGINS` | HTTPS production and preview origins, comma-separated. |
| `CLOUDINARY_URL` | Cloudinary storage credentials. |
| `RESEND_API_KEY` | Resend API credential. |
| `DEFAULT_FROM_EMAIL` | Verified sender address. |
| `CONTACT_RECIPIENT_EMAIL` | Recipient for contact submissions. |
| `USE_X_FORWARDED_PROTO` | `true` behind Vercel's HTTPS proxy. |
| `CSP_ENFORCE` | Start with `false`; enable after CSP reports are reviewed. |
| `SECURE_HSTS_SECONDS` | Positive duration after the production domain is stable. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Enable only when every subdomain is HTTPS-ready. |
| `SECURE_HSTS_PRELOAD` | Enable only after an intentional preload decision. |

Do **not** add `DIRECT_DATABASE_URL` to the Vercel runtime. It is only used by a controlled release command from a trusted terminal or release runner.

Preview deployments need an isolated Neon branch/database and their own `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`. Until that branch integration is configured, keep previews read-only or use no database-backed preview paths.

## Database release

Create migration files locally and commit them with their model changes:

```bash
uv run python manage.py makemigrations
uv run python manage.py makemigrations --check --dry-run
```

Run the production release from a trusted environment with both Neon URLs available. The script switches Django to the direct connection only while applying schema changes:

```bash
# macOS / Linux
./scripts/release.sh

# Windows PowerShell
./scripts/release.ps1
```

Both scripts perform:

```text
check_fresh_baseline
-> migrate --noinput
-> verify_editorial_baseline
```

`migrate` is idempotent: a release with no pending migrations does not alter the schema. Never run `makemigrations` against Neon.

## Editorial dataset

The editorial dataset is intentionally separate from schema release:

```bash
uv run python manage.py seed_editorial
```

It is idempotent, but it writes content and can upload media. Run it only after editorial review and never as part of a normal Vercel deployment. Docker's `SEED_EDITORIAL_ON_START` remains disabled by default for exceptional self-hosted use.

## Validation

Before production:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py check --deploy
uv run pytest
pnpm run build
pnpm test
pnpm run test:e2e
```

After deployment, verify:

- `/healthz/` returns HTTP 200.
- Landing, home, categories, search, authentication, and contact flow work.
- CSS and JavaScript are served from Vercel's CDN.
- Cloudinary media renders correctly.
- No errors appear in Vercel deployment and runtime logs.

## Docker boundary

The Docker image remains a portable production-like artifact and a CI smoke-test target. Its startup defaults do not run migrations or seed editorial data. Vercel does not execute `docker/entrypoint.sh`.

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
