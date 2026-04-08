@echo off
setlocal
cd /d "%~dp0"

set "POWERSHELL_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
if exist "%POWERSHELL_EXE%" (
  "%POWERSHELL_EXE%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_briefing.ps1"
  exit /b %errorlevel%
)

where pwsh >nul 2>&1
if %errorlevel%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_briefing.ps1"
  exit /b %errorlevel%
)

echo PowerShell was not found. Opening the static dashboard page without the local server.
start "" "%CD%\dashboard\index.html"
exit /b 0
