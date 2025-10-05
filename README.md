# ArtifexAI - AI-Powered Art Price Predictions

🎨 **Complete AI-powered art valuation system with beautiful Starry Night background and glassmorphism design**

## 🌟 Features

- **🧠 AI-Powered Predictions** - Advanced machine learning model with 84.49% R² score
- **🎨 Beautiful UI** - Starry Night background with glassmorphism design
- **📊 Image Analysis** - Automatic colorfulness and SVD entropy extraction
- **📈 Confidence Ranges** - Evidence-based estimates with uncertainty quantification
- **📄 PDF Export** - Professional report generation
- **🌐 Hugging Face Ready** - Optimized for Hugging Face Spaces deployment
- **🔧 Demo Mode** - Works without backend for UI exploration

## 🚀 Quick Start

### Option 1: Hugging Face Spaces (Recommended)
1. Go to: https://huggingface.co/spaces/angeli2003/ArtifexAI
2. Upload an image and explore the interface
3. No setup required - runs in demo mode

### Option 2: Local Development
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

### Option 3: Docker
```bash
cd frontend
docker build -t artifexai .
docker run -p 8501:8501 artifexai
```

## 📁 Project Structure

```
ArtifexAI_Final/
├── README.md                 # This file
├── frontend/                 # Streamlit application
│   ├── app.py               # Main application (2122 lines)
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Docker configuration
└── docs/                    # Documentation (if needed)
```

## 🎯 Key Optimizations

- ✅ **Fixed localhost:8000 issue** with proper API resolution
- ✅ **Demo mode** for Hugging Face Spaces compatibility
- ✅ **Base64 encoded images** for platform compatibility
- ✅ **Enhanced debugging** and user controls
- ✅ **Beautiful Starry Night background** with gradient overlays
- ✅ **Glassmorphism UI design** with backdrop blur effects

## 🔧 Technical Details

- **Frontend**: Streamlit with custom CSS
- **ML Model**: CatBoost with image features
- **Dataset**: 60,000+ print auction records (2024)
- **Image Analysis**: Colorfulness, SVD Entropy
- **Styling**: Modern dark theme with blue-purple gradients

## 📊 Model Performance

- **R² Score**: 84.49%
- **Features**: 50+ including image analysis
- **Training Data**: 60,000+ auction records
- **Validation**: Cross-validated with confidence intervals

## 🌐 Live Demo

**Hugging Face Spaces**: https://huggingface.co/spaces/angeli2003/ArtifexAI

## 👥 Team

- Fernando W A A T
- Liyanage M L V O  
- Fernando R S R
- Fernando H T D

## 📚 Course

**Fundamentals of Data Mining (IT3051)**  
Sri Lanka Institute of Information Technology

## 🎨 Design Features

- **Starry Night Background** - Van Gogh inspired with gradient overlays
- **Glassmorphism Cards** - Modern glass effect with backdrop blur
- **Responsive Design** - Works on all screen sizes
- **Dark Theme** - Easy on the eyes with blue-purple accents
- **Smooth Animations** - Professional transitions and effects

---

**Version**: v2.2 (HF Spaces Optimized)  
**Status**: ✅ Production Ready  
**Deployment**: Hugging Face Spaces + GitHub