# Full local build pipeline for the MkDocs-based CV site.
# Order matters: PDF generation needs a first `mkdocs build` pass to read from,
# then a second pass so the freshly generated PDF/DOCX are copied into site/ as static assets.
#
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found at .venv - run: python -m venv .venv; .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host "1/4 Building site (pass 1, for PDF source)..." -ForegroundColor Cyan
& $venvPython -m mkdocs build --strict
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "2/4 Generating PDF..." -ForegroundColor Cyan
& $venvPython generate_pdf.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "3/4 Generating DOCX..." -ForegroundColor Cyan
& $venvPython generate_docx.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "4/4 Building site (pass 2, includes PDF/DOCX as static assets)..." -ForegroundColor Cyan
& $venvPython -m mkdocs build --strict
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Build complete. Preview with: .venv\Scripts\python -m mkdocs serve" -ForegroundColor Green
Write-Host "Publish with:                .venv\Scripts\python -m mkdocs gh-deploy" -ForegroundColor Green
