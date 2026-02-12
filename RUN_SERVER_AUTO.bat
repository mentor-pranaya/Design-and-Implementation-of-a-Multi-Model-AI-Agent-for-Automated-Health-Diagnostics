@echo off
REM ════════════════════════════════════════════════════════════════════
REM  INBLOODO AGENT - Automatic Setup & Launch Script
REM  Python location: C:\Users\gurus\AppData\Local\Programs\Python\Python310
REM ════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Set Python path
set PYTHON=C:\Users\gurus\AppData\Local\Programs\Python\Python310\python.exe

REM Check if Python exists
if not exist "!PYTHON!" (
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo ERROR: Python not found at expected location
    echo Path: !PYTHON!
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════════
echo  INBLOODO AGENT - Automatic Setup
echo ════════════════════════════════════════════════════════════════════
echo.

REM Display Python version
echo [1/6] Verifying Python installation...
!PYTHON! --version
echo ✅ Python found
echo.

REM Check/create venv
echo [2/6] Setting up virtual environment...
if not exist venv (
    echo Creating venv folder...
    !PYTHON! -m venv venv
    if !errorlevel! neq 0 (
        echo ❌ Failed to create venv
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Upgrade pip
echo [3/6] Upgrading pip...
call venv\Scripts\python.exe -m pip install --upgrade pip --quiet
echo ✅ pip upgraded
echo.

REM Install core packages
echo [4/6] Installing core packages (fastapi, uvicorn)...
call venv\Scripts\python.exe -m pip install fastapi uvicorn --quiet --no-cache-dir
if !errorlevel! neq 0 (
    echo ⚠ Warning: Some packages may have failed
    echo Attempting to continue...
)
echo ✅ Core packages installed
echo.

REM Install all requirements
echo [5/6] Installing full requirements...
if exist requirements.txt (
    call venv\Scripts\python.exe -m pip install -r requirements.txt --quiet --no-cache-dir
    if !errorlevel! neq 0 (
        echo ⚠ Warning: Some requirements may have failed
    )
)
echo ✅ Requirements processed
echo.

REM Start server
echo [6/6] Starting server...
echo.
echo ════════════════════════════════════════════════════════════════════
echo  ✅ SERVER STARTING
echo ════════════════════════════════════════════════════════════════════
echo.
echo 🌐 Access your site at: http://localhost:10000
echo 📚 API Docs at: http://localhost:10000/docs
echo ❤️  Health Check: http://localhost:10000/health
echo.
echo    Press Ctrl+C in this window to stop the server
echo.
echo ════════════════════════════════════════════════════════════════════
echo.

REM Run server
call venv\Scripts\python.exe -m uvicorn src.api:app --host 0.0.0.0 --port 10000 --reload

if !errorlevel! neq 0 (
    echo.
    echo ❌ Server failed to start
    echo.
    echo Troubleshooting:
    echo   1. Check that all dependencies installed correctly
    echo   2. Try closing other programs using port 10000
    echo   3. Restart your computer
    echo.
    pause
)

endlocal
