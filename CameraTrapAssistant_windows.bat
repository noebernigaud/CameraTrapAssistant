@echo off
title CameraTrap Assistant Installer
setlocal

:: ======================================================
:: Configuration
:: ======================================================
set "APP_NAME=CameraTrap Assistant"
set "GITHUB_REPO=noebernigaud/CameraTrapAssistant"
set "GITHUB_API_URL=https://api.github.com/repos/%GITHUB_REPO%/releases/latest"
set "APP_DIR=%~dp0"
set "CTA_DIR=%APP_DIR%CameraTrapAssistant"
set "VERSION_JSON=%CTA_DIR%\version.json"
set "REQUIREMENTS_FILE=%CTA_DIR%\requirements.txt"
set "MAIN_PY=%CTA_DIR%\src\main.py"
set "TEMP_DIR=%TEMP%\CameraTrapAssistant_Update"
set "INSTALLER_DIR=%APP_DIR%installer"
set "LOG_FILE=%INSTALLER_DIR%\CameraTrapAssistant_installer.log"

:: Create installer directory if it doesn't exist
if not exist "%INSTALLER_DIR%" mkdir "%INSTALLER_DIR%"

:: Initialize log
echo ======================================================== >> "%LOG_FILE%"
echo CameraTrap Assistant Installer - %date% %time% >> "%LOG_FILE%"
echo ======================================================== >> "%LOG_FILE%"

:: Read current version if available
set "CURRENT_VERSION=0.0.0"
if not exist "%CTA_DIR%" (
    echo CameraTrapAssistant folder not found. This appears to be a first-time installation.
    echo Current Version: Not installed >> "%LOG_FILE%"
    echo Forcing update check... >> "%LOG_FILE%"
    set "FORCE_UPDATE=true"
) else (
    if exist "%VERSION_JSON%" (
        :: Read version from JSON file
        powershell -Command "try { $json = Get-Content '%VERSION_JSON%' | ConvertFrom-Json; $json.version } catch { '0.0.0' }" > "%TEMP%\version_temp.txt"
        for /f "delims=" %%i in ('type "%TEMP%\version_temp.txt"') do set "CURRENT_VERSION=%%i"
        del "%TEMP%\version_temp.txt" >nul 2>&1
    ) else (
        echo Warning: version.json not found. Using default version 0.0.0 >> "%LOG_FILE%"
    )
    echo Current Version: %CURRENT_VERSION% >> "%LOG_FILE%"
)

echo ======================================================
echo   %APP_NAME% - Setup and Launcher
echo   Current Version: %CURRENT_VERSION%
echo ======================================================
echo.

:: 1. Check for updates
echo Checking for updates...
call :CheckForUpdates
echo.

:: 2. Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is not installed. Installing...
    set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe' -OutFile '%PYTHON_INSTALLER%'"
    start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    echo Python installed successfully.
    echo.
) else (
    echo Python is already installed.
    echo.
)

:: 2. Check pip
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found. Installing...
    python -m ensurepip --upgrade
    echo pip installed successfully.
    echo.
) else (
    echo pip is already available.
    echo.
)

:: 3. Check for previous installations and install dependencies if needed
set "INSTALL_FLAG=%INSTALLER_DIR%\.installed_%CURRENT_VERSION%"
for %%f in ("%INSTALLER_DIR%\.installed_*") do (
    if exist "%%f" (
        echo Found previous installation marker: %%~nxf
        if not "%%f"=="%INSTALL_FLAG%" (
            echo Outdated installation detected. Reinstalling dependencies...
            del "%%f" >nul 2>&1
            goto :InstallDependencies
        ) else (
            echo Current version dependencies already installed.
            goto :LaunchApp
        )
    )
)

:: If no flag file found, install dependencies
:InstallDependencies
echo Installing dependencies for version %CURRENT_VERSION%...
if not exist "%REQUIREMENTS_FILE%" (
    echo Error: Requirements file not found at %REQUIREMENTS_FILE%
    echo Please ensure the CameraTrapAssistant folder is present.
    pause
    exit /b 1
)
python -m pip install --upgrade pip
python -m pip install -r "%REQUIREMENTS_FILE%"
echo %date% %time% > "%INSTALL_FLAG%"
echo Dependencies installed successfully.
echo.

:LaunchApp
echo Launching %APP_NAME%...
echo.
if not exist "%MAIN_PY%" (
    echo Error: Main application file not found at %MAIN_PY%
    echo Please ensure the CameraTrapAssistant folder structure is correct.
    pause
    exit /b 1
)
python "%MAIN_PY%"

echo.
echo ======================================================
echo   %APP_NAME% v%CURRENT_VERSION% is now running.
echo   (Close this window to exit)
echo ======================================================
echo.

pause
exit /b

:: ======================================================
:: Functions
:: ======================================================

:CheckForUpdates
:: Check if PowerShell is available
powershell -Command "exit" >nul 2>&1
if errorlevel 1 (
    echo PowerShell not available. Skipping update check.
    goto :eof
)

:: Get latest release info from GitHub
echo Fetching latest version from GitHub...
for /f "tokens=*" %%i in ('powershell -Command "try { $response = Invoke-RestMethod -Uri '%GITHUB_API_URL%'; $response.tag_name -replace '^v', '' } catch { 'ERROR' }"') do set "LATEST_VERSION=%%i"

if "%LATEST_VERSION%"=="ERROR" (
    echo Warning: Could not check for updates. Continuing with current version.
    goto :eof
)

echo Latest version available: %LATEST_VERSION%
echo Current version: %CURRENT_VERSION%

:: Compare versions using PowerShell for better semantic version handling
if "%FORCE_UPDATE%"=="true" (
    set "IS_NEWER=true"
    echo Forcing update due to missing installation >> "%LOG_FILE%"
) else (
    for /f %%i in ('powershell -Command "try { if ([version]'%LATEST_VERSION%' -gt [version]'%CURRENT_VERSION%') { 'true' } else { 'false' } } catch { 'true' }"') do set "IS_NEWER=%%i"
    echo Version comparison result: %IS_NEWER% >> "%LOG_FILE%"
)

if "%IS_NEWER%"=="false" (
    echo You have the latest version.
    echo No update needed >> "%LOG_FILE%"
    goto :eof
)

echo.
echo A newer version (%LATEST_VERSION%) is available!

:: Try to get release notes
powershell -Command "try { $response = Invoke-RestMethod -Uri '%GITHUB_API_URL%'; if ($response.body) { Write-Host 'Release Notes:'; Write-Host $response.body.Substring(0, [Math]::Min(200, $response.body.Length)); if ($response.body.Length -gt 200) { Write-Host '...' } } } catch { }" 2>nul

echo.
set /p "UPDATE_CHOICE=Do you want to update? (y/n): "
if /i "%UPDATE_CHOICE%"=="y" goto :DownloadUpdate
if /i "%UPDATE_CHOICE%"=="yes" goto :DownloadUpdate
echo Continuing with current version...
goto :eof

:DownloadUpdate
echo.
echo Downloading update...
:: Create temporary directory
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: Download the latest release
set "DOWNLOAD_URL=https://github.com/%GITHUB_REPO%/archive/refs/tags/v%LATEST_VERSION%.zip"
set "ZIP_FILE=%TEMP_DIR%\update.zip"

powershell -Command "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%ZIP_FILE%' -UseBasicParsing; Write-Host 'Download completed.' } catch { Write-Host 'Download failed.'; exit 1 }"
if errorlevel 1 (
    echo Failed to download update.
    goto :eof
)

:: Extract the zip file
echo Extracting update...
powershell -Command "try { Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%TEMP_DIR%' -Force; Write-Host 'Extraction completed.' } catch { Write-Host 'Extraction failed.'; exit 1 }"
if errorlevel 1 (
    echo Failed to extract update.
    goto :eof
)

:: Find the extracted folder (should be CameraTrapAssistant-vX.X.X)
for /d %%d in ("%TEMP_DIR%\CameraTrapAssistant-*") do set "EXTRACTED_DIR=%%d"
if not exist "%EXTRACTED_DIR%\CameraTrapAssistant" (
    echo Error: Could not find CameraTrapAssistant folder in update.
    goto :eof
)

:: Backup current installation
echo Backing up current installation...
if exist "%CTA_DIR%" (
    if exist "%CTA_DIR%_backup" rmdir /s /q "%CTA_DIR%_backup"
    move "%CTA_DIR%" "%CTA_DIR%_backup" >nul 2>&1
    if errorlevel 1 (
        echo Warning: Could not backup current installation.
        echo Proceeding with caution...
    ) else (
        echo Backup created successfully.
    )
)

:: Move new version
echo Installing new version...
move "%EXTRACTED_DIR%\CameraTrapAssistant" "%CTA_DIR%" >nul 2>&1
if errorlevel 1 (
    echo Error: Failed to install new version.
    if exist "%CTA_DIR%_backup" (
        echo Restoring backup...
        move "%CTA_DIR%_backup" "%CTA_DIR%" >nul 2>&1
        echo Backup restored.
    )
    goto :eof
)

:: Verify installation
if not exist "%CTA_DIR%\src\main.py" (
    echo Error: Installation verification failed.
    if exist "%CTA_DIR%_backup" (
        echo Restoring backup...
        rmdir /s /q "%CTA_DIR%" 2>nul
        move "%CTA_DIR%_backup" "%CTA_DIR%" >nul 2>&1
        echo Backup restored.
    )
    goto :eof
)

:: Update current version
set "CURRENT_VERSION=%LATEST_VERSION%"

:: Clean up backup after successful installation
if exist "%CTA_DIR%_backup" (
    echo Cleaning up backup...
    rmdir /s /q "%CTA_DIR%_backup"
)

:: Clean up
rmdir /s /q "%TEMP_DIR%"

:: Remove old installation flags
for %%f in ("%INSTALLER_DIR%\.installed_*") do del "%%f" >nul 2>&1

echo.
echo Update completed successfully!
echo New version %LATEST_VERSION% is now installed.
echo.
goto :eof
