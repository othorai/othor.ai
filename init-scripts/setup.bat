@echo off
setlocal enabledelayedexpansion

echo Starting Othor.ai setup on Windows...

:: Check if Git Bash is installed
where bash.exe >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Git Bash is not installed.
    echo Please install Git for Windows from https://gitforwindows.org/
    pause
    exit /b 1
)

:: Check if Docker is installed
where docker.exe >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Docker is not installed.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

:: Execute the setup script using Git Bash
bash.exe setup.sh

if %ERRORLEVEL% neq 0 (
    echo Setup failed. Please check the error messages above.
    pause
    exit /b 1
)

echo Setup completed successfully!
pause