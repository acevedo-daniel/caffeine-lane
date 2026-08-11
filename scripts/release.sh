#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

: "${DATABASE_URL:?DATABASE_URL must point to Neon pooled connection}"
: "${DIRECT_DATABASE_URL:?DIRECT_DATABASE_URL must point to Neon direct connection}"

export DATABASE_URL="$DIRECT_DATABASE_URL"

uv run python manage.py check_fresh_baseline
uv run python manage.py migrate --noinput
uv run python manage.py verify_portfolio_baseline
