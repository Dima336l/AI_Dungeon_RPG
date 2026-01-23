@echo off
setlocal enabledelayedexpansion

:: ========================================
:: RPG Dungeon AI - Launch Script
:: ========================================
:: This script launches the required services:
:: 1. ComfyUI (Image Generation Backend)
:: 2. Flask Web Server (Frontend)

echo.
echo ========================================
echo    RPG Dungeon AI - Launch Script
echo ========================================
echo.

:: Set project directory
set PROJECT_DIR=C:\Users\nirca\repos\rpg_dungeon_ai
set COMFYUI_DIR=C:\Users\nirca\repos\ComfyUI
set VENV_DIR=%PROJECT_DIR%\ai_dungeon_env

:: Check if directories exist
if not exist "%PROJECT_DIR%" (
    echo ERROR: Project directory not found: %PROJECT_DIR%
    echo Please update the PROJECT_DIR variable in this script.
    pause
    exit /b 1
)

if not exist "%COMFYUI_DIR%" (
    echo ERROR: ComfyUI directory not found: %COMFYUI_DIR%
    echo Please update the COMFYUI_DIR variable in this script.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%" (
    echo ERROR: Virtual environment not found: %VENV_DIR%
    echo Please run the setup first: python -m venv ai_dungeon_env
    pause
    exit /b 1
)

:: Change to project directory
cd /d "%PROJECT_DIR%"

:: Initialize service flags
set COMFYUI_RUNNING=0
set FLASK_RUNNING=0

:: ========================================
:: STEP 1: Start ComfyUI (Backend)
:: ========================================
echo.
echo [1/2] Starting ComfyUI (Image Generation Backend)...
echo ========================================

:: Check if port 8188 is in use and kill existing ComfyUI processes
netstat -an | findstr ":8188 " >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 8188 is already in use. Killing existing ComfyUI processes...
    taskkill /f /im python.exe >nul 2>&1
    taskkill /f /im ComfyUI.exe >nul 2>&1
    timeout /t 3 /nobreak >nul
    echo Restarting ComfyUI with RTX 5090 optimization...
)

echo Checking ComfyUI dependencies...
cd /d %COMFYUI_DIR%

:: Check if ComfyUI has its own virtual environment
if not exist "%COMFYUI_DIR%\venv" (
    echo Creating ComfyUI virtual environment...
    cd /d %COMFYUI_DIR%
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create ComfyUI virtual environment
        set COMFYUI_RUNNING=0
        goto :comfyui_done
    )
)

:: Skip dependency installation - use existing ComfyUI setup
echo Using existing ComfyUI installation
echo Checking CUDA support...
cd /d %COMFYUI_DIR%
venv\Scripts\python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>nul || echo CUDA check failed - continuing anyway

echo Starting ComfyUI with its own virtual environment
echo RTX 5090 GPU acceleration enabled with PyTorch 2.8.0+cu128 (RTX 5090 COMPATIBLE!)
echo Using GPU mode - RTX 5090 with GPU diffusion + CPU CLIP/VAE (default)
start "ComfyUI" cmd /k "%COMFYUI_DIR%\start_comfyui_rtx5090_gpu.bat"
set COMFYUI_RUNNING=1
echo ComfyUI startup initiated

:: Return to project directory
cd /d %PROJECT_DIR%

:comfyui_done

:: ========================================
:: STEP 2: Start Flask Web Server (Frontend)
:: ========================================
echo.
echo [2/2] Starting Flask Web Server (Frontend)...
echo ========================================

:: Check if port 5000 is in use
netstat -an | findstr ":5000 " >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 5000 is already in use. Stopping existing Flask server...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo Starting Flask server...
start "RPG Dungeon Flask Server" cmd /k "cd /d %PROJECT_DIR% && %VENV_DIR%\Scripts\activate.bat && python app.py"
set FLASK_RUNNING=1
echo Flask server startup initiated!

:: ========================================
:: SERVICES COMPLETE
:: ========================================
echo.
echo [2/2] Services Complete - Ready to Launch
echo ========================================

:: ========================================
:: WAIT FOR SERVICES TO START
:: ========================================
echo.
echo Waiting for services to start up...
echo This may take a few moments...
timeout /t 10 /nobreak >nul

:: ========================================
:: SUMMARY
:: ========================================
echo.
echo ========================================
echo           LAUNCH SUMMARY
echo ========================================
echo.

:: Display ComfyUI status
if !COMFYUI_RUNNING!==1 goto comfyui_ok
echo [FAIL] ComfyUI (Image Generation Backend) - Not started
goto comfyui_done
:comfyui_ok
echo [OK] ComfyUI (Image Generation Backend) - Started on port 8188
:comfyui_done

:: Display Flask status
if !FLASK_RUNNING!==1 goto flask_ok
echo [FAIL] Flask Web Server (Frontend) - Not started
goto flask_done
:flask_ok
echo [OK] Flask Web Server (Frontend) - Started on port 5000
echo   Local URL: http://127.0.0.1:5000
:flask_done

echo.
echo ========================================
echo           IMPORTANT NOTES
echo ========================================
echo.
echo 1. Keep all command windows open while using the application
echo 2. The Flask server will be accessible at: http://127.0.0.1:5000
echo 3. Generated images are cached in static/images/ for faster loading
echo 4. To stop all services, close all the opened command windows
echo 5. Wait a few more seconds for all services to fully initialize
echo.

:: Open the web browser after a short delay
echo Opening web browser in 5 seconds...
timeout /t 5 /nobreak >nul
start http://127.0.0.1:5000

echo.
echo All services have been launched!
echo Press any key to exit this launcher (services will continue running)...
pause >nul

endlocal