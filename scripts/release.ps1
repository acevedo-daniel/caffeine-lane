Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($env:DATABASE_URL)) {
    throw "DATABASE_URL must point to the Neon pooled connection."
}

if ([string]::IsNullOrWhiteSpace($env:DIRECT_DATABASE_URL)) {
    throw "DIRECT_DATABASE_URL must point to the Neon direct connection."
}

function Invoke-DjangoCommand([string[]]$Arguments) {
    & uv run python manage.py @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Django command failed: manage.py $($Arguments -join ' ')"
    }
}

$pooledDatabaseUrl = $env:DATABASE_URL
try {
    $env:DJANGO_SETTINGS_MODULE = "config.settings.production"
    $env:DATABASE_URL = $env:DIRECT_DATABASE_URL

    Invoke-DjangoCommand @("check_fresh_baseline")
    Invoke-DjangoCommand @("migrate", "--noinput")
    Invoke-DjangoCommand @("verify_editorial_baseline")
}
finally {
    $env:DATABASE_URL = $pooledDatabaseUrl
}
