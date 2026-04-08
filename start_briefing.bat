@echo off
setlocal
cd /d "%~dp0"
set "PORT=8765"

where py >nul 2>&1
if %errorlevel%==0 (
  py scripts\fetch_rss.py >nul 2>&1
  py scripts\fetch_goes_page.py >nul 2>&1
  start "Fire Weather Briefing Server" /min py -m http.server %PORT% >nul 2>&1
  start "" "http://127.0.0.1:%PORT%/dashboard/index.html"
  exit /b 0
)

where python >nul 2>&1
if %errorlevel%==0 (
  python scripts\fetch_rss.py >nul 2>&1
  python scripts\fetch_goes_page.py >nul 2>&1
  start "Fire Weather Briefing Server" /min python -m http.server %PORT% >nul 2>&1
  start "" "http://127.0.0.1:%PORT%/dashboard/index.html"
  exit /b 0
)

start "" "%CD%\dashboard\index.html"
exit /b 0
