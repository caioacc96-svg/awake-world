@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title awake/world - Build 0.4.1

echo [awake/world] Build 0.4.1 - Living City

echo [awake/world] locating Python 3...
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 "%~dp0launch_awake.py"
    set "AWAKE_EXIT=%ERRORLEVEL%"
    goto :done
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python "%~dp0launch_awake.py"
    set "AWAKE_EXIT=%ERRORLEVEL%"
    goto :done
)

echo.
echo [awake/world] ERROR: Python 3.11+ was not found.
echo Install Python 3.11 or newer, enable the Python launcher/PATH option, then run this file again.
set "AWAKE_EXIT=9009"

:done
if not "%AWAKE_EXIT%"=="0" (
    echo.
    echo [awake/world] Launch stopped with exit code %AWAKE_EXIT%.
    echo The terminal above contains the exact failing stage.
    pause
)
exit /b %AWAKE_EXIT%
