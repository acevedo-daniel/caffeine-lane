$ErrorActionPreference = "Stop"

uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --settings=config.settings.test --check --dry-run
uv run pytest
pnpm install --frozen-lockfile
pnpm run build
pnpm test
