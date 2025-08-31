# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

# PowerShell script to start Songo BI Platform

Write-Host "🚀 Starting Songo BI Platform..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Check if environment file exists
if (-not (Test-Path "docker\.env-local")) {
    Write-Host "📝 Creating local environment configuration..." -ForegroundColor Yellow
    Copy-Item "docker\.env" "docker\.env-local" -ErrorAction SilentlyContinue
}

Write-Host "🔧 Starting Songo BI services..." -ForegroundColor Cyan
Write-Host "⏳ This may take a few minutes on first run..." -ForegroundColor Yellow
Write-Host ""

# Start the platform
$result = docker-compose up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Songo BI is starting up!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Main Application: http://localhost:8088" -ForegroundColor Cyan
    Write-Host "🔧 Frontend Dev Server: http://localhost:9000" -ForegroundColor Cyan
    Write-Host "📊 Default Login: admin / admin" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Useful commands:" -ForegroundColor White
    Write-Host "  docker-compose logs -f           (view logs)" -ForegroundColor Gray
    Write-Host "  docker-compose ps                (check status)" -ForegroundColor Gray
    Write-Host "  docker-compose down              (stop services)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
    
    Write-Host "🌐 Opening main application in browser..." -ForegroundColor Cyan
    Start-Process "http://localhost:8088"
} else {
    Write-Host ""
    Write-Host "❌ Failed to start Songo BI" -ForegroundColor Red
    Write-Host "Check the logs with: docker-compose logs" -ForegroundColor Yellow
}

Read-Host "Press Enter to continue"
