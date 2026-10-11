@echo off
:: ════════════════════════════════════════════════════════
::   NutriBot — IBM Granite Nutrition Agentic AI Launcher
::   Version 1.0
:: ════════════════════════════════════════════════════════

title NutriBot — IBM Granite Nutrition AI

echo.
echo  ╔══════════════════════════════════════════════════════╗
echo  ║      NutriBot — IBM Granite Nutrition Agentic AI    ║
echo  ║              Powered by IBM watsonx.ai              ║
echo  ╚══════════════════════════════════════════════════════╝
echo.

:: ── Step 1: Check Python ──────────────────────────────────
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python is not installed or not in PATH.
    echo  Please install Python 3.9+ from https://python.org
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo        Found: %%i
echo.

:: ── Step 2: Navigate to project directory ─────────────────
echo [2/5] Navigating to project folder...
cd /d "%~dp0nutrition_ai"
if errorlevel 1 (
    echo  ERROR: Cannot find nutrition_ai folder.
    pause
    exit /b 1
)
echo        Location: %CD%
echo.

:: ── Step 3: Install dependencies ──────────────────────────
echo [3/5] Installing / verifying Python dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo  WARNING: Some packages may not have installed correctly.
    echo           Continuing anyway...
)
echo        Dependencies OK.
echo.

:: ── Step 4: Create .env if not present ────────────────────
echo [4/5] Checking environment configuration...
if not exist ".env" (
    copy ".env.example" ".env" >nul 2>&1
    echo        Created .env from template.
    echo        NOTE: Edit nutrition_ai\.env to add IBM watsonx.ai credentials
    echo              for full IBM Granite API access (demo mode works without them).
) else (
    echo        .env already exists.
)
echo.

:: ── Step 5: Launch the application ────────────────────────
echo [5/5] Starting NutriBot server...
echo.
echo  ┌─────────────────────────────────────────────────────┐
echo  │  Application URL : http://127.0.0.1:5000           │
echo  │  Press CTRL+C to stop the server                   │
echo  └─────────────────────────────────────────────────────┘
echo.

:: Open browser after a short delay (in background)
start /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:5000"

:: Start the Flask server (blocks until CTRL+C)
set PYTHONIOENCODING=utf-8
set FLASK_APP=app.py
python -m flask run --host=0.0.0.0 --port=5000

echo.
echo  Server stopped. Press any key to exit.
pause >nul
