# ArtifexAI - Installation Guide

## Quick Start

### Option 1: Automatic Installation
```bash
# Run the automatic installer
python install_dependencies.py
```

### Option 2: Manual Installation
```bash
# Install core dependencies
pip install streamlit requests Pillow pandas numpy

# Install backend dependencies
pip install fastapi uvicorn pydantic python-multipart

# Install ML dependencies
pip install scikit-learn catboost joblib

# Optional: Install PDF generation support
pip install reportlab
```

## Running the Application

### 1. Start the Backend
```bash
cd backend
python main.py
```
The backend will start on `http://localhost:8000`

### 2. Start the Frontend
```bash
cd frontend
streamlit run app.py
```
The frontend will start on `http://localhost:8501`

## Features

### ✅ Core Features (Always Available)
- Landing page with hero image
- Image upload and analysis
- Artwork details form
- Price prediction with 57 features
- Results display with confidence metrics
- Text report export

### 📄 PDF Export (Optional)
- Install `reportlab` for PDF generation
- Without it, the app falls back to text reports
- Command: `pip install reportlab`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'reportlab'**
   - Solution: Install reportlab or use text reports
   - Command: `pip install reportlab`

2. **Backend connection failed**
   - Make sure backend is running on port 8000
   - Check if any firewall is blocking the connection

3. **Model not loaded**
   - Ensure the model file exists in the correct path
   - Check backend logs for model loading errors

### System Requirements
- Python 3.8+
- 4GB RAM minimum
- 1GB free disk space

## Development

### Project Structure
```
artifex_ai_project/
├── backend/
│   ├── main.py              # FastAPI backend
│   └── database.db          # SQLite database
├── frontend/
│   └── app.py               # Streamlit frontend
├── requirements.txt         # Python dependencies
├── install_dependencies.py  # Auto installer
└── INSTALLATION.md          # This file
```

### Adding Dependencies
1. Add to `requirements.txt`
2. Update `install_dependencies.py`
3. Test installation

## Support

For issues or questions:
1. Check this installation guide
2. Review error messages in terminal
3. Check backend logs for detailed errors
