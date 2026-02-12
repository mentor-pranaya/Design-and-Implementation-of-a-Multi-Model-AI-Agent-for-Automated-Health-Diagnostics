@echo off
REM 🚀 Quick performance test commands for INBLOODO AGENT (Windows)

setlocal enabledelayedexpansion
set "API_KEY=your-api-key"
set "BASE_URL=http://localhost:10000"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     ⚡ INBLOODO AGENT - Performance Test Suite ⚡         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Sample blood report data
set "BLOOD_DATA={\"hemoglobin\": 14.5, \"hematocrit\": 42.3, \"rbc\": 4.8, \"wbc\": 7.2, \"platelets\": 250, \"glucose\": 95, \"creatinine\": 0.9}"

REM Test 1: Health Check
echo 🔍 Test 1: Health Check ^(verify server running^)
echo Command: curl %BASE_URL%/health
echo.
curl -s "%BASE_URL%/health"
echo.
echo.

REM Test 2: First Request ^(builds cache^)
echo 🔄 Test 2: First Analysis ^(builds cache, should be ~2-5s^)
echo Command: curl -X POST "%BASE_URL%/analyze-report/" ...
echo.
for /f %%A in ('powershell -Command "Get-Date -UFormat %%s"') do set START=%%A
curl -s -X POST "%BASE_URL%/analyze-report/" ^
  -H "X-API-Key: %API_KEY%" ^
  -H "Content-Type: application/json" ^
  -d "%BLOOD_DATA%"
for /f %%A in ('powershell -Command "Get-Date -UFormat %%s"') do set END=%%A
set /a ELAPSED=%END%-%START%
echo.
echo Response Time: %ELAPSED% seconds
echo.
echo.

REM Test 3: Cached Request ^(instant!^)
echo ⚡ Test 3: Cached Request ^(same data, should be instant!^)
echo Command: curl -X POST "%BASE_URL%/analyze-report/" ^(identical data^)
echo.
for /f %%A in ('powershell -Command "Get-Date -UFormat %%s"') do set START=%%A
curl -s -X POST "%BASE_URL%/analyze-report/" ^
  -H "X-API-Key: %API_KEY%" ^
  -H "Content-Type: application/json" ^
  -d "%BLOOD_DATA%"
for /f %%A in ('powershell -Command "Get-Date -UFormat %%s"') do set END=%%A
set /a ELAPSED=%END%-%START%
echo.
echo Response Time: %ELAPSED% seconds ⚡
echo.
echo.

REM Test 4: Performance Metrics
echo 📊 Test 4: Performance Metrics
echo Command: curl %BASE_URL%/api/status
echo.
curl -s "%BASE_URL%/api/status"
echo.
echo.

REM Summary
echo ╔════════════════════════════════════════════════════════════╗
echo ║                    ✅ TESTS COMPLETE ✅                   ║
echo ║                                                            ║
echo ║  What You Should See:                                     ║
echo ║  ✓ Test 1: Server status 'healthy'                       ║
echo ║  ✓ Test 2: from_cache = false, ~2-5s                    ║
echo ║  ✓ Test 3: from_cache = true, very fast ⚡              ║
echo ║  ✓ Test 4: Positive hit rate in cache_stats             ║
echo ║                                                            ║
echo ║  Expected Speed Improvement: 20-100x! 🚀                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause
