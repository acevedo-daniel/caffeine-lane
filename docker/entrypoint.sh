#!/bin/sh
set -eu

if [ -n "${DIRECT_DATABASE_URL:-}" ]; then
    DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py migrate --noinput
else
    python manage.py migrate --noinput
fi

python manage.py collectstatic --noinput
exec "$@"
