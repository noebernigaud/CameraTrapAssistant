@echo off
title CameraTrap Assistant - Updater
setlocal

:: ======================================================
:: Updater Script - Checks GitHub and updates application
:: ======================================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "CTA_DIR=%PROJECT_ROOT%\CameraTrapAssistant"
set "UTILS_DIR=%SCRIPT_DIR%installer_files_utils"
set "LOG_FILE=%UTILS_DIR%\CameraTrapAssistant_installer.log"
set "VERSION_JSON=%CTA_DIR%\version.json"
set "REQUIREMENTS_FILE=%CTA_DIR%\requirements.txt"
set "GITHUB_REPO=noebernigaud/CameraTrapAssistant"
set "GITHUB_API_URL=https://api.github.com/repos/%GITHUB_REPO%/releases/latest"
set "TEMP_DIR=%TEMP%\CameraTrapAssistant_Update"

:: Create utils directory if it doesn't exist
if not exist "%UTILS_DIR%" mkdir "%UTILS_DIR%"

echo ======================================================
echo   CameraTrap Assistant - Update Checker
echo ======================================================
echo.

:: Read current version
set "CURRENT_VERSION=0.0.0"
if not exist "%CTA_DIR%" (
    echo CameraTrapAssistant folder not found. This appears to be a first-time installation.
    echo Current Version: Not installed >> "%LOG_FILE%"
    echo Forcing update check... >> "%LOG_FILE%"
    set "FORCE_UPDATE=true"
) else (
    if exist "%VERSION_JSON%" (
        powershell -Command "try { $json = Get-Content '%VERSION_JSON%' | ConvertFrom-Json; $json.version } catch { '0.0.0' }" > "%TEMP%\version_temp.txt"
        for /f "delims=" %%i in ('type "%TEMP%\version_temp.txt"') do set "CURRENT_VERSION=%%i"
        del "%TEMP%\version_temp.txt" >nul 2>&1
    ) else (
        echo Warning: version.json not found. Using default version 0.0.0 >> "%LOG_FILE%"
    )
    echo Current Version: %CURRENT_VERSION% >> "%LOG_FILE%"
)

echo Current Version: %CURRENT_VERSION%
echo.

:: Check for updates
echo Checking for updates from GitHub...
call :CheckForUpdates

echo.
echo Update check completed.
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
    echo PowerShell not available >> "%LOG_FILE%"
    goto :eof
)

:: Get latest release info from GitHub
echo Fetching latest version from GitHub...
for /f "tokens=*" %%i in ('powershell -Command "try { $response = Invoke-RestMethod -Uri '%GITHUB_API_URL%'; $response.tag_name -replace '^v', '' } catch { 'ERROR' }"') do set "LATEST_VERSION=%%i"

if "%LATEST_VERSION%"=="ERROR" (
    echo Warning: Could not check for updates. Continuing with current version.
    echo Warning: Could not check for updates >> "%LOG_FILE%"
    goto :eof
)

echo Latest version available: %LATEST_VERSION%
echo Current version: %CURRENT_VERSION%

:: Compare versions
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
echo Starting download of version %LATEST_VERSION% >> "%LOG_FILE%"

:: Create temporary directory
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

:: Download the latest release
set "DOWNLOAD_URL=https://github.com/%GITHUB_REPO%/archive/refs/tags/v%LATEST_VERSION%.zip"
set "ZIP_FILE=%TEMP_DIR%\update.zip"

powershell -Command "try { Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%ZIP_FILE%' -UseBasicParsing; Write-Host 'Download completed.' } catch { Write-Host 'Download failed.'; exit 1 }"
if errorlevel 1 (
    echo Failed to download update.
    echo Failed to download update >> "%LOG_FILE%"
    goto :eof
)

:: Extract the zip file
echo Extracting update...
powershell -Command "try { Expand-Archive -Path '%ZIP_FILE%' -DestinationPath '%TEMP_DIR%' -Force; Write-Host 'Extraction completed.' } catch { Write-Host 'Extraction failed.'; exit 1 }"
if errorlevel 1 (
    echo Failed to extract update.
    echo Failed to extract update >> "%LOG_FILE%"
    goto :eof
)

:: Find the extracted folder
for /d %%d in ("%TEMP_DIR%\CameraTrapAssistant-*") do set "EXTRACTED_DIR=%%d"
if not exist "%EXTRACTED_DIR%\CameraTrapAssistant" (
    echo Error: Could not find CameraTrapAssistant folder in update.
    echo Error: CameraTrapAssistant folder not found in update >> "%LOG_FILE%"
    goto :eof
)

:: Backup current installation
echo Backing up current installation...
if exist "%CTA_DIR%" (
    if exist "%CTA_DIR%_backup" rmdir /s /q "%CTA_DIR%_backup"
    move "%CTA_DIR%" "%CTA_DIR%_backup" >nul 2>&1
    if errorlevel 1 (
        echo Warning: Could not backup current installation.
        echo Warning: Could not backup current installation >> "%LOG_FILE%"
        echo Proceeding with caution...
    ) else (
        echo Backup created successfully.
        echo Backup created successfully >> "%LOG_FILE%"
    )
)

:: Install new version
echo Installing new version...
move "%EXTRACTED_DIR%\CameraTrapAssistant" "%CTA_DIR%" >nul 2>&1
if errorlevel 1 (
    echo Error: Failed to install new version.
    echo Error: Failed to install new version >> "%LOG_FILE%"
    if exist "%CTA_DIR%_backup" (
        echo Restoring backup...
        move "%CTA_DIR%_backup" "%CTA_DIR%" >nul 2>&1
        echo Backup restored.
        echo Backup restored >> "%LOG_FILE%"
    )
    goto :eof
)

:: Verify installation
if not exist "%CTA_DIR%\src\main.py" (
    echo Error: Installation verification failed.
    echo Error: Installation verification failed >> "%LOG_FILE%"
    if exist "%CTA_DIR%_backup" (
        echo Restoring backup...
        rmdir /s /q "%CTA_DIR%" 2>nul
        move "%CTA_DIR%_backup" "%CTA_DIR%" >nul 2>&1
        echo Backup restored.
        echo Backup restored >> "%LOG_FILE%"
    )
    goto :eof
)

:: Update dependencies
echo Updating dependencies...
if exist "%REQUIREMENTS_FILE%" (
    echo Updating Python dependencies...
    echo Updating dependencies >> "%LOG_FILE%"
    python -m pip install --upgrade pip
    python -m pip install -r "%REQUIREMENTS_FILE%"
    if errorlevel 1 (
        echo Warning: Some dependencies may not have been updated properly.
        echo Warning: Dependencies update issues >> "%LOG_FILE%"
    ) else (
        echo Dependencies updated successfully.
        echo Dependencies updated successfully >> "%LOG_FILE%"
    )
) else (
    echo Warning: Requirements file not found in new version.
    echo Warning: Requirements file not found >> "%LOG_FILE%"
)

:: Clean up backup after successful installation
if exist "%CTA_DIR%_backup" (
    echo Cleaning up backup...
    rmdir /s /q "%CTA_DIR%_backup"
)

:: Clean up temp files
rmdir /s /q "%TEMP_DIR%"

:: Remove old installation flag and create new one
if exist "%UTILS_DIR%\.installed" del "%UTILS_DIR%\.installed" >nul 2>&1
echo %date% %time% > "%UTILS_DIR%\.installed"

echo.
echo Update completed successfully!
echo New version %LATEST_VERSION% is now installed.
echo Update completed successfully to version %LATEST_VERSION% >> "%LOG_FILE%"
echo.
goto :eof