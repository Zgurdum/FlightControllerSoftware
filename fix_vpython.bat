@echo off
REM Fix script for VPython 3D visualization
REM Resolves common installation issues with vpython

echo ========================================
echo F722 Flight Controller - VPython Fix
echo ========================================
echo.
echo This will install dependencies for 3D visualization
echo.

REM Ensure we're in the script's directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/3] Updating pip...
python -m pip install --upgrade pip -q

echo [2/3] Installing build tools...
python -m pip install -q setuptools wheel --upgrade

echo [3/3] Installing vpython...
python -m pip install -q vpython --upgrade

echo.
echo Testing vpython import...
python -c "import vpython; print('✓ VPython is now installed and working!')" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ✗ VPython installation may have failed.
    echo Try these troubleshooting steps:
    echo.
    echo 1. Close all Python programs and IDEs
    echo 2. Open Command Prompt as Administrator
    echo 3. Run: python -m pip install --force-reinstall vpython
    echo.
)

echo.
echo Next, run:
echo   - run.bat     (to launch the full GUI)
echo   - test.bat    (to test the connection first)
echo.
pause
