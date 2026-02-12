@echo off
REM Quick Enable Enhanced Login System
REM This script installs dependencies and enables the enhanced login page

echo ========================================
echo  INBLOODO Enhanced Login Setup
echo ========================================
echo.

echo Step 1: Installing authentication packages...
pip install passlib[bcrypt] pyjwt email-validator
echo.

echo Step 2: Backing up original login page...
cd templates
if exist login.html (
    copy login.html login_original_backup.html
    echo ✓ Original login.html backed up to login_original_backup.html
)
echo.

echo Step 3: Enabling enhanced login page...
if exist login_enhanced.html (
    copy /Y login_enhanced.html login.html
    echo ✓ Enhanced login page activated!
) else (
    echo ✗ Error: login_enhanced.html not found
    cd ..
    pause
    exit /b 1
)
cd ..
echo.

echo ========================================
echo  Setup Complete! ✓
echo ========================================
echo.
echo The enhanced login system is now active with:
echo   • Login + Registration tabs
echo   • Password hashing (bcrypt)
echo   • JWT token authentication
echo   • 4 default test users
echo.
echo Test Credentials:
echo   - admin / admin123
echo   - doctor / doctor123
echo   - patient / patient123
echo   - test / secret
echo.
echo Starting server in 5 seconds...
echo Press Ctrl+C to cancel, or wait...
timeout /t 5

echo.
echo Starting INBLOODO Agent...
python launch_server.py

pause
