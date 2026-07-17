@echo off
setlocal

set VENV_PY=%~dp0.venv\Scripts\python.exe
if not exist "%VENV_PY%" (
    echo Virtual environment not found at .venv - run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    exit /b 1
)

"%VENV_PY%" -m mkdocs serve
