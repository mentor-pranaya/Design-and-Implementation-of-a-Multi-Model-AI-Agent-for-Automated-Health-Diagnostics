@echo off
title INBLOODO AGENT - Always On Server
cls

:START
echo.
echo -------------------------------------------------------------------
echo 🩺 Starting INBLOODO AGENT in ALWAYS ON mode...
echo 📅 %date% %time%
echo -------------------------------------------------------------------
echo.

REM Check/Create Virtual Environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate Virtual Environment
call venv\Scripts\activate.bat

REM Check dependencies
pip install -r requirements.txt > nul 2>&1

REM Run the server
echo 🚀 Server execution started.
echo ⚠️  To stop the server, verify you want to quit by pressing Ctrl+C twice.
echo.
python main.py

REM If we get here, the server crashed or stopped
echo.
echo ⚠️  Server stopped or crashed!
echo 🔄 Restarting in 5 seconds...
timeout /t 5 /nobreak > nul
goto START
