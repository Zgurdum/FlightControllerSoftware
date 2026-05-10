@echo off
REM F722 Flight Controller - Installer and Launcher

echo ========================================
echo F722 Flight Controller Software Setup
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from: https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo.
echo [1/3] Installing dependencies...
pip install -q pyserial
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies
    pause
    exit /b 1
)
echo OK

echo.
echo [2/3] Running connection test...
python test_connection.py
if %ERRORLEVEL% NEQ 0 (
    echo Connection test failed
    pause
    exit /b 1
)

echo.
echo [3/3] Launching F722 Flight Controller GUI...
python src\gui_main.py

pause
