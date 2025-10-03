"""
ArtifexAI Enhanced Frontend - IMPROVED VERSION
Fixed error handling, validation, and security issues
"""

import streamlit as st
import requests
import json
from typing import Dict, Any, Optional
import time
import io
from PIL import Image
import base64
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="ArtifexAI - Enhanced Art Auction Price Predictor",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration
class FrontendConfig:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
    REQUEST_TIMEOUT = 30
    RETRY_ATTEMPTS = 3

config = FrontendConfig()

# Custom CSS with improved styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #A23B72;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2E86AB;
    }
    .prediction-box {
        background-color: #e8f4fd;
        padding: 2rem;
        border-radius: 1rem;
        border: 2px solid #2E86AB;
        text-align: center;
        margin: 2rem 0;
    }
    .stButton > button {
        background-color: #2E86AB;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #A23B72;
        color: white;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff4444;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #44ff44;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .image-upload-area {
        border: 2px dashed #2E86AB;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .feature-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# API endpoints
API_ENDPOINTS = {
    "health": f"{config.API_BASE_URL}/health",
    "predict": f"{config.API_BASE_URL}/predict",
    "analyze_image": f"{config.API_BASE_URL}/analyze-image",
    "model_info": f"{config.API_BASE_URL}/model/info"
}

def validate_image_file(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded image file"""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size
    if uploaded_file.size > config.MAX_FILE_SIZE:
        return False, f"File too large. Maximum size: {config.MAX_FILE_SIZE // (1024*1024)}MB"
    
    # Check file type
    if uploaded_file.type not in config.ALLOWED_IMAGE_TYPES:
        return False, f"Invalid file type. Allowed: {', '.join(config.ALLOWED_IMAGE_TYPES)}"
    
    return True, "Valid file"

def check_api_health() -> Dict[str, Any]:
    """Check if the API is running and healthy with retry logic"""
    for attempt in range(config.RETRY_ATTEMPTS):
        try:
            response = requests.get(API_ENDPOINTS["health"], timeout=5)
            if response.status_code == 200:
                return {"status": "healthy", "data": response.json()}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except requests.exceptions.ConnectionError:
            if attempt < config.RETRY_ATTEMPTS - 1:
                time.sleep(1)  # Wait before retry
                continue
            return {"status": "offline", "error": "Cannot connect to API"}
        except requests.exceptions.Timeout:
            return {"status": "timeout", "error": "API request timed out"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    return {"status": "offline", "error": "API connection failed after retries"}

def analyze_image(image_file) -> Dict[str, Any]:
    """Send image for analysis to API with proper error handling"""
    try:
        # Validate file first
        is_valid, error_msg = validate_image_file(image_file)
        if not is_valid:
            return {"success": False, "error": error_msg}
        
        files = {"file": image_file}
        response = requests.post(
            API_ENDPOINTS["analyze_image"],
            files=files,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False, 
                "error": f"Image Analysis Error: {response.status_code} - {response.text}"
            }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Is the backend running?"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def predict_price(artwork_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send prediction request to API with proper error handling"""
    try:
        response = requests.post(
            API_ENDPOINTS["predict"],
            json=artwork_data,
            timeout=config.REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 422:
            # Validation error
            try:
                error_data = response.json()
                return {"success": False, "error": f"Validation Error: {error_data}"}
            except:
                return {"success": False, "error": "Validation Error: Invalid input data"}
        else:
            return {
                "success": False, 
                "error": f"API Error: {response.status_code} - {response.text}"
            }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Is the backend running?"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def display_error(error_msg: str, error_type: str = "error"):
    """Display error message with appropriate styling"""
    if error_type == "error":
        st.markdown(f'<div class="error-box">❌ {error_msg}</div>', unsafe_allow_html=True)
    elif error_type == "warning":
        st.markdown(f'<div class="warning-box">⚠️ {error_msg}</div>', unsafe_allow_html=True)
    else:
        st.error(error_msg)

def display_success(success_msg: str):
    """Display success message"""
    st.markdown(f'<div class="success-box">✅ {success_msg}</div>', unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🎨 ArtifexAI Enhanced</h1>', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Advanced Art Auction Price Predictor with Image Analysis</h2>', unsafe_allow_html=True)
    
    # Check API health
    with st.spinner("Checking API connection..."):
        health_status = check_api_health()
    
    # Display API status
    if health_status["status"] == "healthy":
        display_success("Backend API is running and healthy")
        model_loaded = health_status["data"]["model_loaded"]
        if model_loaded:
            st.success("🤖 AI Model loaded and ready for predictions")
        else:
            display_error("Model not loaded - predictions may not be accurate", "warning")
    else:
        display_error(f"Backend API is {health_status['status']}: {health_status['error']}")
        st.error("Please start the backend API first: `python backend/main_improved.py`")
        return
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Artwork Details", "📸 Image Analysis", "🔮 Prediction Results", "📊 System Info"])
    
    with tab1:
        st.markdown("### 📝 Complete Artwork Information")
        
        # Create form with all required features
        with st.form("enhanced_artwork_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Basic Information")
                artist = st.text_input(
                    "Artist Name", 
                    value="Pablo Picasso", 
                    help="Enter the artist's full name",
                    max_chars=100
                )
                object_type = st.selectbox(
                    "Object Type", 
                    ["painting", "drawing", "print", "sculpture", "photograph", "other"],
                    help="Type of artwork"
                )
                technique = st.selectbox(
                    "Technique", 
                    ["oil on canvas", "watercolor", "etching", "lithograph", "woodcut", "screenprint", "painting", "other"],
                    help="Artistic technique used"
                )
                signature = st.selectbox(
                    "Signature", 
                    ["hand signed", "plate signed", "unsigned", "unknown"],
                    help="Signature type"
                )
                condition = st.selectbox(
                    "Condition", 
                    ["excellent", "very good", "good", "fair", "poor"],
                    help="Physical condition of the artwork"
                )
                edition_type = st.selectbox(
                    "Edition Type", 
                    ["unique", "numbered", "limited", "open", "unknown"],
                    help="Edition information"
                )
                
                st.markdown("#### Physical Dimensions")
                year = st.number_input(
                    "Year Created", 
                    min_value=1200, 
                    max_value=2024, 
                    value=1950, 
                    help="Year the artwork was created"
                )
                width = st.number_input(
                    "Width (cm)", 
                    min_value=0.1, 
                    max_value=1000.0, 
                    value=50.0, 
                    step=0.1, 
                    help="Width in centimeters"
                )
                height = st.number_input(
                    "Height (cm)", 
                    min_value=0.1, 
                    max_value=1000.0, 
                    value=60.0, 
                    step=0.1, 
                    help="Height in centimeters"
                )
            
            with col2:
                st.markdown("#### Physical Attributes")
                has_edition = st.checkbox("Has Edition Information", help="Does the artwork have edition details?")
                has_certificate = st.checkbox("Has Certificate of Authenticity", help="Does it come with a COA?")
                has_frame = st.checkbox("Has Frame", help="Is the artwork framed?")
                has_damage = st.checkbox("Has Damage", help="Does the artwork have any damage?")
                
                st.markdown("#### Additional Information")
                title = st.text_input("Title (Optional)", value="Untitled", help="Artwork title", max_chars=200)
                expert = st.text_input("Expert/Appraiser", value="Unknown", help="Name of the expert or appraiser", max_chars=100)
                
                st.markdown("#### Image Features (Optional)")
                st.info("💡 Upload an image in the 'Image Analysis' tab to automatically calculate colorfulness and SVD entropy")
                colorfulness_score = st.number_input(
                    "Colorfulness Score", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=0.0, 
                    step=0.01, 
                    help="Image colorfulness (0-1000)"
                )
                svd_entropy = st.number_input(
                    "SVD Entropy", 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=0.0, 
                    step=0.01, 
                    help="Image complexity measure"
                )
            
            submitted = st.form_submit_button("🔮 Predict Price", use_container_width=True)
    
    with tab2:
        st.markdown("### 📸 Image Analysis")
        st.markdown("Upload an image of your artwork to automatically calculate visual features that improve prediction accuracy.")
        
        # Image upload area
        st.markdown('<div class="image-upload-area">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg'],
            help=f"Upload a clear image of your artwork (max {config.MAX_FILE_SIZE // (1024*1024)}MB)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        if uploaded_file is not None:
            # Validate file
            is_valid, error_msg = validate_image_file(uploaded_file)
            if not is_valid:
                display_error(error_msg)
            else:
                # Display uploaded image
                try:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_container_width=True)
                    
                    # Analyze image
                    if st.button("🔍 Analyze Image", use_container_width=True):
                        with st.spinner("Analyzing image features..."):
                            # Reset file pointer
                            uploaded_file.seek(0)
                            analysis_result = analyze_image(uploaded_file)
                        
                        if analysis_result["success"]:
                            data = analysis_result["data"]
                            display_success("Image analysis completed!")
                            
                            # Display results
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Colorfulness Score", f"{data['colorfulness_score']:.2f}")
                            with col2:
                                st.metric("SVD Entropy", f"{data['svd_entropy']:.2f}")
                            
                            # Store results in session state
                            st.session_state['image_features'] = data
                            st.info("💡 These values have been automatically filled in the Artwork Details form!")
                        else:
                            display_error(f"Image analysis failed: {analysis_result['error']}")
                except Exception as e:
                    display_error(f"Error processing image: {str(e)}")
        
        # Display current image features
        if 'image_features' in st.session_state:
            st.markdown("#### Current Image Features")
            features = st.session_state['image_features']
            st.json(features)
    
    with tab3:
        st.markdown("### 🔮 Prediction Results")
        
        if submitted:
            # Validate required fields
            if not artist.strip():
                display_error("Artist name is required")
                return
            
            # Get image features from session state if available
            image_features = st.session_state.get('image_features', None)
            
            # Create input data dictionary with all required features
            input_data = {
                "artist": artist.strip(),
                "object_type": object_type,
                "technique": technique,
                "signature": signature,
                "condition": condition,
                "edition_type": edition_type,
                "year": year,
                "width": width,
                "height": height,
                "has_edition": has_edition,
                "has_certificate": has_certificate,
                "has_frame": has_frame,
                "has_damage": has_damage,
                "expert": expert.strip()
            }
            
            # Add image features if available
            if image_features:
                input_data["colorfulness_score"] = image_features["colorfulness_score"]
                input_data["svd_entropy"] = image_features["svd_entropy"]
            elif colorfulness_score > 0 or svd_entropy > 0:
                input_data["colorfulness_score"] = colorfulness_score
                input_data["svd_entropy"] = svd_entropy
            
            # Make prediction
            with st.spinner("Making prediction with all 57 features..."):
                prediction_result = predict_price(input_data)
            
            if prediction_result["success"]:
                data = prediction_result["data"]
                
                # Display main prediction
                st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                st.markdown(f"### 💰 Predicted Price")
                st.markdown(f"# ${data['predicted_price']:,.0f}")
                st.markdown(f"*Log-space prediction: {data['log_price']:.3f}*")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Detailed metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Confidence", data['confidence'], "High" if data['confidence'] == "High" else "")
                with col2:
                    st.metric("Artist Popularity", data['artist_popularity'], "")
                with col3:
                    st.metric("Features Used", data['features_used'], "Total")
                with col4:
                    st.metric("Model R²", "84.49%", "")
                
                # Price range estimation
                price_pred = data['predicted_price']
                price_lower = price_pred * 0.8
                price_upper = price_pred * 1.2
                st.info(f"📊 **Estimated Price Range:** ${price_lower:,.0f} - ${price_upper:,.0f}")
                
                # Additional information
                st.markdown("#### 🧮 Additional Information")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Artist Frequency", data.get('artist_popularity', 'Unknown'))
                    st.metric("Confidence Level", data.get('confidence', 'Unknown'))
                with col2:
                    st.metric("Image Quality", data.get('image_quality', 'Not provided'))
                    st.metric("Model Type", data.get('model_type', 'CatBoost'))
                
            else:
                display_error(f"Prediction failed: {prediction_result['error']}")
    
    with tab4:
        st.markdown("### 📊 System Information")
        
        # API Health
        st.markdown("#### 🔧 API Status")
        if health_status["status"] == "healthy":
            st.success("🟢 API Online")
            if health_status["data"]["model_loaded"]:
                st.success("🟢 Model Loaded")
            else:
                st.warning("🟡 Model Not Loaded")
        else:
            st.error("🔴 API Offline")
        
        # Configuration
        st.markdown("#### ⚙️ Configuration")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("API Base URL", config.API_BASE_URL)
            st.metric("Max File Size", f"{config.MAX_FILE_SIZE // (1024*1024)}MB")
        with col2:
            st.metric("Request Timeout", f"{config.REQUEST_TIMEOUT}s")
            st.metric("Retry Attempts", config.RETRY_ATTEMPTS)
        
        # Features used
        st.markdown("#### 📊 Features Used")
        st.markdown("""
        **57 Total Features:**
        - 6 Categorical features
        - 51 Numeric features
        - Image analysis (2 features)
        - Artist popularity (5 features)
        - Physical attributes (4 features)
        - Advanced calculations (40+ features)
        """)
    
    # Sidebar with system status
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        
        # API Health
        if health_status["status"] == "healthy":
            st.success("🟢 API Online")
        else:
            st.error("🔴 API Offline")
        
        # Model Status
        if health_status["status"] == "healthy":
            if health_status["data"]["model_loaded"]:
                st.success("🟢 Model Loaded")
            else:
                st.warning("🟡 Model Not Loaded")
        
        # Instructions
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Fill Details**: Complete all artwork information
        2. **Upload Image**: Optional but recommended
        3. **Analyze Image**: Get automatic visual features
        4. **Predict**: Click "Predict Price"
        5. **View Results**: See detailed prediction
        """)
        
        # Error reporting
        st.markdown("### 🐛 Error Reporting")
        if st.button("Report Issue"):
            st.info("Please check the console logs and API documentation for troubleshooting.")

if __name__ == "__main__":
    main()
