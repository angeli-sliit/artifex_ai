"""
Test script to verify the improved system works correctly
"""
import requests
import time
import sys
from pathlib import Path

def test_improved_system():
    """Test the improved system functionality"""
    print("Testing ArtifexAI Improved System...")
    print("=" * 50)
    
    # Test 1: Backend Health Check
    print("\n1. Testing Backend Health Check...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Backend is healthy")
            print(f"   [INFO] Model loaded: {data['model_loaded']}")
            print(f"   [INFO] Version: {data['version']}")
        else:
            print(f"   [ERROR] Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Backend not accessible: {e}")
        print("   [TIP] Make sure to start the backend: python backend/main_improved.py")
        return False
    
    # Test 2: Model Info
    print("\n2. Testing Model Information...")
    try:
        response = requests.get("http://localhost:8000/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Model info retrieved")
            print(f"   [INFO] Model type: {data['model_type']}")
            print(f"   [INFO] Features: {data['features_count']}")
            print(f"   [INFO] R² Score: {data['performance']['r2_score']}")
        else:
            print(f"   [ERROR] Model info failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Model info error: {e}")
    
    # Test 3: Prediction Test
    print("\n3. Testing Price Prediction...")
    try:
        test_data = {
            "artist": "Pablo Picasso",
            "object_type": "painting",
            "technique": "oil on canvas",
            "signature": "hand signed",
            "condition": "excellent",
            "edition_type": "unique",
            "year": 1907,
            "width": 100.0,
            "height": 80.0,
            "has_edition": False,
            "has_certificate": True,
            "has_frame": True,
            "has_damage": False,
            "expert": "Unknown"
        }
        
        response = requests.post("http://localhost:8000/predict", json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   [OK] Prediction successful")
            print(f"   [INFO] Predicted price: ${data['predicted_price']:,.0f}")
            print(f"   [INFO] Confidence: {data['confidence']}")
            print(f"   [INFO] Features used: {data['features_used']}")
        else:
            print(f"   [ERROR] Prediction failed: {response.status_code}")
            print(f"   [INFO] Error: {response.text}")
    except Exception as e:
        print(f"   [ERROR] Prediction error: {e}")
    
    # Test 4: Input Validation
    print("\n4. Testing Input Validation...")
    try:
        invalid_data = {
            "artist": "",  # Empty artist name
            "object_type": "painting",
            "technique": "oil on canvas",
            "signature": "hand signed",
            "condition": "excellent",
            "edition_type": "unique",
            "year": 1000,  # Invalid year
            "width": -100.0,  # Negative width
            "height": 80.0,
            "has_edition": False,
            "has_certificate": True,
            "has_frame": True,
            "has_damage": False,
            "expert": "Unknown"
        }
        
        response = requests.post("http://localhost:8000/predict", json=invalid_data, timeout=10)
        if response.status_code == 422:  # Validation error
            print(f"   [OK] Input validation working (422 error)")
        else:
            print(f"   [WARNING] Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] Validation test error: {e}")
    
    print("\n" + "=" * 50)
    print("Improved System Test Complete!")
    print("\nNext Steps:")
    print("1. Start the improved frontend: streamlit run frontend/app_improved.py")
    print("2. Open http://localhost:8501 in your browser")
    print("3. Test the full user interface")
    print("\nFor development:")
    print("- Run tests: pytest tests/")
    print("- Check logs in console")
    print("- Review API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    test_improved_system()
