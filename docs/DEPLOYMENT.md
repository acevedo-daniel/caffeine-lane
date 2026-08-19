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

| Component | Target | Responsibility |
| --- | --- | --- |
| Web runtime | Render | Run the production Docker image and expose the Django/Gunicorn service. |
| Database | Neon | Persist application data through PostgreSQL. |
| Media | Cloudinary | Persist uploaded post images and avatars. |
| Email | Resend through Anymail | Deliver production email. |
| Static assets | WhiteNoise | Serve collected, fingerprinted/compressed static assets from the application runtime. |

The repository contains the Docker build and startup logic. Provider-specific secrets and service configuration are managed outside Git.

## Docker image

The production `Dockerfile` has three stages.

### Asset stage

A Node 22 image:

- installs the locked pnpm dependencies;
- builds Tailwind CSS;
- builds JavaScript assets into `static/dist/`.

### Python dependency stage

A Python 3.14 image:

- installs the pinned `uv` tool;
- installs the locked production Python environment into `.venv`.

### Runtime stage

The final Python 3.14 image:

- runs as a non-root `app` user;
- copies the production virtual environment and built frontend assets;
- uses `docker/entrypoint.sh`;
- starts Gunicorn on the provider-supplied `PORT`;
- defines a container health check against `/healthz/`.

## Startup sequence

`docker/entrypoint.sh` runs:

```text
check_fresh_baseline
-> migrate when RUN_MIGRATIONS_ON_START=true
-> seed only when SEED_PORTFOLIO_ON_START=true
-> collectstatic
-> Gunicorn
```

Migrations and seeding are separately controlled so normal production startup can migrate without automatically inserting portfolio demo content.

## Production configuration

Production uses:

```text
DJANGO_SETTINGS_MODULE=config.settings.production
```

Important environment values include:

| Variable | Purpose |
| --- | --- |
| `SECRET_KEY` | Django signing secret. Must not use the local/default value. |
| `DATABASE_URL` | PostgreSQL connection used by the normal application runtime. |
| `DIRECT_DATABASE_URL` | Direct PostgreSQL connection used by startup migrations when enabled. |
| `ALLOWED_HOSTS` | Allowed production hostnames. |
| `CSRF_TRUSTED_ORIGINS` | Trusted HTTPS origins for CSRF-protected requests. |
| `CLOUDINARY_URL` | Production uploaded-media storage credentials/configuration. |
| `RESEND_API_KEY` | Resend credential used by Anymail. |
| `DEFAULT_FROM_EMAIL` | Production sender identity. |
| `CONTACT_RECIPIENT_EMAIL` | Recipient for contact submissions. |
| `USE_X_FORWARDED_PROTO` | Enables trust of the HTTPS proxy header when required by the host. |
| `RUN_MIGRATIONS_ON_START` | Controls startup migration execution; the image defaults it to `true`. |
| `SEED_PORTFOLIO_ON_START` | Controls portfolio seeding; the image defaults it to `false`. |
| `SECURE_HSTS_SECONDS` | Configures HSTS duration. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Extends HSTS to subdomains when enabled. |
| `SECURE_HSTS_PRELOAD` | Enables HSTS preload flag when appropriate. |
| `CSP_ENFORCE` | Switches the configured CSP from report-only to enforced mode. |

Do not commit production values for these settings.

## Production security configuration

`config.settings.production` requires a non-development `SECRET_KEY`, `DATABASE_URL`, and at least one allowed host.

It configures:

- `DEBUG = False`;
- HTTPS redirect behavior;
- secure session and CSRF cookies;
- configurable HSTS;
- content-type and referrer protections;
- a Content Security Policy;
- Cloudinary storage for uploaded media;
- WhiteNoise compressed-manifest storage for static assets;
- Resend/Anymail for email;
- Argon2 as the first password hasher.

Run Django's deployment checks when production configuration changes:

```bash
uv run python manage.py check --deploy
```

with the required production environment supplied.

## Database migrations

Committed Django migrations are the schema-change mechanism.

When:

```text
RUN_MIGRATIONS_ON_START=true
```

the entrypoint requires both database URLs. It temporarily replaces the normal pooled `DATABASE_URL` with `DIRECT_DATABASE_URL`, runs:

```bash
python manage.py migrate --noinput
```

then restores the pooled runtime URL before Gunicorn starts.

Production rules:

- do not point migration commands at an unintended database;
- keep migration files committed with model changes;
- run `makemigrations --check --dry-run` in CI before release;
- keep `SEED_PORTFOLIO_ON_START=false` for normal deployments;
- use `seed_portfolio` only as an intentional bootstrap when demo content is actually desired.

## Static and media delivery

Static frontend assets are built during the Docker build and collected at container startup.

Production static path:

```text
static/src
-> build
-> static/dist
-> collectstatic
-> WhiteNoise
```

Uploaded media is stored through Cloudinary and therefore does not rely on the Render container filesystem.

## Validation

### Health

The public liveness endpoint is:

```text
https://caffeinelane.onrender.com/healthz/
```

The Docker `HEALTHCHECK`, browser test server, and CI smoke workflow all use `/healthz/` as a readiness/liveness signal.

### Application

After a deployment, verify:

- the landing/home route loads;
- generated CSS and JavaScript are served;
- a published article can be opened;
- search/category navigation works;
- uploaded media renders through the production storage configuration.

### Provider-dependent flows

When changing Cloudinary or Resend configuration, separately verify the affected upload/email workflow rather than treating the health endpoint as proof of external-provider behavior.

## Deployment boundaries

- The browser never receives database or provider secret credentials.
- Persistent application data belongs in PostgreSQL, not the Render container filesystem.
- Persistent uploaded media belongs in Cloudinary, not the Render container filesystem.
- WhiteNoise serves built/collected static assets; it is not persistent user-media storage.
- Production schema migration uses the direct connection only for the migration step; normal runtime uses `DATABASE_URL`.
- The repository does not currently define a Render-specific infrastructure manifest, so provider-side service/secrets configuration must remain synchronized with the Docker/application requirements.

## Related documentation

- [README](../README.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
