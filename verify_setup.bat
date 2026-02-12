@echo off
REM ════════════════════════════════════════════════════════════════════════════
REM   FINAL VERIFICATION TEST - Run this after setup_and_start.bat completes
REM ════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo.
echo ════════════════════════════════════════════════════════════════════════════
echo                     FINAL VERIFICATION TEST
echo ════════════════════════════════════════════════════════════════════════════
echo.

REM Test 1: Check Python installation
echo [Test 1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python found
    python --version
) else (
    echo ❌ Python NOT found
    echo    Fix: Install Python from https://www.python.org/downloads/
    echo    Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)

echo.

REM Test 2: Check pip installation
echo [Test 2/5] Checking pip installation...
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip found
    pip --version
) else (
    echo ❌ pip NOT found
    echo    This usually means Python wasn't installed correctly
    pause
    exit /b 1
)

echo.

REM Test 3: Check virtual environment
echo [Test 3/5] Checking virtual environment...
if exist venv (
    echo ✅ Virtual environment directory found
) else (
    echo ⚠️  Virtual environment not found
    echo    It will be created when you run: setup_and_start.bat
)

echo.

REM Test 4: Check key dependencies (if venv exists)
echo [Test 4/5] Checking dependencies...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python -c "import fastapi; import uvicorn; import sqlalchemy" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Key dependencies installed
        pip list | findstr /i "fastapi uvicorn sqlalchemy" | head -3
    ) else (
        echo ❌ Dependencies not installed
        echo    Run: setup_and_start.bat
        pause
        exit /b 1
    )
) else (
    echo ⚠️  Virtual environment not activated yet
    echo    Run: setup_and_start.bat to create and activate it
)

echo.

REM Test 5: Check project structure
echo [Test 5/5] Checking project structure...
set missing_files=0

if not exist src\api.py (
    echo ❌ Missing: src\api.py
    set missing_files=1
) else (
    echo ✅ Found: src\api.py
)

if not exist src\main.py (
    echo ❌ Missing: src\main.py
    set missing_files=1
) else (
    echo ✅ Found: src\main.py
)

if not exist requirements.txt (
    echo ❌ Missing: requirements.txt
    set missing_files=1
) else (
    echo ✅ Found: requirements.txt
)

echo.

REM Print summary
echo ════════════════════════════════════════════════════════════════════════════
echo                           VERIFICATION SUMMARY
echo ════════════════════════════════════════════════════════════════════════════
echo.

if %missing_files% equ 0 (
    echo ✅ All checks passed!
    echo.
    echo Your system is ready. Next steps:
    echo.
    echo 1. Make sure you've run: setup_and_start.bat
    echo.
    echo 2. When you see "Uvicorn running on http://0.0.0.0:10000"
    echo    the server is ready!
    echo.
    echo 3. Open your browser and go to:
    echo    http://localhost:10000
    echo.
    echo 4. You should see the INBLOODO AGENT website ✅
    echo.
    echo That's it! Your AI health diagnostics system is working!
    echo.
) else (
    echo ❌ Some checks failed
    echo.
    echo Check the errors above and fix them.
    echo Usually this means:
    echo   • Python not installed
    echo   • Dependencies not installed yet
    echo   • Files missing from project folder
    echo.
)

echo.
echo Need help? Read these guides:
echo   • JUST_DO_THIS_NOW.txt (quickest)
echo   • COMPLETE_SERVER_FIX_GUIDE.md (detailed)
echo   • Run: diagnose.bat (automatic diagnostics)
echo.

pause
