"""
Unit tests for ArtifexAI Backend
"""
import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from main_improved import (
    calculate_colorfulness,
    calculate_svd_entropy,
    process_image_async,
    create_features_matching_model,
    ArtworkInput,
    DatabaseManager
)

class TestImageProcessing:
    """Test image processing functions"""
    
    def test_calculate_colorfulness_valid_image(self):
        """Test colorfulness calculation with valid image"""
        # Create a test image array
        image_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        result = calculate_colorfulness(image_array)
        assert isinstance(result, float)
        assert result >= 0
    
    def test_calculate_colorfulness_empty_image(self):
        """Test colorfulness calculation with empty image"""
        result = calculate_colorfulness(None)
        assert result == 0.0
    
    def test_calculate_svd_entropy_valid_image(self):
        """Test SVD entropy calculation with valid image"""
        image_array = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        result = calculate_svd_entropy(image_array)
        assert isinstance(result, float)
        assert result >= 0
    
    def test_calculate_svd_entropy_empty_image(self):
        """Test SVD entropy calculation with empty image"""
        result = calculate_svd_entropy(None)
        assert result == 0.0

class TestFeatureEngineering:
    """Test feature engineering functions"""
    
    def test_create_features_basic(self):
        """Test basic feature creation"""
        artwork = ArtworkInput(
            artist="Pablo Picasso",
            object_type="painting",
            technique="oil on canvas",
            signature="hand signed",
            condition="excellent",
            edition_type="unique",
            year=1907,
            width=100.0,
            height=80.0
        )
        
        with patch('main_improved.db_manager') as mock_db:
            mock_db.get_artist_data.return_value = {
                'frequency': 10,
                'median_price': 1000.0,
                'price_std': 500.0
            }
            
            features_df = create_features_matching_model(artwork)
            
            assert isinstance(features_df, pd.DataFrame)
            assert len(features_df) == 1
            assert 'width' in features_df.columns
            assert 'height' in features_df.columns
            assert 'area' in features_df.columns

class TestPydanticModels:
    """Test Pydantic model validation"""
    
    def test_artwork_input_valid(self):
        """Test valid artwork input"""
        artwork = ArtworkInput(
            artist="Pablo Picasso",
            object_type="painting",
            technique="oil on canvas",
            signature="hand signed",
            condition="excellent",
            edition_type="unique",
            year=1907,
            width=100.0,
            height=80.0
        )
        assert artwork.artist == "Pablo Picasso"
        assert artwork.year == 1907
    
    def test_artwork_input_invalid_year(self):
        """Test invalid year validation"""
        with pytest.raises(ValueError):
            ArtworkInput(
                artist="Pablo Picasso",
                object_type="painting",
                technique="oil on canvas",
                signature="hand signed",
                condition="excellent",
                edition_type="unique",
                year=1000,  # Too old
                width=100.0,
                height=80.0
            )
    
    def test_artwork_input_invalid_dimensions(self):
        """Test invalid dimensions validation"""
        with pytest.raises(ValueError):
            ArtworkInput(
                artist="Pablo Picasso",
                object_type="painting",
                technique="oil on canvas",
                signature="hand signed",
                condition="excellent",
                edition_type="unique",
                year=1907,
                width=-100.0,  # Negative width
                height=80.0
            )

class TestDatabaseManager:
    """Test database management"""
    
    def test_database_manager_init(self):
        """Test database manager initialization"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value.__enter__.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            db_manager = DatabaseManager(":memory:")
            assert db_manager.db_path == ":memory:"

if __name__ == "__main__":
    pytest.main([__file__])
