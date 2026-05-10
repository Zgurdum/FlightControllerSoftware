@echo off
REM Test F722 Flight Controller Connection
REM Run this FIRST to verify your F722 is working before launching the full GUI

setlocal enabledelayedexpansion

REM Ensure we're in the script's directory
cd /d "%~dp0"

echo ========================================
echo F722 Flight Controller - Connection Test
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check dependencies
echo [1/3] Checking dependencies...
python -m pip install -q setuptools wheel --upgrade >nul 2>&1

python -m pip show pyserial >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Installing pyserial...
    python -m pip install -q pyserial
    if !ERRORLEVEL! NEQ 0 (
        echo Failed to install pyserial
        pause
        exit /b 1
    )
)

python -m pip show vpython >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo Installing vpython...
    python -m pip install -q vpython
    if !ERRORLEVEL! NEQ 0 (
        echo Failed to install vpython (3D visualization will be disabled)
        REM Don't exit, vpython is optional
    )
)
echo OK

echo.
echo [2/3] Running connection test...
echo This will check if your F722 is properly connected and communicating
echo.
python test_connection.py

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo Connection test FAILED
    echo Check troubleshooting in INSTALLATION.md
    pause
    exit /b 1
)

echo.
echo [3/3] Success!
echo You can now run: python src\gui_main.py
echo Or double-click run.bat to launch the full GUI
echo.

pause
