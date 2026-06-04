@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "PID_FILE=%~dp0send_pids.txt"
set "PID_ARGS="
set /a pid_count=0

echo PID file: %PID_FILE%
echo Collecting recorded PIDs...
echo.

if not exist "%PID_FILE%" (
    echo No PID file found.
    pause
    exit /b
)

type "%PID_FILE%"
echo.

for /f "usebackq eol=# tokens=1 delims= " %%p in ("%PID_FILE%") do (
    set "PID=%%p"
    set "ISNUM=1"

    rem Numeric check without echo/findstr, so trailing spaces do not break it.
    for /f "delims=0123456789" %%x in ("!PID!") do set "ISNUM=0"

    if "!ISNUM!"=="1" (
        set "PID_ARGS=!PID_ARGS! /PID !PID!"
        set /a pid_count+=1
    )
)

if !pid_count! EQU 0 (
    echo No valid recorded PID found.
    pause
    exit /b
)

echo Closing !pid_count! process tree(s) in one taskkill call...
taskkill /F /T !PID_ARGS!

if exist "%PID_FILE%" del "%PID_FILE%" >nul 2>&1

echo.
echo Done.
pause
