$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw "Ambiente ainda não preparado. Execute ./scripts/setup.ps1 primeiro."
}

& $pythonPath -m nightcrows_bot

