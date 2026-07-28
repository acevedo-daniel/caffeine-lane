set -o errexit

uv sync --frozen --no-dev

uv run --no-sync python manage.py collectstatic --no-input
uv run --no-sync python manage.py migrate
uv run --no-sync python manage.py loaddata initial_data.json
