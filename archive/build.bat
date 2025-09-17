@echo off
REM Cloak & Style PII Data Scrubber - Build Script
REM Windows Build Script for PyInstaller

echo ========================================
echo    Cloak & Style PII Data Scrubber
echo    Build Script
echo ========================================
echo.

REM Check if running in virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo WARNING: Not running in a virtual environment.
    echo It is recommended to activate a virtual environment before building.
    echo.
    pause
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: PyInstaller is not installed.
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

REM Check if all required packages are installed
echo Checking dependencies...
python -c "import torch, transformers, huggingface_hub, openpyxl, docx, pptx, fitz, chardet, psutil, PySide6" >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Some required packages are missing.
    echo Installing requirements...
    pip install -r requirements.txt
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install requirements.
        pause
        exit /b 1
    )
)

REM Clean previous builds
echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

REM Run tests before building
echo.
echo Running tests...
python -m pytest test/ -v --tb=short
if %errorLevel% neq 0 (
    echo WARNING: Some tests failed. Continue with build? (y/n)
    set /p choice=
    if /i "%choice%" neq "y" (
        echo Build cancelled.
        pause
        exit /b 1
    )
)

REM Build the executable
echo.
echo Building executable...
echo This may take several minutes...
echo.

pyinstaller --clean --noconfirm cloak_and_style.spec

if %errorLevel% neq 0 (
    echo ERROR: Build failed.
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\cloak_and_style.exe" (
    echo ERROR: Executable was not created.
    pause
    exit /b 1
)

REM Get executable size
for %%A in ("dist\cloak_and_style.exe") do set size=%%~zA
set /a size_mb=%size%/1024/1024

echo.
echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Executable created: dist\cloak_and_style.exe
echo Size: %size_mb% MB
echo.

REM Test the executable
echo Testing executable...
echo.
dist\cloak_and_style.exe --help >nul 2>&1
if %errorLevel% equ 0 (
    echo ✅ Executable test passed
) else (
    echo ⚠️ Executable test failed (this may be normal for GUI apps)
)

echo.
echo ========================================
echo    Next Steps
echo ========================================
echo.
echo 1. Test the executable: dist\cloak_and_style.exe
echo 2. Build distribution packages: dist\build_packages.bat
echo 3. Test installation on clean system
echo 4. Create release package
echo.

REM Create basic release package
echo Creating basic release package...
if not exist "release" mkdir "release"

REM Copy files to release directory
copy "dist\cloak_and_style.exe" "release\" >nul 2>&1
copy "install.bat" "release\" >nul 2>&1
copy "README.md" "release\" >nul 2>&1
copy "LICENSE" "release\" >nul 2>&1

REM Create ZIP file
echo Creating ZIP package...
powershell -Command "Compress-Archive -Path 'release\*' -DestinationPath 'CloakAndStyle-v1.0.0-Windows.zip' -Force"

echo.
echo Basic release package created: CloakAndStyle-v1.0.0-Windows.zip
echo.

echo ========================================
echo    Build Process Complete!
echo ========================================
echo.
echo Files created:
echo - dist\cloak_and_style.exe (executable)
echo - CloakAndStyle-v1.0.0-Windows.zip (basic release package)
echo.
echo For full distribution packages, run:
echo dist\build_packages.bat
echo.
echo This will create:
echo - User Package (CloakAndStyle-User-v1.0.0-Windows.zip)
echo - Developer Package (CloakAndStyle-Developer-v1.0.0-Windows.zip)
echo.
echo Ready for distribution!
echo.
pause
