@echo off
setlocal

set VENV_PY=%~dp0.venv\Scripts\python.exe
if not exist "%VENV_PY%" (
    echo Virtual environment not found at .venv - run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    exit /b 1
)

echo 1/4 Building site (pass 1, for PDF source)...
"%VENV_PY%" -m mkdocs build --strict || exit /b 1

echo 2/4 Generating PDF...
"%VENV_PY%" generate_pdf.py || exit /b 1

echo 3/4 Generating DOCX...
"%VENV_PY%" generate_docx.py || exit /b 1

echo 4/4 Building site (pass 2, includes PDF/DOCX as static assets)...
"%VENV_PY%" -m mkdocs build --strict || exit /b 1

echo.
echo Build complete. Preview with: .venv\Scripts\python -m mkdocs serve
echo Publish with:                .venv\Scripts\python -m mkdocs gh-deploy
pause
