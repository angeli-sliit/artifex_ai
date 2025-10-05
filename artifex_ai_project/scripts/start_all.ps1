# ArtifexAI Complete System Startup Script
Write-Host "Starting ArtifexAI Complete System..." -ForegroundColor Green
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
Write-Host "Installing all dependencies..." -ForegroundColor Yellow
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt

Write-Host ""
Write-Host "Starting Backend API..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'venv\Scripts\Activate.ps1'; python backend/main.py"

Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'venv\Scripts\Activate.ps1'; streamlit run frontend/app.py"

Write-Host ""
Write-Host "✅ ArtifexAI System Started!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend App: http://localhost:8501" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
