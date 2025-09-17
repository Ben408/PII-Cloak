@echo off
REM Cloak & Style PII Data Scrubber - Package Builder
REM Builds both User and Developer distribution packages

echo ========================================
echo    Cloak & Style Package Builder
echo    Building Distribution Packages
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
echo Checking PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if %errorLevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if %errorLevel% neq 0 (
        echo ERROR: Failed to install PyInstaller.
        pause
        exit /b 1
    )
) else (
    echo PyInstaller is already installed.
)

REM Check if all required packages are installed
echo Checking dependencies...
python -c "import torch, transformers, huggingface_hub, openpyxl, docx, pptx, fitz, chardet, psutil, PySide6" >nul 2>&1
if %errorLevel% neq 0 (
    echo Some required packages are missing. Installing requirements...
    pip install -r requirements.txt
    REM Don't exit on pip warnings, only on actual failures
    python -c "import torch, transformers, huggingface_hub, openpyxl, docx, pptx, fitz, chardet, psutil, PySide6" >nul 2>&1
    if %errorLevel% neq 0 (
        echo ERROR: Critical dependencies are still missing after installation.
        pause
        exit /b 1
    )
) else (
    echo All dependencies are installed.
)

REM Run tests before building (skip if tests fail)
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
echo    Building Distribution Packages
echo ========================================
echo.

REM Create user package
echo Building User Package...
if not exist "dist\user" mkdir "dist\user"

REM Copy files to user package
copy "dist\cloak_and_style.exe" "dist\user\" >nul 2>&1
copy "dist\user\install.bat" "dist\user\" >nul 2>&1
copy "dist\user\README.md" "dist\user\" >nul 2>&1
copy "dist\user\LICENSE" "dist\user\" >nul 2>&1

REM Create user package ZIP
echo Creating User Package ZIP...
powershell -Command "Compress-Archive -Path 'dist\user\*' -DestinationPath 'CloakAndStyle-User-v1.0.0-Windows.zip' -Force"

if %errorLevel% neq 0 (
    echo ERROR: Failed to create user package ZIP.
    pause
    exit /b 1
)

REM Create developer package
echo Building Developer Package...
if not exist "dist\developer" mkdir "dist\developer"

REM Copy source files to developer package
echo Copying source files...
xcopy /E /I /Y core "dist\developer\core\" >nul 2>&1
xcopy /E /I /Y pii-mask "dist\developer\pii-mask\" >nul 2>&1
xcopy /E /I /Y test "dist\developer\test\" >nul 2>&1

REM Copy configuration files
copy "cloak_and_style_ui.py" "dist\developer\" >nul 2>&1
copy "requirements.txt" "dist\developer\" >nul 2>&1
copy "README.md" "dist\developer\" >nul 2>&1
copy "CONTRIBUTING.md" "dist\developer\" >nul 2>&1
copy "CODE_OF_CONDUCT.md" "dist\developer\" >nul 2>&1
copy "LICENSE" "dist\developer\" >nul 2>&1
copy ".gitignore" "dist\developer\" >nul 2>&1
copy "build.bat" "dist\developer\" >nul 2>&1
copy "cloak_and_style.spec" "dist\developer\" >nul 2>&1
copy "version_info.txt" "dist\developer\" >nul 2>&1

REM Create developer package ZIP
echo Creating Developer Package ZIP...
powershell -Command "Compress-Archive -Path 'dist\developer\*' -DestinationPath 'CloakAndStyle-Developer-v1.0.0-Windows.zip' -Force"

if %errorLevel% neq 0 (
    echo ERROR: Failed to create developer package ZIP.
    pause
    exit /b 1
)

REM Get package sizes
for %%A in ("CloakAndStyle-User-v1.0.0-Windows.zip") do set user_size=%%~zA
for %%A in ("CloakAndStyle-Developer-v1.0.0-Windows.zip") do set dev_size=%%~zA
set /a user_size_mb=%user_size%/1024/1024
set /a dev_size_mb=%dev_size%/1024/1024

echo.
echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Executable created: dist\cloak_and_style.exe (%size_mb% MB)
echo.
echo Distribution Packages:
echo - User Package: CloakAndStyle-User-v1.0.0-Windows.zip (%user_size_mb% MB)
echo - Developer Package: CloakAndStyle-Developer-v1.0.0-Windows.zip (%dev_size_mb% MB)
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
echo    Package Contents
echo ========================================
echo.
echo User Package (CloakAndStyle-User-v1.0.0-Windows.zip):
echo - cloak_and_style.exe (executable)
echo - install.bat (installation script)
echo - README.md (user documentation)
echo - LICENSE (MIT license)
echo.
echo Developer Package (CloakAndStyle-Developer-v1.0.0-Windows.zip):
echo - Complete source code (core/, pii-mask/, test/)
echo - All configuration files
echo - Development tools and scripts
echo - Comprehensive documentation
echo.

echo ========================================
echo    Next Steps
echo ========================================
echo.
echo 1. Test the user package on a clean system
echo 2. Verify the developer package contains all source files
echo 3. Upload packages to GitHub releases
echo 4. Update documentation and release notes
echo.
echo Ready for distribution!
echo.
pause
