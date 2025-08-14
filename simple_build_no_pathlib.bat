@echo off
REM Simple Build Script - Excluding pathlib conflict
REM Builds the executable while avoiding pathlib conflicts

echo ========================================
echo    Cloak & Style - Build (No pathlib)
echo ========================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable with explicit exclusions
echo Building executable with PyInstaller...
echo This may take several minutes...
echo.

pyinstaller --clean --noconfirm --exclude-module pathlib cloak_and_style_ui.py --onefile --windowed --name cloak_and_style

if %errorLevel% neq 0 (
    echo ERROR: PyInstaller build failed.
    echo.
    echo Trying alternative approach...
    echo.
    
    REM Try with spec file but exclude pathlib
    pyinstaller --clean --noconfirm --exclude-module pathlib cloak_and_style.spec
    
    if %errorLevel% neq 0 (
        echo ERROR: Alternative build also failed.
        echo.
        echo Manual steps to try:
        echo 1. Create a new virtual environment
        echo 2. Install only required packages
        echo 3. Run: pyinstaller cloak_and_style_ui.py --onefile
        echo.
        pause
        exit /b 1
    )
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
echo Executable created: dist\cloak_and_style.exe (%size_mb% MB)
echo.

REM Create basic user package
echo Creating basic user package...
if not exist "dist\user" mkdir "dist\user"

REM Copy files to user package
copy "dist\cloak_and_style.exe" "dist\user\" >nul 2>&1
copy "install.bat" "dist\user\" >nul 2>&1
copy "README.md" "dist\user\" >nul 2>&1
copy "LICENSE" "dist\user\" >nul 2>&1

REM Create user package ZIP
echo Creating User Package ZIP...
powershell -Command "Compress-Archive -Path 'dist\user\*' -DestinationPath 'CloakAndStyle-User-v1.0.0-Windows.zip' -Force"

if %errorLevel% neq 0 (
    echo ERROR: Failed to create user package ZIP.
    pause
    exit /b 1
)

echo.
echo User Package created: CloakAndStyle-User-v1.0.0-Windows.zip
echo.
echo Package contains:
echo - cloak_and_style.exe (executable)
echo - install.bat (installation script)
echo - README.md (documentation)
echo - LICENSE (MIT license)
echo.
echo Ready for distribution!
echo.
pause
