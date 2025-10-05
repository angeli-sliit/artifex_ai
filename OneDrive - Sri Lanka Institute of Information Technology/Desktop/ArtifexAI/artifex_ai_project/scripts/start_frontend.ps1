# ArtifexAI Improved Frontend Startup Script
Write-Host "Starting ArtifexAI Improved Frontend..." -ForegroundColor Green
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
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
pip install -r frontend/requirements.txt

Write-Host ""
Write-Host "Starting Improved Frontend..." -ForegroundColor Yellow
Write-Host "Frontend App: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

# Start the improved frontend
streamlit run frontend/app.py
