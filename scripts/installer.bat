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

:: 1. Check for Python installation more thoroughly
echo Checking Python installation...
call :FindPython
if "%PYTHON_EXE%"=="" (
    echo Python 3 is not found. Installing...
    echo Installing Python... >> "%LOG_FILE%"
    call :InstallPython
    if errorlevel 1 (
        echo Error: Python installation failed
        echo Error: Python installation failed >> "%LOG_FILE%"
        pause
        exit /b 1
    )
    
    :: Try to find Python again after installation
    call :FindPython
    if "%PYTHON_EXE%"=="" (
        echo Error: Python still not found after installation
        echo Error: Python still not found after installation >> "%LOG_FILE%"
        echo.
        echo Please try one of the following:
        echo 1. Restart your computer and run this installer again
        echo 2. Install Python manually from python.org
        echo 3. Check Windows Settings ^> Apps ^> App execution aliases and disable Python entries
        pause
        exit /b 1
    )
) else (
    echo Python found at: %PYTHON_EXE%
    echo Python found at: %PYTHON_EXE% >> "%LOG_FILE%"
)

echo.

:: 2. Check pip
echo Checking pip...
"%PYTHON_EXE%" -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found. Installing...
    echo Installing pip... >> "%LOG_FILE%"
    "%PYTHON_EXE%" -m ensurepip --upgrade
    if errorlevel 1 (
        echo Error: Failed to install pip
        echo Error: Failed to install pip >> "%LOG_FILE%"
        pause
        exit /b 1
    )
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
"%PYTHON_EXE%" -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Failed to upgrade pip, continuing...
    echo Warning: Failed to upgrade pip >> "%LOG_FILE%"
)

"%PYTHON_EXE%" -m pip install -r "%REQUIREMENTS_FILE%"
if errorlevel 1 (
    echo Error: Failed to install dependencies
    echo Error: Failed to install dependencies >> "%LOG_FILE%"
    echo.
    echo This might be due to:
    echo - Network connectivity issues
    echo - Missing system dependencies
    echo - Antivirus blocking downloads
    echo.
    echo Check the log file for details: %LOG_FILE%
    pause
    exit /b 1
)

:: 4. Create installation marker with Python path
echo Creating installation marker...
echo Installation completed: %date% %time% > "%UTILS_DIR%\.installed"
echo Python executable: %PYTHON_EXE% >> "%UTILS_DIR%\.installed"
echo Installation completed successfully >> "%LOG_FILE%"

echo.
echo Dependencies installed successfully!
echo Installation completed.
echo.
pause
exit /b 0

:: ======================================================
:: Functions
:: ======================================================

:FindPython
:: Try to find Python executable in various locations
set "PYTHON_EXE="

:: Method 1: Try standard python command (but avoid MS Store version)
python --version >nul 2>&1
if not errorlevel 1 (
    :: Check if it's the real Python, not MS Store stub
    for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do (
        if not "%%i"=="" (
            if not "%%i"=="python" (
                set "PYTHON_EXE=%%i"
                goto :FoundPython
            )
        )
    )
)

:: Method 2: Try py launcher
py --version >nul 2>&1
if not errorlevel 1 (
    for /f "tokens=*" %%i in ('py -c "import sys; print(sys.executable)" 2^>nul') do (
        if not "%%i"=="" (
            set "PYTHON_EXE=%%i"
            goto :FoundPython
        )
    )
)

:: Method 3: Check common installation paths
for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles(x86)%\Python312\python.exe"
    "%ProgramFiles(x86)%\Python311\python.exe"
    "%ProgramFiles(x86)%\Python310\python.exe"
) do (
    if exist %%P (
        set "PYTHON_EXE=%%P"
        goto :FoundPython
    )
)

:: Method 4: Search in PATH (excluding MS Store)
for %%P in (python.exe) do (
    set "FOUND_PATH=%%~$PATH:P"
    if not "!FOUND_PATH!"=="" (
        if not "!FOUND_PATH!"=="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
            set "PYTHON_EXE=!FOUND_PATH!"
            goto :FoundPython
        )
    )
)

:FoundPython
if not "%PYTHON_EXE%"=="" (
    echo Found Python at: %PYTHON_EXE% >> "%LOG_FILE%"
)
goto :eof

:InstallPython
echo Downloading Python installer...
set "PYTHON_INSTALLER=%TEMP%\python-installer.exe"
powershell -Command "try { Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe' -OutFile '%PYTHON_INSTALLER%' -UseBasicParsing } catch { exit 1 }"
if errorlevel 1 (
    echo Error: Failed to download Python installer
    echo Error: Failed to download Python installer >> "%LOG_FILE%"
    exit /b 1
)

echo Installing Python (this may take several minutes)...
echo Please wait while Python is being installed...
start /wait "" "%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1 AssociateFiles=1

:: Clean up installer
del "%PYTHON_INSTALLER%" 2>nul

echo Python installation process completed.
echo Python installation process completed >> "%LOG_FILE%"

:: Wait for PATH to be updated
echo Waiting for system to update...
timeout /t 5 /nobreak >nul

goto :eof