@echo off
chcp 65001 >nul
echo ========================================
echo   HeyJarvis Development Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11+ required
    pause
    exit /b 1
)

echo [1/4] Installing Python dependencies...
pip install -e ".[dev]"

echo.
echo [2/4] Starting PostgreSQL and Redis...
docker compose up -d postgres redis

echo.
echo [3/4] Waiting for services...
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Initializing database...
python -c "from shared.database import init_db, seed_demo_data; init_db(); seed_demo_data(); print('Database ready!')"

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Start the API:
echo   uvicorn apps.api.main:app --reload
echo.
echo API docs:
echo   http://localhost:8000/docs
echo.
pause
