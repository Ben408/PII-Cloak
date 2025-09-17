# Cloak & Style PII Data Scrubber Startup Script
# Ensures correct Python version and virtual environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cloak & Style PII Data Scrubber" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.11 is available
Write-Host "Checking Python 3.11 availability..." -ForegroundColor Yellow
try {
    $pythonVersion = py -3.11 --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.11 not found"
    }
    Write-Host "Python 3.11 found ✓" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python 3.11 is not installed or not available" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "cloak_venv")) {
    Write-Host "Creating virtual environment with Python 3.11..." -ForegroundColor Yellow
    try {
        py -3.11 -m venv cloak_venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Host "Virtual environment created ✓" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & "cloak_venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to activate virtual environment"
    }
} catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import PySide6" 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "PySide6 not found"
    }
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
        Write-Host "Dependencies installed ✓" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host ""
}

# Verify Python version in virtual environment
Write-Host "Verifying Python version..." -ForegroundColor Yellow
python --version
Write-Host ""

# Start the application
Write-Host "Starting Cloak & Style PII Data Scrubber..." -ForegroundColor Green
Write-Host ""
try {
    python cloak_and_style_ui_new.py
} catch {
    Write-Host ""
    Write-Host "Application exited with an error" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
