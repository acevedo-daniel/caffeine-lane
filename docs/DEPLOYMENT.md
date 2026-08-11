# Deployment

## Environments

| Environment | Purpose | Deployment source |
|---|---|---|
| Local | Day-to-day development with Compose PostgreSQL or deliberate SQLite fallback | Developer workstation and `config.settings.local` |
| Test | Isolated automated validation | pytest, GitHub Actions, and `config.settings.test` |
| Production | Public Caffeine Lane service | Render Docker deployment and `config.settings.production` |

## Flow

Render builds the root `Dockerfile`. Its multi-stage build installs locked frontend dependencies, creates `static/dist`, installs locked Python runtime dependencies, and starts the production image with Gunicorn. The image entrypoint is the only web-process startup path: it checks the database baseline, runs optional migrations, runs an explicitly requested seed, collects static files, and finally starts Gunicorn.

GitHub Actions validates the same Dockerfile before deployment, but it does not publish an image or initiate a Render deployment.

## Configuration and secrets

- **Configuration:** Render environment variables and the production settings module.
- **Secrets:** Set provider credentials only in Render. Never commit values to Git, `.env.example`, README files, Dockerfiles, or a versioned Render configuration.

| Variable | Required | Purpose |
|---|:---:|---|
| `DJANGO_SETTINGS_MODULE` | Yes | `config.settings.production`. |
| `SECRET_KEY` | Yes | Production Django signing key; must not use the local placeholder. |
| `DATABASE_URL` | Yes | Neon pooled URL used by the running application. |
| `DIRECT_DATABASE_URL` | When startup migrations run | Neon direct URL used only for `migrate`. |
| `ALLOWED_HOSTS` | Yes | Comma-separated Render hostnames. |
| `CSRF_TRUSTED_ORIGINS` | Yes for deployed form origins | Comma-separated HTTPS origins. |
| `CLOUDINARY_URL` | Yes | Cloudinary media-storage credential. |
| `RESEND_API_KEY` | Yes | Resend credential used by Anymail. |
| `DEFAULT_FROM_EMAIL` | No | Sender for transactional email; production settings provide an onboarding-sender default. |
| `CONTACT_RECIPIENT_EMAIL` | Yes | Contact-form recipient. |
| `PASSWORD_RESET_ENABLED` | No | Keep `false` while using the limited Resend onboarding sender. |
| `RUN_MIGRATIONS_ON_START` | No | `true` runs migrations at web-process start; the image default is `true`. |
| `SEED_PORTFOLIO_ON_START` | No | `false` by default; set `true` only for one intentional seed deployment. |
| `WEB_CONCURRENCY` | No | Optional Gunicorn worker count; the image defaults to `1`. |
| `USE_X_FORWARDED_PROTO` | Yes on Render | Trust Render's HTTPS proxy header. |
| `CSP_ENFORCE` | No | Enables enforcement after report-only validation. |
| `SECURE_HSTS_SECONDS` | No | HSTS duration in seconds. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | No | Optional HSTS subdomain behavior. |
| `SECURE_HSTS_PRELOAD` | No | Optional HSTS preload behavior. |
| `CONTACT_RATE_LIMIT` / `CONTACT_RATE_LIMIT_WINDOW` | No | Contact form limit and window. |

`DATABASE_URL` must always remain defined for runtime. When `RUN_MIGRATIONS_ON_START=true`, the entrypoint temporarily assigns `DIRECT_DATABASE_URL` to `DATABASE_URL` only for `manage.py migrate`, then restores the pooled URL before starting Gunicorn. If migrations are disabled, the direct URL is not required by the entrypoint.

## Standard deployment

1. Configure Render to use build context `.`, Dockerfile path `./Dockerfile`, an empty Docker Command, and Health Check Path `/healthz/`.
2. Set the required production variables, with `RUN_MIGRATIONS_ON_START=true` and `SEED_PORTFOLIO_ON_START=false` for normal operation.
3. Deploy from the intended repository revision and inspect the Render logs for the baseline check, migrations when enabled, `collectstatic`, and Gunicorn startup.
4. Validate `/healthz/`, `/home/`, a static asset, media delivery, the contact form, and the expected HTTPS behavior.

The container listens on `0.0.0.0:${PORT:-8000}`. Gunicorn uses `${WEB_CONCURRENCY:-1}` worker and two threads, logs access and errors to standard output, and the Docker health check uses the same `PORT` value.

## Migrations

Render Free has no dedicated release command in this setup, so migrations run at startup when `RUN_MIGRATIONS_ON_START=true`. This is the documented production policy. The entrypoint fails early if either the pooled or direct Neon URL is absent while migrations are enabled.

For a first content bootstrap only:

1. Set `SEED_PORTFOLIO_ON_START=true` in Render.
2. Deploy and confirm `Portfolio ready: 3 categories and 19 posts.` in the logs.
3. Set `SEED_PORTFOLIO_ON_START=false` before any later restart or redeploy.

Seeding is never automatic by default. It is idempotent but updates its defined sample posts, so it must not be used as a routine content refresh. No seed, Docker build, or entrypoint creates a privileged user.

Create the first administrator only from a trusted workstation. Temporarily set `DATABASE_URL` to the Neon direct URL, run the interactive command, then restore the pooled URL before operating the web service:

```bash
uv run python manage.py createsuperuser
```

[`scripts/release.sh`](../scripts/release.sh) remains an optional trusted-workstation maintenance helper. It runs the fresh-baseline check, migrations through the direct URL, and structural-category verification; Docker and Render do not invoke it.

## Validation

- `GET /healthz/` must return `{"status": "ok"}`.
- `/home/` must load with no server error, and generated static assets must respond.
- Verify posts are backed by Neon, uploads are delivered through Cloudinary, and static files are served through WhiteNoise.
- Submit a controlled contact message and verify Resend delivery or controlled failure feedback.
- Confirm `PASSWORD_RESET_ENABLED=false` shows the demo limitation rather than attempting public recovery email.
- Review Render logs for unexpected migration, seed, `collectstatic`, or Gunicorn failures.

## Rollback / recovery

There is no automated rollback script in this repository. For an application regression, redeploy a known working revision through Render and keep `SEED_PORTFOLIO_ON_START=false` so manual editorial changes are not overwritten. For a migration issue, prefer a forward migration or restore the database using the provider's documented recovery process. The exact database restore runbook is **[pending]** and must be established before relying on destructive recovery.
