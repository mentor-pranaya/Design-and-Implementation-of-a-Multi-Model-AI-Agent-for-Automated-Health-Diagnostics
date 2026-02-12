@echo off
REM ╔════════════════════════════════════════════════════════════════╗
REM ║       🔍 INBLOODO AGENT - QUICK DIAGNOSTIC TOOL 🔍           ║
REM ║                                                                ║
REM ║  This script checks why the site can't be reached and        ║
REM ║  provides solutions                                           ║
REM ║                                                                ║
REM ╚════════════════════════════════════════════════════════════════╝

echo.
echo 🔍 DIAGNOSTIC CHECK STARTING...
echo.

REM Check 1: Python Installation
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [1] Checking Python Installation...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ PROBLEM: Python is NOT installed or NOT in PATH
    echo.
    echo 🔧 SOLUTION:
    echo 1. Install Python from: https://www.python.org/downloads/
    echo 2. IMPORTANT: Check "Add Python to PATH" during installation
    echo 3. Restart your computer
    echo 4. Try again
    echo.
) else (
    python --version
    echo ✅ Python installed correctly
)
echo.

REM Check 2: Requirements installed
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [2] Checking Dependencies...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not exist "venv" (
    echo ⚠️  Virtual environment NOT created yet
    echo.
    echo 🔧 SOLUTION: Run this first:
    echo    setup_and_start.bat
    echo.
) else (
    echo ✅ Virtual environment exists
    
    REM Check if requirements installed
    venv\Scripts\python -c "import fastapi" >nul 2>&1
    if errorlevel 1 (
        echo ❌ Dependencies NOT installed
        echo.
        echo 🔧 SOLUTION:
        echo    setup_and_start.bat
        echo.
    ) else (
        echo ✅ Core dependencies installed
    )
)
echo.

REM Check 3: Required files
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [3] Checking Required Files...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if not exist "src\api.py" (
    echo ❌ Missing: src\api.py
) else (
    echo ✅ Found: src\api.py
)

if not exist "src\api_optimized.py" (
    echo ⚠️  Missing: src\api_optimized.py (optional, using standard)
) else (
    echo ✅ Found: src\api_optimized.py
)

if not exist "requirements.txt" (
    echo ❌ Missing: requirements.txt
) else (
    echo ✅ Found: requirements.txt
)

if not exist "run_instant.py" (
    echo ⚠️  Missing: run_instant.py (optional)
) else (
    echo ✅ Found: run_instant.py
)

echo.

REM Check 4: Port availability
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo [4] Checking if Port 10000 is available...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
netstat -ano | findstr :10000 >nul 2>&1
if errorlevel 1 (
    echo ✅ Port 10000 is available
) else (
    echo ⚠️  Port 10000 is ALREADY IN USE
    echo.
    echo This could be from:
    echo - Server already running (check if it's working!)
    echo - Another application using port 10000
    echo.
    echo Try: http://localhost:10000
    echo.
)
echo.

REM Summary and recommendations
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    RECOMMENDATIONS                             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 1️⃣  If Python NOT installed:
echo    → Install Python from https://www.python.org/downloads/
echo    → MUST check "Add Python to PATH"
echo    → Restart computer after install
echo.
echo 2️⃣  To start the server:
echo    → Run: setup_and_start.bat
echo.
echo 3️⃣  To test if server is running:
echo    → Open browser: http://localhost:10000
echo    → Or run: curl http://localhost:10000/health
echo.
echo 4️⃣  If still not working:
echo    → Check logs for errors
echo    → Try different port (edit setup_and_start.bat)
echo    → Restart computer
echo.

pause
