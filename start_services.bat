@echo off
REM Prompt Firewall - Start/Stop Services Script for Windows
REM This script manages both backend and frontend services

setlocal enabledelayedexpansion

REM Get command argument
set COMMAND=%~1
if "%COMMAND%"=="" set COMMAND=start

REM Function to check if port is in use
:check_port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%1') do (
    set PID=%%a
    if not "!PID!"=="" (
        echo Port %1 is in use
        exit /b 0
    )
)
echo Port %1 is available
exit /b 1

REM Function to stop service on port
:stop_service
set PORT=%1
set SERVICE_NAME=%2
echo [INFO] Stopping %SERVICE_NAME% on port %PORT%...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%PORT%') do (
    set PID=%%a
    if not "!PID!"=="" (
        echo Killing process !PID!
        taskkill /PID !PID! /F >nul 2>&1
    )
)
timeout /t 2 /nobreak >nul
goto :eof

REM Start Backend
:start_backend
echo.
echo === Setting up Backend ===
cd backend

REM Check if venv exists
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

REM Activate venv and install dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip (quietly)
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip -q

REM Check if dependencies need installation
echo [INFO] Checking backend dependencies...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing backend dependencies (first time setup)...
    pip install -r requirements.txt
) else (
    echo [INFO] Dependencies found. Skipping installation. Use 'pip install -r requirements.txt' to update.
)

REM Stop backend if running
call :stop_service 8000 "Backend"

REM Start backend
echo [INFO] Starting Backend on port 8000...
start /B cmd /c "set PYTHONPATH=src && uvicorn src.main:app --host 0.0.0.0 --port 8000 > ..\logs\backend.log 2>&1"
echo 8000 > ..\logs\backend.port

timeout /t 3 /nobreak >nul
cd ..

REM Check if backend started
netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo [INFO] Backend is running on http://localhost:8000
) else (
    echo [ERROR] Failed to start backend!
    exit /b 1
)
goto :eof

REM Start Frontend
:start_frontend
echo.
echo === Setting up Frontend ===
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo [INFO] Installing frontend dependencies (first time setup)...
    call npm install
) else (
    echo [INFO] Dependencies found. Skipping installation. Use 'npm install' to update.
)

REM Stop frontend if running
call :stop_service 3000 "Frontend"

REM Start frontend
echo [INFO] Starting Frontend on port 3000...
start /B cmd /c "npm run dev > ..\logs\frontend.log 2>&1"
echo 3000 > ..\logs\frontend.port

timeout /t 5 /nobreak >nul
cd ..

REM Check if frontend started
netstat -an | findstr :3000 >nul
if %errorlevel% equ 0 (
    echo [INFO] Frontend is running on http://localhost:3000
) else (
    echo [ERROR] Failed to start frontend!
    exit /b 1
)
goto :eof

REM Stop all services
:stop_services
echo [INFO] === Stopping Services ===

REM Stop backend
if exist "logs\backend.port" (
    set /p BACKEND_PORT=<logs\backend.port
    call :stop_service %BACKEND_PORT% "Backend"
)
call :stop_service 8000 "Backend"

REM Stop frontend
if exist "logs\frontend.port" (
    set /p FRONTEND_PORT=<logs\frontend.port
    call :stop_service %FRONTEND_PORT% "Frontend"
)
call :stop_service 3000 "Frontend"

echo [INFO] All services stopped
goto :eof

REM Show status
:show_status
echo [INFO] === Service Status ===

netstat -an | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo Backend is running on port 8000
) else (
    echo Backend is not running
)

netstat -an | findstr :3000 >nul
if %errorlevel% equ 0 (
    echo Frontend is running on port 3000
) else (
    echo Frontend is not running
)
goto :eof

REM Main script logic
if "%COMMAND%"=="start" goto start_all
if "%COMMAND%"=="stop" goto stop_all
if "%COMMAND%"=="status" goto status_all
if "%COMMAND%"=="restart" goto restart_all
goto help

:start_all
REM Create logs directory
if not exist "logs" mkdir logs

echo [INFO] Starting Prompt Firewall services...
echo ======================================

REM Stop existing services
echo [INFO] Stopping any existing services...
call :stop_services
timeout /t 2 /nobreak >nul

REM Start services
call :start_backend
timeout /t 2 /nobreak >nul
call :start_frontend

echo.
echo ======================================
echo All services started successfully!
echo.
echo Backend API: http://localhost:8000
echo Backend Docs: http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo.
echo To stop services, run: start_services.bat stop
echo To check status, run: start_services.bat status
goto :eof

:stop_all
call :stop_services
goto :eof

:status_all
call :show_status
goto :eof

:restart_all
echo [INFO] Restarting services...
call :stop_services
timeout /t 2 /nobreak >nul
goto start_all

:help
echo Usage: start_services.bat {start^|stop^|status^|restart}
echo.
echo Commands:
echo   start   - Start both backend and frontend services
echo   stop    - Stop both backend and frontend services
echo   status  - Check status of services
echo   restart - Restart both services
echo.
echo Default: start

endlocal

