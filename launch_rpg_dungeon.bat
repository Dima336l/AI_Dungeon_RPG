@echo off
setlocal enabledelayedexpansion

:: ========================================
:: Fables - Launch Script
:: ========================================
:: This script launches the required services:
:: 1. Ollama (LLM for narrative generation)
:: 2. ComfyUI (Image Generation Backend)
:: 3. Flask Web Server (Frontend)

echo.
echo ========================================
echo    Fables - Launch Script
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
set OLLAMA_RUNNING=0
set COMFYUI_RUNNING=0
set FLASK_RUNNING=0

:: ========================================
:: STEP 0: Start Ollama (LLM)
:: ========================================
echo.
echo [1/3] Starting Ollama (LLM for narrative generation)...
echo ========================================

:: Check if Ollama is already responding on port 11434 (we still open the terminal below)
netstat -an | findstr ":11434 " >nul
if %errorlevel% equ 0 (
    set OLLAMA_ALREADY=1
) else (
    set OLLAMA_ALREADY=0
)

:: Find Ollama: try PATH first, then default Windows install path
set OLLAMA_CMD=
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    set OLLAMA_CMD=ollama serve
) else (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        set OLLAMA_CMD="%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    ) else if exist "%LOCALAPPDATA%\Programs\Ollama\Ollama.exe" (
        set OLLAMA_CMD="%LOCALAPPDATA%\Programs\Ollama\Ollama.exe" serve
    )
)

if "!OLLAMA_CMD!"=="" (
    echo WARNING: Ollama not found in PATH or at %LOCALAPPDATA%\Programs\Ollama
    echo Please install Ollama from https://ollama.com/download or start it manually, then press any key...
    pause >nul
    set OLLAMA_RUNNING=1
    goto :ollama_done
)

:: Always open the Ollama terminal so the user sees it running
start "Ollama" cmd /k !OLLAMA_CMD!
set OLLAMA_RUNNING=1
echo Ollama terminal opened.

if !OLLAMA_ALREADY! equ 1 (
    echo Ollama already running on port 11434 - skipping wait.
    goto :ollama_done
)
echo Ollama launched.

:ollama_wait
echo Giving Ollama time to start and detect GPU (about 12 seconds)...
timeout /t 12 /nobreak >nul
echo Checking if Ollama API is ready...
set OLLAMA_READY=0
for /L %%i in (1,1,30) do (
    powershell -NoProfile -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:11434/api/tags' -UseBasicParsing -TimeoutSec 3; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        set OLLAMA_READY=1
        echo Ollama is ready.
        goto :ollama_done
    )
    echo   Attempt %%i/30 - waiting 1 sec...
    timeout /t 1 /nobreak >nul
)
echo WARNING: Ollama did not respond within 30 seconds. Continuing anyway - ensure Ollama is running.
:ollama_done

:: ========================================
:: STEP 1: Start ComfyUI (Backend)
:: ========================================
echo.
echo [2/3] Starting ComfyUI (Image Generation Backend)...
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
echo [3/3] Starting Flask Web Server (Frontend)...
echo ========================================

:: Check if port 5000 is in use
netstat -an | findstr ":5000 " >nul
if %errorlevel% equ 0 (
    echo WARNING: Port 5000 is already in use. Stopping existing Flask server...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo Starting Flask server...
start "Fables - Flask Server" cmd /k "cd /d %PROJECT_DIR% && %VENV_DIR%\Scripts\activate.bat && python app.py"
set FLASK_RUNNING=1
echo Flask server startup initiated!

:: ========================================
:: SERVICES COMPLETE
:: ========================================
echo.
echo [3/3] Services Complete - Ready to Launch
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

:: Display Ollama status
if !OLLAMA_RUNNING!==1 (
    echo [OK] Ollama - LLM - Started / available on port 11434
) else (
    echo [FAIL] Ollama - LLM - Not started. Start it manually to avoid connection errors.
)

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
echo 1. Keep all command windows open (Ollama, ComfyUI, Flask) while using the application
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