@echo off
REM ╔════════════════════════════════════════════════════════════════╗
REM ║           ⚡ PYTHON INSTALLATION REQUIRED ⚡                   ║
REM ║                                                                ║
REM ║  Your server won't run without Python                         ║
REM ║  This script helps you install it                             ║
REM ║                                                                ║
REM ╚════════════════════════════════════════════════════════════════╝

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                  🚨 PYTHON NOT FOUND 🚨                       ║
echo ║                                                                ║
echo ║  The server requires Python to run                            ║
echo ║  Your system does NOT have Python installed                   ║
echo ║                                                                ║
echo ║  THREE QUICK OPTIONS:                                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo OPTION 1: Download & Install Python (RECOMMENDED)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1. Go to: https://www.python.org/downloads/
echo.
echo   2. Click "Download Python 3.x.x" (yellow button)
echo.
echo   3. Run the installer and IMPORTANT:
echo      ✓ CHECK "Add Python to PATH"
echo      ✓ CHECK "Install pip"
echo      ✓ Click "Install Now"
echo.
echo   4. Restart your computer
echo.
echo   5. Come back and run: setup_and_start.bat
echo.
echo.
echo OPTION 2: Use Microsoft Store Python (FAST)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   1. Open PowerShell or cmd
echo.
echo   2. Copy and paste this command:
echo      winget install Python.Python.3.11
echo.
echo   3. Restart computer
echo.
echo   4. Run: setup_and_start.bat
echo.
echo.
echo OPTION 3: Use Conda/Anaconda (FOR ADVANCED USERS)
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   Download Anaconda from: https://www.anaconda.com/download
echo.
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  RECOMMENDED: Use Option 1 (python.org)                       ║
echo ║  Takes 2 minutes ~ Most compatible                            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Ask user for action
set /p action="Press ENTER to open python.org download page (then close when done and restart): "

REM Try to open browser to python.org
start https://www.python.org/downloads/

echo.
echo Please:
echo   1. Install Python from the opened page
echo   2. CHECK "Add Python to PATH" during install
echo   3. Restart your computer
echo   4. Run setup_and_start.bat again
echo.

pause
