@echo off
title CameraTrap Assistant - Launcher
setlocal

:: ======================================================
:: Launcher Script - Launches the application
:: ======================================================

set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."
set "CTA_DIR=%PROJECT_ROOT%\CameraTrapAssistant"
set "UTILS_DIR=%SCRIPT_DIR%installer_files_utils"
set "LOG_FILE=%UTILS_DIR%\CameraTrapAssistant_installer.log"
set "MAIN_PY=%CTA_DIR%\src\main.py"

:: Check if application exists
if not exist "%MAIN_PY%" (
    echo Error: Main application file not found at %MAIN_PY%
    echo Error: Main application file not found >> "%LOG_FILE%"
    echo Please ensure the CameraTrapAssistant folder structure is correct.
    pause
    exit /b 1
)

:: Read current version if available
set "CURRENT_VERSION=Unknown"
set "VERSION_JSON=%CTA_DIR%\version.json"
if exist "%VERSION_JSON%" (
    powershell -Command "try { $json = Get-Content '%VERSION_JSON%' | ConvertFrom-Json; $json.version } catch { 'Unknown' }" > "%TEMP%\version_temp.txt"
    for /f "delims=" %%i in ('type "%TEMP%\version_temp.txt"') do set "CURRENT_VERSION=%%i"
    del "%TEMP%\version_temp.txt" >nul 2>&1
)

echo ======================================================
echo   CameraTrap Assistant v%CURRENT_VERSION%
echo ======================================================
echo.

echo Launching CameraTrap Assistant...
echo Launching application v%CURRENT_VERSION% - %date% %time% >> "%LOG_FILE%"

:: Launch the application
python "%MAIN_PY%"

echo.
echo Application closed.
echo Application closed - %date% %time% >> "%LOG_FILE%"