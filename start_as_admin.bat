@echo off
title SSD Firmware Studio Pro (Administrator)
cd /d "%~dp0"
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with Administrator privileges...
    python app.py
) else (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python app.py' -Verb RunAs"
)
