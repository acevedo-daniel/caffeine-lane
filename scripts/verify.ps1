Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Invoke-Checked([string]$Label, [scriptblock]$Command) {
    Write-Host "==> $Label"
    $global:LASTEXITCODE = 0
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

$envNames = @(
    "TEST_DATABASE_URL",
    "DJANGO_SETTINGS_MODULE",
    "DATABASE_URL",
    "DEBUG_TOOLBAR_ENABLED",
    "E2E_DATABASE_URL",
    "SECRET_KEY",
    "ALLOWED_HOSTS",
    "CSRF_TRUSTED_ORIGINS",
    "CLOUDINARY_URL",
    "RESEND_API_KEY",
    "DEFAULT_FROM_EMAIL",
    "CONTACT_RECIPIENT_EMAIL",
    "USE_X_FORWARDED_PROTO",
    "CSP_ENFORCE",
    "SECURE_HSTS_SECONDS",
    "SECURE_HSTS_INCLUDE_SUBDOMAINS",
    "SECURE_HSTS_PRELOAD"
)

$savedEnv = @{}
foreach ($name in $envNames) {
    $item = Get-Item -Path "Env:$name" -ErrorAction SilentlyContinue
    $savedEnv[$name] = if ($null -ne $item) { $item.Value } else { $null }
}

Push-Location $repoRoot
try {
    # 1. Quality and Tests (PostgreSQL 18 as in CI)
    Invoke-Checked "Start PostgreSQL 18 container" {
        docker compose up -d --wait db
    }
    $env:TEST_DATABASE_URL = "postgresql://caffeine-lane:caffeine-lane@localhost:5432/caffeine-lane"
    $checkCommands = Get-Content (Join-Path $PSScriptRoot "check.ps1") |
        Where-Object { $_ -and $_ -notmatch '^\s*#' -and $_ -notmatch '^\s*\$ErrorActionPreference\s*=' }
    foreach ($cmd in $checkCommands) {
        Invoke-Checked $cmd {
            Invoke-Expression $cmd
        }
    }

    # 2. E2E (isolated SQLite database)
    New-Item -ItemType Directory -Force -Path "tmp" | Out-Null
    Remove-Item -ErrorAction SilentlyContinue "tmp\verify-e2e.sqlite3"
    $e2eDbUrl = "sqlite:///tmp/verify-e2e.sqlite3"
    $env:DJANGO_SETTINGS_MODULE = "config.settings.local"
    $env:DATABASE_URL = $e2eDbUrl
    $env:DEBUG_TOOLBAR_ENABLED = "false"
    Invoke-Checked "Check fresh baseline for E2E" {
        uv run python manage.py check_fresh_baseline
    }
    Invoke-Checked "Migrate E2E database" {
        uv run python manage.py migrate --noinput
    }
    Invoke-Checked "Seed editorial data for E2E" {
        uv run python manage.py seed_editorial
    }
    $env:E2E_DATABASE_URL = $e2eDbUrl
    Invoke-Checked "Run Playwright E2E suite" {
        pnpm run test:e2e
    }

    # 3. Production
    Invoke-Checked "Verify Vercel build contract" {
        uv run python -c "import tomllib; config = tomllib.load(open('pyproject.toml', 'rb')); assert config['tool']['vercel']['scripts']['build'] == 'pnpm run build'"
    }
    $env:DJANGO_SETTINGS_MODULE = "config.settings.production"
    $env:SECRET_KEY = "ci-production-secret-key-not-for-production-0123456789"
    $env:DATABASE_URL = "sqlite:///:memory:"
    $env:ALLOWED_HOSTS = "example.test"
    $env:CSRF_TRUSTED_ORIGINS = "https://example.test"
    $env:CLOUDINARY_URL = "cloudinary://123456789012345:ci-secret@example"
    $env:RESEND_API_KEY = "re_ci_not_a_real_key"
    $env:DEFAULT_FROM_EMAIL = "noreply@example.test"
    $env:CONTACT_RECIPIENT_EMAIL = "owner@example.test"
    $env:USE_X_FORWARDED_PROTO = "true"
    $env:CSP_ENFORCE = "false"
    $env:SECURE_HSTS_SECONDS = "31536000"
    $env:SECURE_HSTS_INCLUDE_SUBDOMAINS = "true"
    $env:SECURE_HSTS_PRELOAD = "true"
    Invoke-Checked "Run Django production deployment checks" {
        uv run python manage.py check --deploy
    }

    # 4. Docker
    Invoke-Checked "Build production Docker image" {
        docker build -t caffeine-lane-verify .
    }
}
finally {
    Pop-Location
    foreach ($name in $envNames) {
        if ($null -eq $savedEnv[$name]) {
            Remove-Item -Path "Env:$name" -ErrorAction SilentlyContinue
        }
        else {
            Set-Item -Path "Env:$name" -Value $savedEnv[$name]
        }
    }
}
