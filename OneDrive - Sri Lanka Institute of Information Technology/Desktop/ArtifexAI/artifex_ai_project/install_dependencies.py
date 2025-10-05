#!/usr/bin/env python3
"""
ArtifexAI Dependency Installer
Installs required dependencies for the ArtifexAI project
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    print("🎨 ArtifexAI - Installing Dependencies")
    print("=" * 50)
    
    # Core dependencies
    core_packages = [
        "streamlit>=1.28.0",
        "requests>=2.31.0", 
        "Pillow>=10.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0"
    ]
    
    # Backend dependencies
    backend_packages = [
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6"
    ]
    
    # ML dependencies
    ml_packages = [
        "scikit-learn>=1.3.0",
        "catboost>=1.2.0",
        "joblib>=1.3.0"
    ]
    
    # Optional dependencies
    optional_packages = [
        "reportlab>=4.0.0"  # For PDF generation
    ]
    
    print("\n📦 Installing core dependencies...")
    for package in core_packages:
        install_package(package)
    
    print("\n🔧 Installing backend dependencies...")
    for package in backend_packages:
        install_package(package)
    
    print("\n🤖 Installing ML dependencies...")
    for package in ml_packages:
        install_package(package)
    
    print("\n📄 Installing optional dependencies...")
    for package in optional_packages:
        install_package(package)
    
    print("\n" + "=" * 50)
    print("🎉 Installation complete!")
    print("\nTo run the application:")
    print("1. Backend: cd backend && python main.py")
    print("2. Frontend: cd frontend && streamlit run app.py")
    print("\nNote: If you encounter any issues, try:")
    print("pip install --upgrade pip")
    print("pip install -r requirements.txt")

if __name__ == "__main__":
    main()
