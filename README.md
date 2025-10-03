# 🎨 ArtifexAI - Complete Art Auction Price Prediction System

## 🚀 **Project Overview**

This repository contains a complete art auction price prediction system with two main components:

1. **`art_auction_project/`** - Data analysis, preprocessing, and model training
2. **`artifex_ai_project/`** - Production web application with FastAPI backend and Streamlit frontend

---

## 📁 **Repository Structure**

```
ArtifexAI/
├── art_auction_project/          # Data Science & ML Pipeline
│   ├── 1_eda.ipynb              # Exploratory Data Analysis
│   ├── 2_preprocess_v2.ipynb    # Data Preprocessing
│   ├── 3_model _v5.ipynb        # Model Training & Evaluation
│   ├── artifacts/               # Trained Models & Preprocessors
│   ├── data/                    # Processed Datasets
│   └── auction/                 # Raw Auction Data
└── artifex_ai_project/          # Production Web Application
    ├── backend/                 # FastAPI Backend
    ├── frontend/                # Streamlit Frontend
    ├── data/                    # Model Files & Database
    ├── scripts/                 # Startup Scripts
    └── tests/                   # Test Suite
```

---

## 🎯 **Key Features**

### **Data Science Pipeline** (`art_auction_project/`)
- ✅ **Exploratory Data Analysis**: Comprehensive data exploration
- ✅ **Data Preprocessing**: Advanced feature engineering (57+ features)
- ✅ **Model Training**: CatBoost, XGBoost, Random Forest, Stacking
- ✅ **Image Analysis**: Colorfulness, SVD entropy, quality assessment
- ✅ **Performance**: 84.5% R² score, 60.6% average error

### **Production Web App** (`artifex_ai_project/`)
- ✅ **FastAPI Backend**: RESTful API with image processing
- ✅ **Streamlit Frontend**: Interactive web interface
- ✅ **Docker Support**: Complete containerization
- ✅ **Database Integration**: SQLite artist database
- ✅ **Real-time Predictions**: Live price estimation

---

## 🚀 **Quick Start**

### **Option 1: Run Web Application (Recommended)**
```bash
cd artifex_ai_project
docker-compose up --build
```

### **Option 2: Manual Setup**
```bash
# Backend
cd artifex_ai_project/backend
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd artifex_ai_project/frontend
pip install -r requirements.txt
streamlit run app.py
```

### **Option 3: Data Science Pipeline**
```bash
cd art_auction_project
jupyter notebook
# Open and run: 1_eda.ipynb → 2_preprocess_v2.ipynb → 3_model _v5.ipynb
```

---

## 📊 **Model Performance**

### **Accuracy Metrics**
- **R² Score**: 84.5% (Excellent)
- **Average Error**: 40.6%
- **High-Value Art**: 65% accuracy 
- **Famous Artists**: 61% accuracy 

### **Prediction Examples**
- **Pablo Picasso**: 22.2% error
- **Joan Miro**: 36.3% error 
- **Marc Chagall**: 41.3% error 

---

## 🔧 **Technical Stack**

### **Data Science**
- **Python**: 3.8+
- **Libraries**: pandas, numpy, scikit-learn, catboost, xgboost
- **Visualization**: matplotlib, seaborn, plotly
- **Image Processing**: OpenCV, PIL

### **Web Application**
- **Backend**: FastAPI, SQLite, Pydantic
- **Frontend**: Streamlit, requests
- **Deployment**: Docker, Docker Compose
- **Testing**: pytest

---

## 📈 **Project Workflow**

1. **Data Collection**: Raw auction data from Excel files
2. **Exploration**: EDA notebooks for data understanding
3. **Preprocessing**: Feature engineering and data cleaning
4. **Model Training**: Multiple algorithms and ensemble methods
5. **Web Development**: FastAPI backend and Streamlit frontend
6. **Deployment**: Docker containerization and production setup

---

## 🎨 **Features**

### **Image Analysis**
- **Colorfulness Score**: Automatic color analysis
- **SVD Entropy**: Image complexity measurement
- **Aspect Ratio**: Dimension analysis
- **Quality Assessment**: Image quality scoring

### **Artist Intelligence**
- **Popularity Tracking**: Artist frequency analysis
- **Rarity Scoring**: Artist rarity assessment
- **Price History**: Historical price analysis
- **Database Integration**: Comprehensive artist data

### **Advanced Features**
- **57+ Features**: Comprehensive feature engineering
- **Dynamic Scaling**: Price range-based scaling
- **Threading**: Concurrent image processing
- **Caching**: Optimized performance

---

## 🔗 **API Endpoints**

### **Backend API** (http://localhost:8000)
- `POST /predict` - Predict art price
- `POST /analyze-image` - Analyze image features
- `GET /health` - Health check
- `GET /model/info` - Model information
- `GET /docs` - API documentation

### **Frontend** (http://localhost:8501)
- Interactive web interface
- Image upload with drag & drop
- Real-time price predictions
- Artist database integration

---

## 🧪 **Testing**

```bash
# Test web application
cd artifex_ai_project
python show_10_artists_results.py

# Run unit tests
pytest tests/
```

---

## 🚀 **Deployment**

### **Docker Deployment**
```bash
# Complete system
docker-compose up --build -d

# Individual services
docker-compose up backend
docker-compose up frontend
```

### **Production Deployment**
1. Configure environment variables
2. Set up model files
3. Initialize database
4. Deploy with Docker

---

## 📚 **Documentation**

- **Data Science**: See notebooks in `art_auction_project/`
- **Web Application**: See README in `artifex_ai_project/`
- **API Documentation**: http://localhost:8000/docs
- **Model Information**: http://localhost:8000/model/info

---

## 🎉 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🎨 **ArtifexAI - Where Art Meets AI!**

**Advanced Art Auction Price Predictor with Image Analysis**

*Built with ❤️ for the art community*

---


- **GitHub**: [angeli-sliit](https://github.com/angeli-sliit)
- **Repository**: [ArtifexAI](https://github.com/angeli-sliit/artifexAI)
