@echo off
title SSD Firmware Studio Pro v1.0.1
cd /d "%~dp0"

set "PY_EXE=python"
where python >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
    "%PY_EXE%" app.py
) else (
    echo Requesting Administrator privileges (required for physical disk probes)...
    powershell -NoProfile -Command "Start-Process cmd -ArgumentList '/c cd /d \"\"%~dp0\"\" && \"\"%PY_EXE%\"\" app.py' -Verb RunAs"
)
