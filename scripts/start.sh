#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

uv run python manage.py check_fresh_baseline

exec uv run gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers 1 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
