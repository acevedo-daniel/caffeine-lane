#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

uv sync --frozen --no-dev
uv run python manage.py collectstatic --noinput
uv run python manage.py check
