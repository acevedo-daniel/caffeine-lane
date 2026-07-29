#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

if [[ -n "${DIRECT_DATABASE_URL:-}" ]]; then
  DATABASE_URL="$DIRECT_DATABASE_URL" uv run python manage.py migrate --noinput
else
  uv run python manage.py migrate --noinput
fi

exec uv run gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
