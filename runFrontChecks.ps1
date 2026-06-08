$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
& python (Join-Path $projectRoot "scripts\verifyFront.py") @args
exit $LASTEXITCODE
