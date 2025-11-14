# Generate CV HTML from source files
# Usage: .\g.ps1 or Set-Alias g .\g.ps1 in your PowerShell profile

python "$PSScriptRoot\generate_site.py"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ CV generated successfully: cv.html" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Error generating CV" -ForegroundColor Red
    exit $LASTEXITCODE
}
