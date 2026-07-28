set -o errexit

pnpm install --frozen-lockfile
pnpm run build

uv sync --frozen --no-dev

uv run --no-sync python manage.py collectstatic --no-input
uv run --no-sync python manage.py migrate
