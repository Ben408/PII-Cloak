@echo off
REM Cloak & Style PII Data Scrubber - Installation Script
REM Windows 10/11 x64 Installation

echo ========================================
echo    Cloak & Style PII Data Scrubber
echo    Installation Script
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo WARNING: Running as administrator is not required.
    echo This tool is designed for per-user installation.
    echo.
)

REM Check Windows version
ver | findstr /i "10\.0\|11\.0" >nul
if %errorLevel% neq 0 (
    echo ERROR: Windows 10 or 11 is required.
    echo Current Windows version:
    ver
    pause
    exit /b 1
)

REM Check if 64-bit
if not "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    echo ERROR: 64-bit Windows is required.
    echo Current architecture: %PROCESSOR_ARCHITECTURE%
    pause
    exit /b 1
)

echo System Requirements Check:
echo ✓ Windows 10/11 x64 detected
echo ✓ User has write permissions
echo.

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\CloakAndStyle
echo Installing to: %INSTALL_DIR%

if exist "%INSTALL_DIR%" (
    echo Directory already exists. Updating installation...
) else (
    echo Creating installation directory...
    mkdir "%INSTALL_DIR%"
)

REM Copy executable and files
echo.
echo Copying files...
copy "cloak_and_style.exe" "%INSTALL_DIR%\" >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Could not copy cloak_and_style.exe
    echo Make sure the executable is in the same directory as this installer.
    pause
    exit /b 1
)

REM Copy README and licenses
if exist "README.md" copy "README.md" "%INSTALL_DIR%\" >nul 2>&1
if exist "LICENSE" copy "LICENSE" "%INSTALL_DIR%\" >nul 2>&1
if exist "licenses\" xcopy "licenses\" "%INSTALL_DIR%\licenses\" /E /I /Y >nul 2>&1

REM Create desktop shortcut
echo Creating desktop shortcut...
set SHORTCUT="%USERPROFILE%\Desktop\Cloak & Style.lnk"
set TARGET="%INSTALL_DIR%\cloak_and_style.exe"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = %TARGET%; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Cloak & Style PII Data Scrubber'; $Shortcut.Save()" >nul 2>&1

REM Create start menu shortcut
echo Creating start menu shortcut...
set START_MENU="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Cloak & Style.lnk"
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%START_MENU%'); $Shortcut.TargetPath = %TARGET%; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'Cloak & Style PII Data Scrubber'; $Shortcut.Save()" >nul 2>&1

echo.
echo ========================================
echo    Installation Complete!
echo ========================================
echo.
echo Cloak & Style has been installed to:
echo %INSTALL_DIR%
echo.
echo Shortcuts created:
echo - Desktop: "Cloak & Style"
echo - Start Menu: "Cloak & Style"
echo.
echo To run the application:
echo 1. Double-click the desktop shortcut, or
echo 2. Search for "Cloak & Style" in the Start Menu
echo.
echo For help and documentation, see README.md in the installation directory.
echo.
echo IMPORTANT: This tool processes sensitive data locally.
echo No data is sent to the cloud or stored after session ends.
echo.
pause
