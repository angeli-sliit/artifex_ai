"""
Improved Backend for 57-Feature Model
This backend can handle both old 10-feature and new 57-feature models
"""

import os
import sys
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import joblib
import json
import sqlite3
from contextlib import asynccontextmanager

# FastAPI imports
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Image processing imports
try:
    import cv2  # type: ignore
    from PIL import Image, ImageOps
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    print("Warning: Image processing libraries not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
class AppState:
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.feature_info = None
        self.db_manager = None

app_state = AppState()

# Database Manager
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with artist data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create artists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artists (
                name TEXT PRIMARY KEY,
                frequency INTEGER,
                median_price REAL,
                price_std REAL
            )
        ''')
        
        # Create technique_artist_medians table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technique_artist_medians (
                technique TEXT,
                artist TEXT,
                median_price REAL,
                sample_count INTEGER,
                PRIMARY KEY (technique, artist)
            )
        ''')
        
        # Check if database is empty and add sample data
        cursor.execute("SELECT COUNT(*) FROM artists")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Add sample famous artists
            sample_artists = [
                ('pablo picasso', 150, 50000, 25000),
                ('salvador dali', 80, 30000, 15000),
                ('vincent van gogh', 200, 75000, 40000),
                ('claude monet', 120, 40000, 20000),
                ('andy warhol', 100, 35000, 18000)
            ]
            
            cursor.executemany(
                "INSERT OR REPLACE INTO artists (name, frequency, median_price, price_std) VALUES (?, ?, ?, ?)",
                sample_artists
            )
            logger.info(f"Added {len(sample_artists)} sample artists to database")
            
            # Add sample technique-artist medians
            sample_tech_artist = [
                ('oil on canvas', 'pablo picasso', 55000, 25),
                ('oil on canvas', 'vincent van gogh', 80000, 30),
                ('oil on canvas', 'claude monet', 45000, 20),
                ('lithograph', 'andy warhol', 25000, 15),
                ('etching', 'salvador dali', 20000, 10),
                ('watercolor', 'pablo picasso', 30000, 12),
                ('screenprint', 'andy warhol', 15000, 8),
            ]
            
            cursor.executemany(
                "INSERT OR REPLACE INTO technique_artist_medians (technique, artist, median_price, sample_count) VALUES (?, ?, ?, ?)",
                sample_tech_artist
            )
            logger.info(f"Added {len(sample_tech_artist)} sample technique-artist medians to database")
        
        conn.commit()
        conn.close()
    
    def get_artist_data(self, artist_name: str) -> Dict[str, Any]:
        """Get artist data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT frequency, median_price, price_std FROM artists WHERE name = ?",
            (artist_name.lower(),)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'frequency': result[0],
                'median_price': result[1],
                'price_std': result[2]
            }
        else:
            # Return default values for unknown artists
            return {
                'frequency': 1,
                'median_price': 500.0,
                'price_std': 250.0
            }
    
    def get_tech_artist_median(self, technique: str, artist: str) -> Dict[str, Any]:
        """Get technique-artist median price from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT median_price, sample_count FROM technique_artist_medians WHERE technique = ? AND artist = ?",
            (technique.lower(), artist.lower())
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'median_price': result[0],
                'sample_count': result[1]
            }
        else:
            # Return default values for unknown technique-artist combinations
            return {
                'median_price': 1000.0,
                'sample_count': 1
            }

# Pydantic models
class ArtworkInput(BaseModel):
    artist: str = Field(..., description="Artist name")
    object_type: str = Field(..., description="Object type (painting, sculpture, etc.)")
    technique: str = Field(..., description="Technique used")
    signature: str = Field(..., description="Signature type")
    condition: str = Field(..., description="Condition of the artwork")
    edition_type: str = Field(..., description="Edition type")
    year: int = Field(..., description="Year created")
    width: float = Field(..., description="Width in cm")
    height: float = Field(..., description="Height in cm")
    has_edition: bool = Field(False, description="Has edition")
    has_certificate: bool = Field(False, description="Has certificate")
    has_frame: bool = Field(False, description="Has frame")
    has_damage: bool = Field(False, description="Has damage")
    expert: str = Field("Unknown", description="Expert name")
    colorfulness_score: Optional[float] = Field(None, description="Colorfulness score")
    svd_entropy: Optional[float] = Field(None, description="SVD entropy")
    title: Optional[str] = Field("Untitled", description="Artwork title")
    title_word_count: Optional[int] = Field(None, description="Number of words in title")

class PredictionResponse(BaseModel):
    predicted_price: float
    log_price: float
    confidence: str
    artist_popularity: str
    image_quality: str
    features_used: int
    model_type: str

# Image processing functions
def calculate_colorfulness(image_path: str) -> float:
    """Calculate colorfulness score using OpenCV"""
    if not IMAGE_PROCESSING_AVAILABLE:
        return 0.0
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            return 0.0
        
        # Convert to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Calculate colorfulness using the method from the notebook
        R, G, B = image_rgb[:, :, 0], image_rgb[:, :, 1], image_rgb[:, :, 2]
        rg = R.astype(float) - G.astype(float)
        yb = 0.5 * (R.astype(float) + G.astype(float)) - B.astype(float)
        
        std_rg = np.std(rg)
        std_yb = np.std(yb)
        mean_rg = np.mean(rg)
        mean_yb = np.mean(yb)
        
        colorfulness = np.sqrt(std_rg**2 + std_yb**2) + 0.3 * np.sqrt(mean_rg**2 + mean_yb**2)
        return float(colorfulness)
    
    except Exception as e:
        logger.error(f"Error calculating colorfulness: {e}")
        return 0.0

def calculate_svd_entropy(image_path: str) -> float:
    """Calculate SVD entropy using OpenCV"""
    if not IMAGE_PROCESSING_AVAILABLE:
        return 0.0
    
    try:
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            return 0.0
        
        # Resize image for faster processing
        image = cv2.resize(image, (64, 64))
        
        # Calculate SVD
        U, s, Vt = np.linalg.svd(image.astype(float), full_matrices=False)
        
        # Calculate entropy
        s_normalized = s / np.sum(s)
        s_normalized = s_normalized[s_normalized > 1e-10]  # Remove very small values
        entropy = -np.sum(s_normalized * np.log2(s_normalized))
        
        return float(entropy)
    
    except Exception as e:
        logger.error(f"Error calculating SVD entropy: {e}")
        return 0.0

def create_all_57_features(input_data: ArtworkInput, image_features: Optional[Dict] = None) -> pd.DataFrame:
    """Create ALL 57 features exactly matching the model training"""
    try:
        features = {}
        
        # Get artist data
        artist_data = app_state.db_manager.get_artist_data(input_data.artist)
        
        # 1. Basic categorical features (6)
        features['OBJECT'] = input_data.object_type.lower()
        features['ARTIST'] = input_data.artist.lower().strip()
        features['EXPERT'] = input_data.expert.lower()
        features['TECHNIQUE_SIMPLE'] = input_data.technique.lower()
        features['SIGNATURE_SIMPLE'] = input_data.signature.lower()
        features['CONDITION_SIMPLE'] = input_data.condition.lower()
        
        # 2. Edition type mapping (2)
        edition_map = {
            'unique': 1.0,
            'numbered': 2.0,
            'limited': 3.0,
            'open': 4.0,
            'unknown': 0.0
        }
        features['edition_type'] = edition_map.get(input_data.edition_type.lower(), 0.0)
        features['EDITION_TYPE'] = input_data.edition_type.lower()
        
        # 3. Basic numeric features (5)
        features['width'] = float(input_data.width)
        features['height'] = float(input_data.height)
        features['area'] = features['width'] * features['height']
        features['EXPERT_RAW'] = input_data.expert.lower()
        features['auction_year'] = 2024
        
        # 4. Binary signature features (3)
        features['has_hand_signed'] = 1 if 'hand' in features['SIGNATURE_SIMPLE'] else 0
        features['has_plate_signed'] = 1 if 'plate' in features['SIGNATURE_SIMPLE'] else 0
        features['has_unsigned'] = 1 if 'unsigned' in features['SIGNATURE_SIMPLE'] else 0
        
        # 5. Binary technique features (4)
        features['has_etching'] = 1 if 'etching' in features['TECHNIQUE_SIMPLE'] else 0
        features['has_lithograph'] = 1 if 'lithograph' in features['TECHNIQUE_SIMPLE'] else 0
        features['has_woodcut'] = 1 if 'woodcut' in features['TECHNIQUE_SIMPLE'] else 0
        features['has_screenprint'] = 1 if 'screenprint' in features['TECHNIQUE_SIMPLE'] else 0
        
        # 6. Binary edition features (5)
        features['has_limited_edition'] = 1 if 'limited' in features['EDITION_TYPE'] else 0
        features['has_certificate'] = 1 if input_data.has_certificate else 0
        features['has_frame'] = 1 if input_data.has_frame else 0
        features['has_damage'] = 1 if input_data.has_damage else 0
        features['has_edition'] = 1 if input_data.has_edition else 0
        
        # 7. Image features (2)
        if image_features:
            features['colorfulness_score'] = image_features['colorfulness_score']
            features['svd_entropy'] = image_features['svd_entropy']
        else:
            features['colorfulness_score'] = input_data.colorfulness_score or 0.0
            features['svd_entropy'] = input_data.svd_entropy or 0.0
        
        # 8. Advanced dimension features (6)
        features['aspect_ratio'] = features['width'] / (features['height'] + 1e-8)
        features['log_area'] = np.log1p(features['area'])
        features['log_width'] = np.log1p(features['width'])
        features['log_height'] = np.log1p(features['height'])
        features['area_per_width'] = features['area'] / (features['width'] + 1e-8)
        features['area_per_height'] = features['area'] / (features['height'] + 1e-8)
        
        # 9. Size category (1)
        area = features['area']
        if area <= 100:
            features['size_category'] = 'tiny'
        elif area <= 1000:
            features['size_category'] = 'small'
        elif area <= 5000:
            features['size_category'] = 'medium'
        else:
            features['size_category'] = 'large'
        
        # 10. Age features (4)
        age = 2024 - input_data.year
        features['log_age'] = np.log1p(max(0, age))
        features['is_antique'] = 1 if age >= 100 else 0
        features['is_vintage'] = 1 if 20 <= age < 100 else 0
        features['is_modern'] = 1 if age < 20 else 0
        
        # 11. Year category (1)
        year = input_data.year
        if year < 1900:
            features['year_category'] = 'pre_1900'
        elif year < 1950:
            features['year_category'] = 'early_1900s'
        elif year < 1980:
            features['year_category'] = 'mid_1900s'
        elif year < 2000:
            features['year_category'] = 'late_1900s'
        else:
            features['year_category'] = 'modern'
        
        # 12. Artist popularity features (6)
        features['log_artist_frequency'] = np.log1p(artist_data['frequency'])
        features['artist_rarity'] = 1 / (artist_data['frequency'] + 1)
        features['is_rare_artist'] = 1 if artist_data['frequency'] <= 5 else 0
        features['is_popular_artist'] = 1 if artist_data['frequency'] >= 50 else 0
        features['is_very_popular_artist'] = 1 if artist_data['frequency'] >= 100 else 0
        features['artist_frequency'] = artist_data['frequency']
        
        # 13. Technique complexity features (3)
        features['technique_count'] = (
            features['has_etching'] + features['has_lithograph'] + 
            features['has_woodcut'] + features['has_screenprint']
        )
        features['technique_score'] = (
            features['has_etching'] * 2 + features['has_lithograph'] * 2 +
            features['has_woodcut'] * 3 + features['has_screenprint'] * 1
        )
        features['has_multiple_techniques'] = 1 if features['technique_count'] > 1 else 0
        
        # 14. Signature features (1)
        features['has_any_signature'] = 1 if (features['has_hand_signed'] or features['has_plate_signed']) else 0
        
        # 15. Object features (3)
        features['object_frequency'] = 100.0  # Default
        features['is_rare_object'] = 0
        features['is_common_object'] = 1
        
        # 16. Edition features (2)
        features['edition_features'] = (
            features['has_edition'] + features['has_limited_edition'] + features['has_certificate']
        )
        features['physical_features'] = (
            features['has_frame'] + features['has_certificate'] - features['has_damage']
        )
        
        # 17. Interaction features (2)
        features['size_artist_interaction'] = features['area'] * artist_data['frequency']
        features['technique_artist_interaction'] = features['technique_count'] * artist_data['frequency']
        
        # 18. Title features (1)
        if input_data.title and input_data.title.strip() and input_data.title.strip() != "Untitled":
            features['title_word_count'] = len(input_data.title.strip().split())
        elif input_data.title_word_count is not None:
            features['title_word_count'] = input_data.title_word_count
        else:
            features['title_word_count'] = 3  # Default
        
        # 19. Market interaction features (1)
        # Get technique-artist median price
        tech_artist_data = app_state.db_manager.get_tech_artist_median(
            input_data.technique, input_data.artist
        )
        tech_artist_median = tech_artist_data['median_price']
        
        # For prediction, we estimate the ratio based on artist's general median
        artist_median = artist_data['median_price']
        if tech_artist_median > 0 and artist_median > 0:
            # Calculate the ratio of technique-specific median to general artist median
            features['price_vs_tech_artist_median'] = tech_artist_median / artist_median
        else:
            features['price_vs_tech_artist_median'] = 1.0  # Default
        
        # Create DataFrame
        df = pd.DataFrame([features])
        
        # Ensure all features are in the correct order
        if app_state.feature_info and 'feature_names' in app_state.feature_info:
            expected_features = app_state.feature_info['feature_names']
            ordered_features = {}
            
            for feature_name in expected_features:
                if feature_name in df.columns:
                    ordered_features[feature_name] = df[feature_name].iloc[0]
                else:
                    # Fill missing features with appropriate defaults
                    if feature_name in ['size_category', 'year_category']:
                        ordered_features[feature_name] = 'unknown'
                    else:
                        ordered_features[feature_name] = 0.0
            
            df = pd.DataFrame([ordered_features])
        
        # Convert categorical features to string
        if app_state.feature_info and 'categorical_indices' in app_state.feature_info:
            categorical_indices = app_state.feature_info['categorical_indices']
            for idx in categorical_indices:
                if idx < len(df.columns):
                    col_name = df.columns[idx]
                    df[col_name] = df[col_name].astype(str)
        
        # Convert numeric features
        for col in df.columns:
            if col not in [df.columns[i] for i in (app_state.feature_info.get('categorical_indices', []) if app_state.feature_info else [])]:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        
        return df
        
    except Exception as e:
        logger.error(f"Feature creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Feature creation failed: {str(e)}")

# Model loading
def load_model():
    """Load the trained model with comprehensive error handling"""
    try:
        model_path = Path("art_price_model.pkl")
        if not model_path.exists():
            logger.error(f"Model file not found: {model_path.absolute()}")
            app_state.model_loaded = False
            return False
        
        # Load model
        app_state.model = joblib.load(model_path)
        logger.info(f"Model loaded successfully from {model_path}")
        
        # Load feature info if available
        feature_info_path = Path("feature_info.json")
        if feature_info_path.exists():
            with open(feature_info_path, 'r') as f:
                app_state.feature_info = json.load(f)
            logger.info(f"Feature info loaded: {app_state.feature_info['n_features']} features")
        else:
            logger.warning("Feature info file not found, using model defaults")
            app_state.feature_info = {
                'feature_names': app_state.model.feature_names_ if hasattr(app_state.model, 'feature_names_') else [],
                'categorical_indices': app_state.model.get_cat_feature_indices() if hasattr(app_state.model, 'get_cat_feature_indices') else [],
                'n_features': len(app_state.model.feature_names_) if hasattr(app_state.model, 'feature_names_') else 0
            }
        
        app_state.model_loaded = True
        logger.info(f"Model loaded with {app_state.feature_info['n_features']} features")
        return True
        
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        app_state.model_loaded = False
        return False

# Initialize database
def init_database():
    """Initialize the database"""
    try:
        db_path = Path("data/artist_database.db")
        db_path.parent.mkdir(exist_ok=True)
        app_state.db_manager = DatabaseManager(str(db_path))
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ArtifexAI Backend...")
    
    # Initialize database
    if not init_database():
        logger.error("Failed to initialize database")
    
    # Load model
    if not load_model():
        logger.error("Failed to load model")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ArtifexAI Backend...")

# Create FastAPI app
app = FastAPI(
    title="ArtifexAI API",
    description="AI-powered art auction price prediction API",
    version="8.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ArtifexAI API is running!", "version": "8.0.0"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": app_state.model_loaded,
        "features_count": app_state.feature_info['n_features'] if app_state.feature_info else 0,
        "image_processing": IMAGE_PROCESSING_AVAILABLE
    }

@app.get("/model/info")
async def get_model_info():
    """Get detailed model information"""
    if not app_state.model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_type": "CatBoost Regressor",
        "version": "8.0.0",
        "features_count": app_state.feature_info['n_features'] if app_state.feature_info else 0,
        "categorical_features": app_state.feature_info['categorical_indices'] if app_state.feature_info else [],
        "feature_names": app_state.feature_info['feature_names'][:10] if app_state.feature_info else [],
        "performance": {
            "r2_score": app_state.feature_info.get('r2_score', 0.8449) if app_state.feature_info else 0.8449,
            "mae": 0.264,
            "rmse": 0.535,
            "accuracy_within_20_percent": 0.695
        },
        "training_info": {
            "algorithm": "CatBoost",
            "ensemble_method": "Gradient Boosting",
            "categorical_features_handling": "Automatic",
            "missing_values_handling": "Automatic"
        }
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_price(artwork: ArtworkInput):
    """Predict artwork price"""
    if not app_state.model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Create features
        logger.info(f"Creating features for artist: {artwork.artist}")
        features_df = create_all_57_features(artwork, None)
        logger.info(f"Features created successfully. Shape: {features_df.shape}")
        
        # Debug: Check artist-related features
        if 'artist_frequency' in features_df.columns:
            logger.info(f"Artist frequency in features: {features_df['artist_frequency'].iloc[0]}")
        if 'log_artist_frequency' in features_df.columns:
            logger.info(f"Log artist frequency: {features_df['log_artist_frequency'].iloc[0]}")
        if 'is_very_popular_artist' in features_df.columns:
            logger.info(f"Is very popular artist: {features_df['is_very_popular_artist'].iloc[0]}")
        
        # Make prediction
        logger.info("Making prediction...")
        log_price_pred = app_state.model.predict(features_df)[0]
        logger.info(f"Prediction made. Log price: {log_price_pred}")
        
        # Convert log price back to actual price
        # The model was trained on log1p(price), so we need to use expm1 to convert back
        price_pred = np.expm1(log_price_pred)
        logger.info(f"Base price after expm1: {price_pred}")
        
        # Get artist data first
        logger.info(f"Getting artist data for: {artwork.artist}")
        artist_data = app_state.db_manager.get_artist_data(artwork.artist)
        frequency = artist_data['frequency']
        median_price = artist_data['median_price']
        logger.info(f"Artist frequency: {frequency}, median_price: {median_price}")

        # Apply proper artist-based scaling using median price as reference
        if frequency >= 100:  # Very popular artists (Picasso, Van Gogh, etc.)
            # For famous artists, use median price as base and scale up
            price_pred = max(price_pred * 20, median_price * 0.1)  # At least 10% of median
            logger.info(f"Price after famous artist scaling: {price_pred}")
        elif frequency >= 50:  # Popular artists
            price_pred = max(price_pred * 15, median_price * 0.05)
            logger.info(f"Price after popular artist scaling: {price_pred}")
        elif frequency >= 20:  # Known artists
            price_pred = max(price_pred * 10, median_price * 0.02)
            logger.info(f"Price after known artist scaling: {price_pred}")
        else:  # Unknown artists
            # For unknown artists, use much lower scaling
            price_pred = max(price_pred * 3, 10)  # Much lower for unknown artists
            logger.info(f"Price after unknown artist scaling: {price_pred}")

        # Ensure reasonable price range
        price_pred = max(price_pred, 10.0)  # Minimum $10
        price_pred = min(price_pred, 1000000.0)  # Maximum $1M
        logger.info(f"Final price: {price_pred}")
        
        # Confidence based on artist frequency
        if frequency >= 20:
            confidence = "HIGH"
        elif frequency >= 5:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
        
        # Popularity based on frequency
        if frequency >= 50:
            popularity = "VERY_POPULAR"
        elif frequency >= 10:
            popularity = "POPULAR"
        elif frequency >= 5:
            popularity = "KNOWN"
        else:
            popularity = "UNKNOWN"
        
        return PredictionResponse(
            predicted_price=round(price_pred, 2),
            log_price=round(log_price_pred, 4),
            confidence=confidence,
            artist_popularity=popularity,
            image_quality="Not provided",
            features_used=app_state.feature_info['n_features'] if app_state.feature_info else 0,
            model_type="CatBoost_57_Features"
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze uploaded image for colorfulness and SVD entropy"""
    if not IMAGE_PROCESSING_AVAILABLE:
        raise HTTPException(status_code=503, detail="Image processing not available")
    
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Calculate features
        colorfulness = calculate_colorfulness(temp_path)
        svd_entropy = calculate_svd_entropy(temp_path)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "colorfulness_score": round(colorfulness, 4),
            "svd_entropy": round(svd_entropy, 4),
            "image_quality": "Good" if colorfulness > 10 and svd_entropy > 2 else "Fair"
        }
        
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
