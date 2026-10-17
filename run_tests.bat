@echo off
title MotionGuard Test Suite
echo =======================================================
echo          MotionGuard Automated Pytest Suite
echo =======================================================
echo.
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    echo Using local .venv environment...
    .venv\Scripts\python.exe -m pytest
    goto end
)

if exist "venv\Scripts\python.exe" (
    echo Using venv environment...
    venv\Scripts\python.exe -m pytest
    goto end
)

if exist "C:\Users\visha\MotionGuard\.venv\Scripts\python.exe" (
    echo Using MotionGuard venv environment...
    "C:\Users\visha\MotionGuard\.venv\Scripts\python.exe" -m pytest
    goto end
)

echo Checking system Python with pytest...
python -m pytest

:end
pause
