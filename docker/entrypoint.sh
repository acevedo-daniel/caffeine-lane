#!/bin/sh
set -eu

python manage.py check_fresh_baseline

if [ "${RUN_MIGRATIONS_ON_START:-false}" = "true" ]; then
    : "${DATABASE_URL:?DATABASE_URL must point to Neon pooled connection}"
    : "${DIRECT_DATABASE_URL:?DIRECT_DATABASE_URL must point to Neon direct connection}"

    pooled_database_url="$DATABASE_URL"
    export DATABASE_URL="$DIRECT_DATABASE_URL"
    python manage.py migrate --noinput
    export DATABASE_URL="$pooled_database_url"
fi

if [ "${SEED_EDITORIAL_ON_START:-false}" = "true" ]; then
    : "${DATABASE_URL:?DATABASE_URL must point to Neon pooled connection}"
    # A seed may be requested independently after a database has already been
    # migrated. Verify that prerequisite so an accidental flag has a clear
    # failure instead of a database-table traceback.
    python manage.py verify_editorial_baseline
    python manage.py seed_editorial
fi

python manage.py collectstatic --noinput
exec "$@"
