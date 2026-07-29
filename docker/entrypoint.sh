#!/bin/sh
set -eu

python manage.py check_fresh_baseline
python manage.py collectstatic --noinput
exec "$@"
