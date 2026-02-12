@echo off
REM INBLOODO AGENT Startup Script for Windows
echo 🩺 Starting INBLOODO AGENT...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Create data directories
if not exist "data\uploads" mkdir data\uploads
if not exist "src\data" mkdir src\data

REM Set environment variables
set ENVIRONMENT=production
set HOST=0.0.0.0
if "%PORT%"=="" set PORT=10000
if "%API_KEY%"=="" (
    for /f %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))"') do set API_KEY=%%i
)

echo 🔑 API Key: %API_KEY%
echo 🌐 Starting server on http://%HOST%:%PORT%
echo 📊 Health check: http://%HOST%:%PORT%/health
echo 🏠 Web interface: http://%HOST%:%PORT%
echo.
echo ⚠️  Keep this window open while the server is running
echo ⚠️  Press Ctrl+C to stop the server
echo.

REM Start the application
python main.py

pause