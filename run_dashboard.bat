@echo off
title MotionGuard AI — Road Safety & Emergency Response
echo =======================================================
echo     MotionGuard: Autonomous Incident Response AI
echo =======================================================
echo.
cd /d "%~dp0"

REM 1. Check local virtual environments
if exist ".venv\Scripts\streamlit.exe" (
    echo [OK] Using local .venv environment...
    .venv\Scripts\streamlit.exe run app.py
    goto end
)

if exist "venv\Scripts\streamlit.exe" (
    echo [OK] Using local venv environment...
    venv\Scripts\streamlit.exe run app.py
    goto end
)

if exist "%USERPROFILE%\MotionGuard\.venv\Scripts\streamlit.exe" (
    echo [OK] Using MotionGuard venv environment...
    "%USERPROFILE%\MotionGuard\.venv\Scripts\streamlit.exe" run app.py
    goto end
)

if exist "C:\Users\visha\MotionGuard\.venv\Scripts\streamlit.exe" (
    echo [OK] Using MotionGuard venv environment...
    "C:\Users\visha\MotionGuard\.venv\Scripts\streamlit.exe" run app.py
    goto end
)

REM 2. Check system Python with Streamlit module
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Running via system Python Streamlit...
    python -m streamlit run app.py
    goto end
)

py -3.12 -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [OK] Running via Python 3.12 Streamlit...
    py -3.12 -m streamlit run app.py
    goto end
)

REM 3. If Streamlit is not installed, offer quick auto-setup
echo.
echo [!] Streamlit was not found in your active Python environment.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% equ 0 (
    echo [OK] Dependencies installed successfully! Launching MotionGuard...
    python -m streamlit run app.py
) else (
    echo [ERROR] Failed to install dependencies. Please run 'pip install -r requirements.txt' manually.
)

:end
pause
