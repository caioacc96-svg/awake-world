$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = $PSScriptRoot

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Virtual environment not found. Run start_awake.ps1 once first." -ForegroundColor Yellow
    exit 2
}

$env:QT_QPA_PLATFORM = "offscreen"
& $python tools\smoke_test.py
exit $LASTEXITCODE
