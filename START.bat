@echo off
title Seed Sensei - Precision Agriculture Prototype
color 0A

echo ==============================================================================
echo                SEED SENSEI - OILSEED PRECISION AGRICULTURE SYSTEM
echo                      Target Crop: Groundnut (Peanut)
echo ==============================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.9+ and ensure "Add Python to PATH" is checked.
    echo.
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import pandas, sklearn, joblib" >nul 2>nul
if %errorlevel% neq 0 (
    echo [NOTICE] Installing required packages from requirements.txt...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo Starting Seed Sensei...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [NOTICE] Seed Sensei closed with error code %errorlevel%.
    pause
)
