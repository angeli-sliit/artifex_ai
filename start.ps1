Write-Host "🎨 ArtifexAI - AI-Powered Art Price Predictions" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Choose an option:" -ForegroundColor Yellow
Write-Host "1. Run Streamlit App (Local)" -ForegroundColor Green
Write-Host "2. Install Dependencies" -ForegroundColor Blue
Write-Host "3. Open Hugging Face Demo (Online)" -ForegroundColor Magenta
Write-Host "4. View Project Info" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🚀 Starting Streamlit application..." -ForegroundColor Green
        Set-Location frontend
        streamlit run app.py
    }
    "2" {
        Write-Host ""
        Write-Host "📦 Installing dependencies..." -ForegroundColor Blue
        Set-Location frontend
        pip install -r requirements.txt
        Write-Host ""
        Write-Host "✅ Dependencies installed! You can now run option 1." -ForegroundColor Green
        Read-Host "Press Enter to continue"
    }
    "3" {
        Write-Host ""
        Write-Host "🌐 Opening Hugging Face demo..." -ForegroundColor Magenta
        Start-Process "https://huggingface.co/spaces/angeli2003/ArtifexAI"
    }
    "4" {
        Write-Host ""
        Write-Host "📋 Project Information:" -ForegroundColor Cyan
        Write-Host "• Version: v2.2 (HF Spaces Optimized)" -ForegroundColor White
        Write-Host "• Frontend: Streamlit with Starry Night background" -ForegroundColor White
        Write-Host "• Features: AI predictions, image analysis, PDF export" -ForegroundColor White
        Write-Host "• Live Demo: https://huggingface.co/spaces/angeli2003/ArtifexAI" -ForegroundColor White
        Write-Host "• Course: IT3051 - Fundamentals of Data Mining" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to continue"
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
        Read-Host "Press Enter to continue"
    }
}
