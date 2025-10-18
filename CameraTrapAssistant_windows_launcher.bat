@echo off
title CameraTrap Assistant - Windows Launcher
setlocal

:: ======================================================
:: Main Windows Launcher - Checks installation and launches app
:: ======================================================

set "APP_NAME=CameraTrap Assistant"
set "PROJECT_ROOT=%~dp0"
set "SCRIPTS_DIR=%PROJECT_ROOT%scripts"
set "UTILS_DIR=%SCRIPTS_DIR%\installer_files_utils"
set "INSTALL_FLAG=%UTILS_DIR%\.installed"
set "CTA_DIR=%PROJECT_ROOT%CameraTrapAssistant"

echo ======================================================
echo   %APP_NAME% - Windows Launcher
echo ======================================================
echo.

:: Check if CameraTrapAssistant folder exists
if not exist "%CTA_DIR%" (
    echo CameraTrapAssistant folder not found.
    echo This appears to be a first-time setup.
    echo.
    echo Please run the updater script first to download the application:
    echo   scripts\updater.bat
    echo.
    pause
    exit /b 1
)

:: Check if installation is complete
if not exist "%INSTALL_FLAG%" (
    echo Installation marker not found. Running installer...
    echo.
    call "%SCRIPTS_DIR%\installer.bat"
    if errorlevel 1 (
        echo Installation failed. Please check the logs and try again.
        pause
        exit /b 1
    )
)

:: Launch the application
echo Installation found. Launching application...
echo.
call "%SCRIPTS_DIR%\launcher.bat"

:: Launcher will exit automatically after starting the app
:: No need to pause - terminal will close