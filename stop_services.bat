@echo off
REM Prompt Firewall - Stop Services Script for Windows
REM This script stops both backend and frontend services

setlocal enabledelayedexpansion

set FORCE_STOP=0
if "%1"=="--force" set FORCE_STOP=1
if "%1"=="-f" set FORCE_STOP=1

echo [INFO] Stopping Prompt Firewall services...
echo ======================================
echo.

REM Stop backend
echo [INFO] Stopping Backend...

REM Check if PID file exists
if exist "logs\backend.pid" (
    set /p BACKEND_PID=<logs\backend.pid
    if not "!BACKEND_PID!"=="" (
        echo [INFO] Killing backend process !BACKEND_PID!...
        taskkill /PID !BACKEND_PID! /F >nul 2>&1
        del logs\backend.pid >nul 2>&1
    )
)

REM Kill any process using port 8000
echo [INFO] Stopping processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do (
    set PID=%%a
    if not "!PID!"=="" (
        echo Killing process !PID!
        taskkill /PID !PID! /F >nul 2>&1
    )
)

REM Stop frontend
echo.
echo [INFO] Stopping Frontend...

REM Check if PID file exists
if exist "logs\frontend.pid" (
    set /p FRONTEND_PID=<logs\frontend.pid
    if not "!FRONTEND_PID!"=="" (
        echo [INFO] Killing frontend process !FRONTEND_PID!...
        taskkill /PID !FRONTEND_PID! /F >nul 2>&1
        del logs\frontend.pid >nul 2>&1
    )
)

REM Kill any process using port 3000
echo [INFO] Stopping processes on port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do (
    set PID=%%a
    if not "!PID!"=="" (
        echo Killing process !PID!
        taskkill /PID !PID! /F >nul 2>&1
    )
)

timeout /t 2 /nobreak >nul

REM Force cleanup if requested
if "%FORCE_STOP%"=="1" (
    echo.
    echo [INFO] Performing force cleanup...
    
    REM Kill all uvicorn processes
    taskkill /FI "WINDOWTITLE eq uvicorn*" /F >nul 2>&1
    
    REM Kill all node processes running next
    for /f "tokens=2" %%a in ('tasklist ^| findstr /i "node.exe"') do (
        REM Check if it's a next dev process
        taskkill /FI "IMAGENAME eq node.exe" /F >nul 2>&1
    )
    
    echo [INFO] Force cleanup complete
)

echo.
echo ======================================
echo [INFO] All services stopped

REM Verify ports are free
echo.
echo [INFO] Verifying ports are free...

netstat -an | findstr :8000 >nul
if %errorlevel% neq 0 (
    echo [INFO] Port 8000 is now free
) else (
    echo [WARNING] Port 8000 may still be in use
)

netstat -an | findstr :3000 >nul
if %errorlevel% neq 0 (
    echo [INFO] Port 3000 is now free
) else (
    echo [WARNING] Port 3000 may still be in use
)

echo.
echo [INFO] Done!

endlocal

