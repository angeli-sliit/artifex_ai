"""
Fix Model Saving Script for Google Colab
Run this after training your model in the notebook
"""

import joblib
import json
from pathlib import Path

def fix_model_saving(best_model, best_model_name, best_r2, X_train_cb, X_train_sk, categorical_cols):
    """
    Properly save the model with all 57 features and feature information
    """
    print("🔧 Fixing model saving with ALL features...")
    print(f"Best model: {best_model_name}")
    print(f"R² Score: {best_r2:.4f}")

    # Create artifacts directory
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(exist_ok=True)

    # Save the model
    model_path = artifacts_dir / "art_price_model.pkl"
    joblib.dump(best_model, model_path)
    print(f"✅ Model saved to: {model_path}")

    # Get feature information based on the best model
    if best_model_name == 'catboost':
        feature_names = X_train_cb.columns.tolist()
        categorical_indices = [i for i, col in enumerate(X_train_cb.columns) if col in categorical_cols]
        print(f"CatBoost features: {len(feature_names)}")
        print(f"Categorical features: {len(categorical_indices)}")
    else:
        feature_names = X_train_sk.columns.tolist()
        categorical_indices = []
        print(f"Sklearn features: {len(feature_names)}")

    # Save feature information
    feature_info = {
        'feature_names': feature_names,
        'categorical_indices': categorical_indices,
        'n_features': len(feature_names),
        'model_type': best_model_name,
        'target_transformation': 'log1p',
        'inverse_transformation': 'expm1',
        'r2_score': best_r2,
        'categorical_columns': categorical_cols
    }

    feature_info_path = artifacts_dir / "feature_info.json"
    with open(feature_info_path, 'w') as f:
        json.dump(feature_info, f, indent=2)
    print(f"✅ Feature info saved to: {feature_info_path}")

    # Save preprocessor (same as model for now)
    preprocessor_path = artifacts_dir / "preprocessor.pkl"
    joblib.dump(best_model, preprocessor_path)
    print(f"✅ Preprocessor saved to: {preprocessor_path}")

    print(f"\n📊 Model details:")
    print(f"  Features: {len(feature_names)}")
    print(f"  Categorical features: {len(categorical_indices)}")
    print(f"  R² Score: {best_r2:.4f}")
    print(f"  Model type: {best_model_name}")

    # Show first 10 features
    print(f"\n🔍 First 10 features:")
    for i, feature in enumerate(feature_names[:10]):
        print(f"  {i}: {feature}")

    # Show categorical features
    if categorical_indices:
        print(f"\n🏷️ Categorical features:")
        for i, idx in enumerate(categorical_indices[:10]):
            print(f"  {idx}: {feature_names[idx]}")

    print(f"\n✅ Model saving fixed! All {len(feature_names)} features are now properly saved.")
    
    return model_path, feature_info_path, preprocessor_path

# Instructions for Google Colab:
print("""
🚀 INSTRUCTIONS FOR GOOGLE COLAB:

1. After training your model in the notebook, run this cell:

# Copy and paste this code into a new cell in your notebook:
exec(open('fix_model_saving.py').read())

# Then run this to fix the model saving:
model_path, feature_info_path, preprocessor_path = fix_model_saving(
    best_model, best_model_name, best_r2, X_train_cb, X_train_sk, categorical_cols
)

2. Download the files:
from google.colab import files
files.download('artifacts/art_price_model.pkl')
files.download('artifacts/feature_info.json')
files.download('artifacts/preprocessor.pkl')

3. Upload these files to your project's artifacts folder
""")
