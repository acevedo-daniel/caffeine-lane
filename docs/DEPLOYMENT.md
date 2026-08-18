# Deployment

> Hosted topology, multi-stage Docker delivery, database migrations, and validation.

## Environments

| Environment    | Purpose                                           | Deployment Source                                                          |
| -------------- | ------------------------------------------------- | -------------------------------------------------------------------------- |
| **Local**      | Development and disposable database verification. | Developer workstation, Docker Compose, `config.settings.local`             |
| **Test**       | Automated CI pipeline validation.                 | GitHub Actions, PostgreSQL 18 service, `config.settings.test`              |
| **Production** | Live public web service and persistent user data. | Render Web Service (Docker), Neon PostgreSQL, `config.settings.production` |

## Deployment Targets

```text
Browser -> HTTPS -> Render (Docker / Gunicorn) -> Neon PostgreSQL + Cloudinary + Resend
```

| Component               | Selected Target  | Responsibility                                                  |
| ----------------------- | ---------------- | --------------------------------------------------------------- |
| **Web Service**         | Render           | Executes the containerized Django Gunicorn application.         |
| **Database**            | Neon             | Provides managed PostgreSQL 18 with connection pooling.         |
| **Media Storage**       | Cloudinary       | Persistent object storage for article images and user avatars.  |
| **Transactional Email** | Resend (Anymail) | Delivers contact form submissions and password recovery emails. |
| **Static Delivery**     | WhiteNoise       | Embedded high-performance static asset server.                  |

## Multi-Stage Docker Delivery

The production image is built using a multi-stage `Dockerfile`:

1. **Asset Builder Stage (`node:22-alpine`):** Installs locked frontend dependencies, compiles Tailwind CSS 4, and builds minified JavaScript bundles into `static/dist/`.
2. **Dependency Stage (`python:3.13-slim`):** Uses `uv` to compile and install locked production dependencies into a standalone virtual environment (`/app/.venv`).
3. **Runtime Stage (`python:3.13-slim`):** Combines the pre-built virtual environment and compiled static assets into a non-privileged `app` container, managed by `docker/entrypoint.sh`.

## Container Startup Sequence

The container entrypoint (`/entrypoint.sh`) executes deterministically on every container boot:

```text
1. Database baseline sanity check (check_fresh_baseline)
2. Database migrations (if RUN_MIGRATIONS_ON_START=true, using DIRECT_DATABASE_URL)
3. Portfolio seeding (if SEED_PORTFOLIO_ON_START=true)
4. Static file collection (collectstatic --noinput)
5. Gunicorn HTTP server execution (listening on $PORT with 2 threads)
```

## Production Configuration & Secrets

Configure production variables exclusively in Render's secure dashboard. Never commit secrets to Git or Dockerfiles.

| Variable                  | Required | Purpose                                                                        |
| ------------------------- | :------: | ------------------------------------------------------------------------------ |
| `DJANGO_SETTINGS_MODULE`  |   Yes    | Must be `config.settings.production`.                                          |
| `SECRET_KEY`              |   Yes    | High-entropy production signing key.                                           |
| `DATABASE_URL`            |   Yes    | Neon pooled connection string for web runtime.                                 |
| `DIRECT_DATABASE_URL`     |   Yes    | Neon direct connection string used for schema migrations.                      |
| `ALLOWED_HOSTS`           |   Yes    | Comma-separated deployed hostnames.                                            |
| `CSRF_TRUSTED_ORIGINS`    |   Yes    | Comma-separated deployed HTTPS origins.                                        |
| `CLOUDINARY_URL`          |   Yes    | Cloudinary storage connection string.                                          |
| `RESEND_API_KEY`          |   Yes    | Resend API key for transactional email.                                        |
| `CONTACT_RECIPIENT_EMAIL` |   Yes    | Target email address for contact form inquiries.                               |
| `USE_X_FORWARDED_PROTO`   |   Yes    | Set to `true` to trust Render HTTPS reverse proxy headers.                     |
| `RUN_MIGRATIONS_ON_START` |    No    | Defaults to `true` to run forward migrations on deployment.                    |
| `SEED_PORTFOLIO_ON_START` |    No    | Defaults to `false`; toggle `true` only for one intentional initial bootstrap. |

## Database Migration Strategy

- **Connection Split:** Web requests utilize Neon's connection pooler (`DATABASE_URL`), while schema migrations require direct connections (`DIRECT_DATABASE_URL`) to support DDL transactions and advisory locks.
- **Forward Migrations:** Schema changes are strictly additive and use committed forward migration scripts.
- **First Administrator Creation:** Run `createsuperuser` from a trusted terminal using the direct database connection:
  ```bash
  DATABASE_URL=$DIRECT_DATABASE_URL uv run python manage.py createsuperuser
  ```

## Release Validation

- **Health Check:** `GET /healthz/` returns `200 OK` with `{"status": "ok"}`.
- **Public Navigation:** Verify `https://your-domain.com/` loads with zero errors and that static CSS/JS assets respond with proper cache headers.
- **Media Delivery:** Confirm uploaded post images are served properly through Cloudinary.
- **Contact Form:** Submit a test message and confirm receipt via Resend.

## Rollback and Recovery

- **Application Rollback:** Revert to the previous stable Git commit and trigger a Render deployment with `SEED_PORTFOLIO_ON_START=false`.
- **Database Recovery:** Apply a reviewed forward migration or restore from Neon automated point-in-time snapshots.

## Related Documentation

- [Development](DEVELOPMENT.md)
- [Architecture](ARCHITECTURE.md)
- [Testing](TESTING.md)
