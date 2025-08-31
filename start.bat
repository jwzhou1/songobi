@echo off
REM Licensed under the Apache License, Version 2.0 (the "License");
REM you may not use this file except in compliance with the License.

echo Starting Songo BI Platform...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Docker is running ✓
echo.

REM Check if .env file exists
if not exist "docker\.env" (
    echo Creating environment configuration...
    copy "docker\.env" "docker\.env-local" >nul 2>&1
)

echo Starting Songo BI services...
echo This may take a few minutes on first run...
echo.

REM Start the platform
docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✅ Songo BI is starting up!
    echo.
    echo 🌐 Main Application: http://localhost:8088
    echo 🔧 Frontend Dev Server: http://localhost:9000
    echo 📊 Default Login: admin / admin
    echo.
    echo 📋 Useful commands:
    echo   docker-compose logs -f           ^(view logs^)
    echo   docker-compose ps                ^(check status^)
    echo   docker-compose down              ^(stop services^)
    echo.
    echo Opening main application in browser...
    timeout /t 10 /nobreak >nul
    start http://localhost:8088
) else (
    echo.
    echo ❌ Failed to start Songo BI
    echo Check the logs with: docker-compose logs
)

pause
