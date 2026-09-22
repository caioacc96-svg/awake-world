$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & py -3 "$PSScriptRoot\launch_awake.py"
    exit $LASTEXITCODE
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & python "$PSScriptRoot\launch_awake.py"
    exit $LASTEXITCODE
}

throw "Python 3.11+ was not found. Use RUN_AWAKE_WORLD.cmd after installing Python."
