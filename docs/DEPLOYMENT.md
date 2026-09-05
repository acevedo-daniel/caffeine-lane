# Caffeine Lane — Deployment

> Production topology, Docker delivery, environment boundaries, migrations, and release validation.

## Production topology

Caffeine Lane is deployed as a single Dockerized Django web service on Render.

```text
Browser
  -> Render container
      -> Gunicorn
      -> Django
          -> Neon PostgreSQL
          -> Cloudinary media storage
          -> Resend through Anymail
          -> WhiteNoise static assets
```

| Component | Platform | Responsibility |
| --- | --- | --- |
| Web runtime | Render | Run the production Docker container and serve Django via Gunicorn. |
| Database | Neon | Persist application relational data via PostgreSQL. |
| Media storage | Cloudinary | Persist user-uploaded post images and profile avatars. |
| Email service | Resend | Deliver transactional emails via Anymail backend. |
| Static assets | WhiteNoise | Serve compressed and fingerprinted static assets from the web runtime. |

The repository contains the Docker build and startup orchestration. Provider credentials and service settings are managed securely outside Git.

## Release flow

```text
Git push to main
-> GitHub Actions CI (tests, migrations check, Docker smoke)
-> Render auto-deploy triggered
-> Multi-stage Docker image built
-> entrypoint.sh checks baseline and applies migrations via DIRECT_DATABASE_URL
-> Static assets collected
-> Gunicorn launches web process
-> Render health check confirms /healthz/
-> Live traffic cut over to new release
```

GitHub Actions automates code verification, asset validation, and Docker container smoke tests. Merging to `main` triggers automated container delivery on Render.

## Web runtime container

The production container is defined in `Dockerfile` across three stages:

- **Asset stage (Node 22):** installs locked dependencies via pnpm, compiles Tailwind CSS, and minifies JavaScript into `static/dist/`.
- **Python dependency stage (Python 3.14):** installs pinned `uv` and builds the production virtual environment in `.venv`.
- **Runtime stage (Python 3.14):** runs as a non-root `app` user, copies the virtual environment and static assets, executes `docker/entrypoint.sh`, binds Gunicorn to the provider `PORT`, and monitors `/healthz/`.

### Container startup sequence

`docker/entrypoint.sh` executes the following sequence:

```text
check_fresh_baseline
-> migrate (when RUN_MIGRATIONS_ON_START=true)
-> seed (only when SEED_PORTFOLIO_ON_START=true)
-> collectstatic
-> Gunicorn
```

Migrations and demo seeding are controlled independently to ensure routine deployments execute migrations without altering live production data.

## Production configuration

Production operates under:

```text
DJANGO_SETTINGS_MODULE=config.settings.production
```

| Variable | Component | Requirement |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Web runtime | Must be set to `config.settings.production`. |
| `SECRET_KEY` | Web runtime | Unique cryptographic secret; never use development fallback. |
| `DATABASE_URL` | Web runtime | Pooled PostgreSQL connection string for normal web traffic. |
| `DIRECT_DATABASE_URL` | Migrations | Direct unpooled PostgreSQL connection string for schema migrations. |
| `ALLOWED_HOSTS` | Web runtime | Comma-separated list of approved production domain names. |
| `CSRF_TRUSTED_ORIGINS` | Web runtime | Comma-separated list of trusted HTTPS origins for CSRF validation. |
| `CLOUDINARY_URL` | Media storage | Cloudinary API URI for uploaded asset storage. |
| `RESEND_API_KEY` | Email service | API credential for transactional email dispatch. |
| `DEFAULT_FROM_EMAIL` | Email service | Verified sender email address. |
| `CONTACT_RECIPIENT_EMAIL` | Web runtime | Destination address for contact inquiries. |
| `USE_X_FORWARDED_PROTO` | Web runtime | Set to `true` behind Render's HTTPS reverse proxy. |
| `RUN_MIGRATIONS_ON_START` | Migrations | Set to `true` to execute migrations during container startup. |
| `SEED_PORTFOLIO_ON_START` | Web runtime | Set to `false` in production to prevent unintended demo data insertion. |
| `SECURE_HSTS_SECONDS` | Security | Positive integer specifying HSTS header duration. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Security | Boolean to extend HSTS to subdomains. |
| `SECURE_HSTS_PRELOAD` | Security | Boolean enabling browser HSTS preload registration. |
| `CSP_ENFORCE` | Security | Set to `true` to enforce CSP; `false` keeps report-only mode. |

Never commit production credentials or secrets to source control.

## Database migrations

Committed Django migrations are the sole mechanism for database schema evolution.

When `RUN_MIGRATIONS_ON_START=true`, the container entrypoint:
1. Validates that both `DATABASE_URL` and `DIRECT_DATABASE_URL` are present.
2. Temporarily points Django to `DIRECT_DATABASE_URL` for unpooled migration execution:
   ```bash
   python manage.py migrate --noinput
   ```
3. Restores `DATABASE_URL` so Gunicorn uses pooled connections for application traffic.

Safety rules:
- Run `check_fresh_baseline` prior to migration execution to guard against legacy schema collisions.
- Keep migration files committed and reviewed alongside their corresponding model changes.
- Validate with `uv run python manage.py makemigrations --check --dry-run` before release.
- Keep `SEED_PORTFOLIO_ON_START=false` for production deployments.

## Validation

### Health endpoint

Verify service liveness:

```bash
curl -f https://caffeinelane.onrender.com/healthz/
```

The Docker `HEALTHCHECK`, browser test runner, and CI container smoke job all monitor `/healthz/` as the readiness indicator.

### Post-deployment verification

After deployment, confirm:
- The landing and editorial home surfaces load without errors.
- Compiled CSS and JavaScript assets are delivered with correct MIME types and caching headers.
- Article detail pages and search filtering functions correctly.
- Uploaded media renders via Cloudinary storage.
- Health check returns HTTP 200.

## Deployment boundaries

- Browser clients never receive database credentials or third-party secret tokens.
- Persistent application state belongs strictly in Neon PostgreSQL, never in container ephemeral storage.
- User-uploaded media belongs in Cloudinary, not the container filesystem.
- WhiteNoise serves static distribution assets; it does not store user uploads.
- Schema migrations use a dedicated direct connection, isolating migration DDL from pooled web requests.

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
