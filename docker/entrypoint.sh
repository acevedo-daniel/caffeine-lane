#!/bin/sh
set -eu

python manage.py check_fresh_baseline

if [ "${RUN_RELEASE_TASKS_ON_START:-0}" = "1" ]; then
    : "${DATABASE_URL:?DATABASE_URL must point to Neon pooled connection}"
    : "${DIRECT_DATABASE_URL:?DIRECT_DATABASE_URL must point to Neon direct connection}"

    pooled_database_url="$DATABASE_URL"
    export DATABASE_URL="$DIRECT_DATABASE_URL"
    python manage.py migrate --noinput

    export DATABASE_URL="$pooled_database_url"
    python manage.py seed_portfolio
fi

python manage.py collectstatic --noinput
exec "$@"
