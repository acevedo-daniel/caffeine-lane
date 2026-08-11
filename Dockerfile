# syntax=docker/dockerfile:1
FROM node:22.18.0-alpine AS assets

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY scripts ./scripts
COPY static/src ./static/src
COPY templates ./templates
COPY apps ./apps
RUN pnpm run build


FROM python:3.13.6-slim AS dependencies

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
WORKDIR /app
RUN pip install --no-cache-dir uv==0.11.32
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev


FROM python:3.13.6-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    RUN_MIGRATIONS_ON_START=true \
    SEED_PORTFOLIO_ON_START=false \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
RUN groupadd --system app && useradd --system --gid app --home-dir /app app

COPY --from=dependencies /app/.venv /app/.venv
COPY --chown=app:app . .
COPY --from=assets --chown=app:app /app/static/dist /app/static/dist
COPY --chown=app:app docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod 755 /entrypoint.sh \
    && mkdir /app/staticfiles && chown app:app /app/staticfiles

USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/healthz/' % os.environ.get('PORT', '8000'), timeout=2)" || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads 2 --timeout 120 --access-logfile=- --error-logfile=- config.wsgi:application"]
