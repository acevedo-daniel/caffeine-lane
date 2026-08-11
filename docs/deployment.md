# Render Free deployment

## Startup strategy

Render Free has no dedicated release command. The [entrypoint](../docker/entrypoint.sh)
is the only startup path: it checks the accounts fresh baseline, uses
`DIRECT_DATABASE_URL` for migrations when `RUN_MIGRATIONS_ON_START=true`, returns
to the pooled `DATABASE_URL`, optionally runs `seed_portfolio`, collects static
files, and starts Gunicorn.

Keep `SEED_PORTFOLIO_ON_START=false` after the first content deployment so
editorial changes made in Django Admin are preserved.

## Required variables

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<long-random-production-secret>
DATABASE_URL=<neon-pooled-url>
DIRECT_DATABASE_URL=<neon-direct-url>
ALLOWED_HOSTS=caffeinelane.onrender.com
CSRF_TRUSTED_ORIGINS=https://caffeinelane.onrender.com
CLOUDINARY_URL=<cloudinary-credential>
RESEND_API_KEY=<resend-api-key>
DEFAULT_FROM_EMAIL=The Caffeine Lane <onboarding@resend.dev>
CONTACT_RECIPIENT_EMAIL=<controlled-inbox>
PASSWORD_RESET_ENABLED=false
RUN_MIGRATIONS_ON_START=true
SEED_PORTFOLIO_ON_START=false
USE_X_FORWARDED_PROTO=true
CSP_ENFORCE=false
SECURE_HSTS_SECONDS=3600
SECURE_HSTS_INCLUDE_SUBDOMAINS=false
SECURE_HSTS_PRELOAD=false
```

Never commit secrets to Git, the README, `.env.example`, the Dockerfile, or a
Render configuration file.

## First content deployment

1. Set `SEED_PORTFOLIO_ON_START=true` temporarily.
2. Deploy and verify `Portfolio ready: 3 categories and 10 posts.` in the logs.
3. Return the flag to `false` and redeploy.

Use the root Dockerfile with build context `.`, Dockerfile path `./Dockerfile`,
an empty Docker Command, and health check path `/healthz/`. Gunicorn defaults to
one worker, uses two threads, and listens on Render's `PORT`.

## Services and email

- Neon: pooled connection for the application and direct connection for migrations.
- Cloudinary: user media; never depend on Render disk for uploads.
- WhiteNoise: static files.
- Resend via Anymail: transactional email.

Keep `PASSWORD_RESET_ENABLED=false` while using `onboarding@resend.dev`. It
cannot deliver public password-reset email, and the UI displays the demo limit.

## First administrator

No seed, Docker build, or entrypoint creates privileged users. From a trusted
machine, temporarily set `DATABASE_URL` to Neon's direct connection and run:

```bash
uv run python manage.py createsuperuser
```

Enter credentials only at the interactive prompt, then restore the pooled URL
before running the web application. Never store passwords in seeds, GitHub,
the README, `.env.example`, Dockerfiles, or versioned variables.
