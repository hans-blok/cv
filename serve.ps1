# Local MkDocs preview server with live-reload.
# Usage: .\serve.ps1

$ErrorActionPreference = "Stop"
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found at .venv - run: python -m venv .venv; .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

& $venvPython -m mkdocs serve
