$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFilePath = Join-Path $projectRoot ".env"

if (Test-Path $envFilePath) {
    $bytecodeSetting = Get-Content $envFilePath |
        Where-Object { $_ -match "^\s*PYTHONDONTWRITEBYTECODE=" } |
        Select-Object -First 1

    if ($bytecodeSetting) {
        $env:PYTHONDONTWRITEBYTECODE = ($bytecodeSetting -split "=", 2)[1].Trim()
    }
}

if (-not $env:PYTHONDONTWRITEBYTECODE) {
    $env:PYTHONDONTWRITEBYTECODE = "1"
}

& python -m app.main @args
exit $LASTEXITCODE
