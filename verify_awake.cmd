@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title awake/world - Verify Build 0.4.1
where py >nul 2>nul
if %ERRORLEVEL%==0 (
    py -3 "%~dp0launch_awake.py" --verify-only
) else (
    python "%~dp0launch_awake.py" --verify-only
)
set "AWAKE_EXIT=%ERRORLEVEL%"
echo.
if "%AWAKE_EXIT%"=="0" (
    echo [awake/world] Build verification completed successfully.
) else (
    echo [awake/world] Build verification failed with exit code %AWAKE_EXIT%.
)
pause
exit /b %AWAKE_EXIT%
