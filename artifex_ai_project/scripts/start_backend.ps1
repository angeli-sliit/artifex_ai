# ArtifexAI Backend Startup Script
Write-Host "Starting ArtifexAI Backend..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r backend/requirements.txt

Write-Host ""
Write-Host "Starting Backend API..." -ForegroundColor Yellow
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan
Write-Host ""

# Start the backend
python backend/main.py
