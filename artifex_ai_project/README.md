# 🎨 ArtifexAI - Advanced Art Auction Price Predictor with Image Analysis

## 🚀 **Production-Ready Art Price Prediction System**

A sophisticated machine learning system that predicts art auction prices using advanced image analysis, artist data, and comprehensive feature engineering.

### ✨ **Key Features**

#### 🎯 **Core Functionality**
- ✅ **Price Prediction**: Accurate art auction price estimation
- ✅ **Image Analysis**: Automatic colorfulness and SVD entropy calculation
- ✅ **Artist Database**: Comprehensive artist popularity tracking
- ✅ **Feature Engineering**: 57+ engineered features for optimal accuracy

#### 🔧 **Technical Excellence**
- ✅ **Machine Learning**: CatBoost model with 84.5% R² score
- ✅ **Image Processing**: OpenCV-based image feature extraction
- ✅ **API Architecture**: FastAPI backend with Streamlit frontend
- ✅ **Database Integration**: SQLite for artist data management

#### 🏗️ **Production Ready**
- ✅ **Docker Support**: Complete containerization
- ✅ **Error Handling**: Comprehensive error management
- ✅ **Type Safety**: Full type hints and validation
- ✅ **Testing**: Unit and integration tests

---

## 📁 **Project Structure**

```
artifex_ai_project/
├── backend/
│   ├── main.py                   # FastAPI backend application
│   ├── config.py                 # Configuration management
│   ├── requirements.txt          # Backend dependencies
│   └── Dockerfile               # Backend containerization
├── frontend/
│   ├── app.py                   # Streamlit frontend application
│   ├── requirements.txt         # Frontend dependencies
│   └── Dockerfile               # Frontend containerization
├── data/
│   ├── art_price_model.pkl      # Trained CatBoost model
│   ├── feature_info.json        # Model feature information
│   ├── preprocessor.pkl         # Data preprocessor
│   └── artist_database.db       # Artist popularity database
├── scripts/
│   ├── start_backend.ps1        # Backend startup script
│   ├── start_frontend.ps1       # Frontend startup script
│   └── start_all.ps1            # Complete system startup
├── tests/
│   ├── test_backend.py          # Backend unit tests
│   └── requirements.txt         # Test dependencies
├── show_10_artists_results.py   # Prediction testing script
├── find_price_rows.py           # Data analysis script
├── docker-compose.yml           # Docker orchestration
├── env.example                  # Environment configuration
└── README.md                    # This file
```

---

## 🚀 **Quick Start**

### **Option 1: Complete System (Recommended)**
```powershell
# Start both backend and frontend
.\scripts\start_all.ps1
```

### **Option 2: Individual Services**
```powershell
# Terminal 1 - Backend
.\scripts\start_backend.ps1

# Terminal 2 - Frontend  
.\scripts\start_frontend.ps1
```

### **Option 3: Docker**
```bash
# Start with Docker Compose
docker-compose up --build
```

---

## 🎯 **Model Performance**

### **Accuracy Metrics**
- **R² Score**: 84.5% (Excellent)
- **Average Error**: 60.6%
- **High-Value Art**: 65% accuracy (FAIR)
- **Famous Artists**: 61% accuracy (FAIR)

### **Prediction Examples**
- **Pablo Picasso**: 22.2% error (GOOD)
- **Joan Miro**: 36.3% error (GOOD)
- **Marc Chagall**: 61.3% error (FAIR)

---

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file based on `env.example`:

```bash
# API Configuration
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:8501

# Model Paths
MODEL_PATH=../../art_auction_project/artifacts/art_price_model.pkl

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/jpg
```

---

## 🧪 **Testing**

### **Run Tests**
```powershell
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_backend.py -v
```

### **Test Prediction System**
```powershell
# Test with 10 random artists
python show_10_artists_results.py
```

---

## 🔒 **Security Features**

- ✅ **Input Validation**: All inputs validated and sanitized
- ✅ **File Upload Security**: Size limits and type checking
- ✅ **CORS Protection**: Restricted to allowed origins
- ✅ **Error Handling**: Sanitized error messages

---

## 📊 **API Endpoints**

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

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Backend Won't Start**
```powershell
# Check model path
python -c "from pathlib import Path; print(Path('../../art_auction_project/artifacts/art_price_model.pkl').exists())"

# Check dependencies
pip install -r backend/requirements.txt
```

#### **Frontend Connection Error**
```python
# Check API health
import requests
response = requests.get("http://localhost:8000/health")
print(response.json())
```

#### **Prediction Errors**
```powershell
# Test prediction system
python show_10_artists_results.py
```

---

## 🎉 **Features**

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

## 🚀 **Deployment**

### **Production Deployment**
1. **Environment Setup**: Configure `.env` file
2. **Model Preparation**: Ensure model files are available
3. **Database Setup**: Initialize artist database
4. **Service Start**: Run startup scripts
5. **Health Check**: Verify all services

### **Docker Deployment**
```bash
# Build and run
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 📈 **Performance**

### **System Requirements**
- **Python**: 3.8+
- **Memory**: 4GB+ RAM
- **Storage**: 2GB+ free space
- **CPU**: Multi-core recommended

### **Optimization**
- **Model Caching**: Loaded once at startup
- **Async Processing**: Non-blocking operations
- **Connection Pooling**: Efficient database access
- **Memory Management**: Proper resource cleanup

---

## 🎨 **ArtifexAI - Where Art Meets AI!**

**Advanced Art Auction Price Predictor with Image Analysis**

*Built with ❤️ for the art community*
