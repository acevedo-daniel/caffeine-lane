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

The live application is [caffeine-lane.vercel.app](https://caffeine-lane.vercel.app/).

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

## Vercel web runtime

- **Config:** `pyproject.toml`
- **Build:** `pnpm install --frozen-lockfile --prod=false && pnpm run build`
- **Start:** Vercel Python WSGI handler
- **Validation:** `https://caffeine-lane.vercel.app/healthz/`

Vercel installs Python dependencies from `pyproject.toml` and `uv.lock`. In the Vercel project settings, leave **Install Command** at its default so that Python dependencies are installed automatically. Because this repository also builds a pnpm asset pipeline, set the Vercel **Build Command** to:

```bash
pnpm install --frozen-lockfile --prod=false && pnpm run build
```

Do not replace the Install Command with `pnpm install` alone: a custom install command can prevent Vercel from installing Django. The `pyproject.toml` build hook remains `pnpm run build` for the repository and CI build contract; the Vercel dashboard command adds the frontend dependency installation required by the hosted build.

## Production configuration

| Variable | Component | Requirement |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Vercel runtime | Must be set to `config.settings.production`. |
| `SECRET_KEY` | Vercel runtime | Unique Django cryptographic secret. |
| `DATABASE_URL` | Vercel runtime | Neon **pooled** connection string used by the web runtime. |
| `ALLOWED_HOSTS` | Vercel runtime | Production and preview hostnames, comma-separated. |
| `CSRF_TRUSTED_ORIGINS` | Vercel runtime | HTTPS production and preview origins, comma-separated. |
| `PUBLIC_SITE_URL` | Vercel runtime | Canonical, sitemap, and social-card base URL; set production to `https://caffeine-lane.vercel.app`. |
| `CLOUDINARY_URL` | Vercel runtime | Cloudinary storage credentials. |
| `RESEND_API_KEY` | Vercel runtime | Resend API credential. |
| `DEFAULT_FROM_EMAIL` | Vercel runtime | Verified sender address. |
| `CONTACT_RECIPIENT_EMAIL` | Vercel runtime | Recipient for contact submissions. |
| `PASSWORD_RESET_ENABLED` | Vercel runtime | Keep `false` until a verified Resend sending domain is configured. |
| `USE_X_FORWARDED_PROTO` | Vercel runtime | Must be `true` behind Vercel's HTTPS proxy. |
| `CSP_ENFORCE` | Vercel runtime | Start with `false`; enable after CSP reports are reviewed. |
| `SECURE_HSTS_SECONDS` | Vercel runtime | Positive duration after the production domain is stable. |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | Vercel runtime | Enable only when every subdomain is HTTPS-ready. |
| `SECURE_HSTS_PRELOAD` | Vercel runtime | Enable only after an intentional preload decision. |

Do **not** add `DIRECT_DATABASE_URL` to the Vercel runtime. It is only used by a controlled release command from a trusted terminal or release runner.

Preview deployments need an isolated Neon branch/database and their own `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`. Until that branch integration is configured, keep previews read-only or use no database-backed preview paths.

### Resend boundary

Production settings require the Resend configuration because the production email backend is Anymail/Resend. Without a verified domain, `onboarding@resend.dev` is suitable only for controlled testing to the Resend account email; it is not a general sender for arbitrary recipients. Keep `PASSWORD_RESET_ENABLED=false` until a domain is verified and `DEFAULT_FROM_EMAIL` uses that domain. See Resend's [resend.dev sending restriction](https://resend.com/docs/knowledge-base/403-error-resend-dev-domain) and [domain verification guide](https://resend.com/docs/dashboard/domains/introduction).

The contact flow must report a delivery failure instead of showing success when Resend rejects or cannot deliver a message. Exercise that failure path in tests and use Resend's [safe test recipients](https://resend.com/docs/dashboard/emails/send-test-emails) for controlled delivery checks.

Contact protection combines CSRF, a hidden honeypot field, input length limits, and an IP-based rate limit. The default limit is five submissions per hour (`CONTACT_RATE_LIMIT=5`, `CONTACT_RATE_LIMIT_WINDOW=3600`). Vercel's default cache is not a shared distributed limiter, so this is a basic best-effort protection; introduce shared rate limiting only if real abuse requires it.

### Public metadata boundary

`PUBLIC_SITE_URL` is the source of truth for canonical URLs, Open Graph URLs, JSON-LD URLs, `robots.txt`, and `sitemap.xml`. Set it explicitly in the production Vercel environment and never point it at a preview deployment. Public landing, home, category, and published article pages are indexable; authentication, admin, contact, search, comment, editor, and error surfaces are marked `noindex` or disallowed from crawling.

The base template also provides the favicon, web manifest, theme colors, Open Graph tags, and Twitter/X card tags. The sitemap only includes public landing, home, category, and published article URLs.

## Database migrations

```bash
# Generate and verify migrations locally
uv run python manage.py makemigrations
uv run python manage.py makemigrations --check --dry-run

# Run production migration release (macOS / Linux)
./scripts/release.sh

# Run production migration release (Windows PowerShell)
./scripts/release.ps1
```

Safety rules:
- Schema migrations run outside the Vercel build using `DIRECT_DATABASE_URL`; `DIRECT_DATABASE_URL` must never be added to the Vercel runtime.
- Pre-flight `check_fresh_baseline` inspects the target database and aborts if legacy schema or incompatible tables are detected.
- Post-migration `verify_editorial_baseline` validates that structural categories exist and are sound.
- Migrations are idempotent: a release with no pending migrations does not alter the schema. Never run `makemigrations` against Neon.

## Editorial dataset

The editorial dataset is intentionally separate from schema release:

```bash
uv run python manage.py seed_editorial --dry-run
uv run python manage.py seed_editorial
```

The dry run checks text, slugs, dates, category distribution, and bundled images without writing data. The seed itself is idempotent, but it writes content and can upload media. Run it only after editorial review and never as part of a normal Vercel deployment. Docker's `SEED_EDITORIAL_ON_START` remains disabled by default for exceptional self-hosted use.

## Validation

Before production:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py check --deploy
uv run pytest
pnpm install --frozen-lockfile --prod=false
pnpm run build
pnpm test
pnpm run test:e2e
```

After deployment, verify:

- `/healthz/` returns HTTP 200.
- The public URL `https://caffeine-lane.vercel.app/` resolves successfully.
- Landing, home, categories, search, authentication, and contact flow work.
- CSS and JavaScript are served from Vercel's CDN.
- Cloudinary media renders correctly.
- `/robots.txt` and `/sitemap.xml` use the production public URL and expose only indexable routes.
- The home page and a published article contain canonical, Open Graph, Twitter/X, and JSON-LD metadata.
- No errors appear in Vercel deployment and runtime logs.

## Docker boundary

The Docker image remains a portable production-like artifact and a CI smoke-test target. Its startup defaults do not run migrations or seed editorial data. Vercel does not execute `docker/entrypoint.sh`.

## Related documentation

- [README](../README.md)
- [Project](PROJECT.md)
- [Architecture](ARCHITECTURE.md)
- [Development](DEVELOPMENT.md)
- [Testing](TESTING.md)
