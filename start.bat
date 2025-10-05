@echo off
echo Starting ArtifexAI...
echo.
echo Choose an option:
echo 1. Run Streamlit App
echo 2. Install Dependencies
echo 3. Open Hugging Face Demo
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Starting Streamlit application...
    cd frontend
    streamlit run app.py
) else if "%choice%"=="2" (
    echo.
    echo Installing dependencies...
    cd frontend
    pip install -r requirements.txt
    echo.
    echo Dependencies installed! You can now run option 1.
    pause
) else if "%choice%"=="3" (
    echo.
    echo Opening Hugging Face demo...
    start https://huggingface.co/spaces/angeli2003/ArtifexAI
) else (
    echo Invalid choice. Please run the script again.
    pause
)
