@echo off
echo ========================================
echo Cloak & Style PII Data Scrubber
echo ========================================
echo.

REM Check if Python 3.11 is available
echo Checking Python 3.11 availability...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 is not installed or not available
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python 3.11 found ✓
echo.

REM Check if virtual environment exists
if not exist "cloak_venv" (
    echo Creating virtual environment with Python 3.11...
    py -3.11 -m venv cloak_venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created ✓
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call cloak_venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed ✓
    echo.
)

REM Verify Python version in virtual environment
echo Verifying Python version...
python --version
echo.

REM Start the application
echo Starting Cloak & Style PII Data Scrubber...
echo.
python cloak_and_style_ui_new.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
