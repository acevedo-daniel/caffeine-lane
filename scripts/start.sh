#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

if [[ -n "${DIRECT_DATABASE_URL:-}" ]]; then
  export DATABASE_URL="$DIRECT_DATABASE_URL"
fi

uv run python manage.py migrate --noinput

exec uv run gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
