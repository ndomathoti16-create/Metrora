@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Metrora could not find its local Python environment.
    echo Create it first with: python -m venv .venv
    echo Then install the project dependencies and run this file again.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting Metrora at http://localhost:8502
echo Keep this window open while you test. Press Ctrl+C here when you are finished.
echo.

".venv\Scripts\python.exe" -m streamlit run app.py --server.port 8502 --server.headless=true

endlocal
