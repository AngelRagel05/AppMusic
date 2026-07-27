$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot
& npm run app @args
exit $LASTEXITCODE
