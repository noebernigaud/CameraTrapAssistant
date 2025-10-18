@echo off
title CameraTrap Assistant - Installer
setlocal

:: ======================================================
:: Installer Script - Handles Python, pip, and dependencies
:: ======================================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "CTA_DIR=%PROJECT_ROOT%\CameraTrapAssistant"
set "UTILS_DIR=%SCRIPT_DIR%installer_files_utils"
set "LOG_FILE=%UTILS_DIR%\CameraTrapAssistant_installer.log"
set "REQUIREMENTS_FILE=%CTA_DIR%\requirements.txt"

:: Create utils directory if it doesn't exist
if not exist "%UTILS_DIR%" mkdir "%UTILS_DIR%"

:: Initialize log
echo ======================================================== >> "%LOG_FILE%"
echo CameraTrap Assistant Installer - %date% %time% >> "%LOG_FILE%"
echo ======================================================== >> "%LOG_FILE%"

echo ======================================================
echo   CameraTrap Assistant - Installation
echo ======================================================
echo.

:: 1. Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is not installed. Installing...
    echo Installing Python... >> "%LOG_FILE%"
    set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe' -OutFile '%PYTHON_INSTALLER%'"
    start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    echo Python installed successfully.
    echo Python installation completed >> "%LOG_FILE%"
    echo.
) else (
    echo Python is already installed.
    echo Python already installed >> "%LOG_FILE%"
    echo.
)

:: 2. Check pip
echo Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found. Installing...
    echo Installing pip... >> "%LOG_FILE%"
    python -m ensurepip --upgrade
    echo pip installed successfully.
    echo pip installation completed >> "%LOG_FILE%"
    echo.
) else (
    echo pip is already available.
    echo pip already available >> "%LOG_FILE%"
    echo.
)

:: 3. Install dependencies
echo Installing dependencies...
if not exist "%REQUIREMENTS_FILE%" (
    echo Error: Requirements file not found at %REQUIREMENTS_FILE%
    echo Error: Requirements file not found >> "%LOG_FILE%"
    echo Please ensure the CameraTrapAssistant folder is present.
    pause
    exit /b 1
)

echo Installing Python dependencies from requirements.txt...
echo Installing dependencies... >> "%LOG_FILE%"
python -m pip install --upgrade pip
python -m pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo Error: Failed to install dependencies
    echo Error: Failed to install dependencies >> "%LOG_FILE%"
    pause
    exit /b 1
)

:: 4. Create installation marker
echo Creating installation marker...
echo %date% %time% > "%UTILS_DIR%\.installed"
echo Installation completed successfully >> "%LOG_FILE%"

echo.
echo Dependencies installed successfully!
echo Installation completed.
echo.
pause