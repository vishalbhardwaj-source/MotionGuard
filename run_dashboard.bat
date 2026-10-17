@echo off
title MotionGuard Dashboard
echo =======================================================
echo          MotionGuard Road-Safety Dashboard
echo =======================================================
echo.
cd /d "%~dp0"

if exist ".venv\Scripts\streamlit.exe" (
    echo Using local .venv environment...
    .venv\Scripts\streamlit.exe run app.py
    goto end
)

if exist "venv\Scripts\streamlit.exe" (
    echo Using venv environment...
    venv\Scripts\streamlit.exe run app.py
    goto end
)

if exist "C:\Users\visha\MotionGuard\.venv\Scripts\streamlit.exe" (
    echo Using MotionGuard venv environment...
    "C:\Users\visha\MotionGuard\.venv\Scripts\streamlit.exe" run app.py
    goto end
)

echo Checking system Python with Streamlit...
python -m streamlit run app.py

:end
pause
