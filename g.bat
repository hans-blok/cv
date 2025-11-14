@echo off
REM Generate CV HTML from source files
REM Usage: g or g.bat
python "%~dp0generate_site.py"
if %errorlevel% equ 0 (
    echo.
    echo ✓ CV generated successfully: cv.html
) else (
    echo.
    echo ✗ Error generating CV
    exit /b %errorlevel%
)
pause