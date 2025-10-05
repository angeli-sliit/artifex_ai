"""
Test 10 Random Artists - Actual vs Predicted Values
"""

import pandas as pd
import numpy as np
import requests
import json

def test_10_artists_predictions():
    """Test 10 random artists with actual vs predicted values"""
    print("TESTING 10 RANDOM ARTISTS - ACTUAL vs PREDICTED VALUES")
    print("=" * 80)
    
    # Read the Excel file
    try:
        df = pd.read_excel('C:/Users/angel/OneDrive - Sri Lanka Institute of Information Technology/Desktop/ArtifexAI/art_auction_project/auction/auction/results_2024_05_11.xlsx')
        print(f"Successfully loaded Excel file with {len(df)} rows")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    # Target prices
    target_prices = [8000, 5000, 2000, 1000, 500, 250, 100, 75, 50, 25]
    
    # Find rows with these exact prices
    found_rows = {}
    
    for price in target_prices:
        price_rows = df[df['PRICE'] == price]
        if len(price_rows) > 0:
            random_row = price_rows.sample(n=1).iloc[0]
            found_rows[price] = random_row
    
    print(f"Found {len(found_rows)} rows with target prices")
    
    # Test backend connection
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("Backend is running. Testing predictions...")
        else:
            print("Backend not responding properly")
            return
    except:
        print("Backend not running. Please start it first:")
        print("  .\\scripts\\start_backend.ps1")
        return
    
    print("\n" + "=" * 80)
    print("RANDOM 10 ARTISTS PREDICTION TEST RESULTS")
    print("=" * 80)
    
    results = []
    
    for price, row in found_rows.items():
        print(f"\n{'='*60}")
        print(f"TESTING: ${price} - {row.get('ARTIST', 'Unknown Artist')}")
        print(f"{'='*60}")
        
        # Prepare prediction data
        prediction_data = {
            "artist": str(row.get('ARTIST', 'Unknown Artist')),
            "object_type": str(row.get('OBJECT', 'Print')),
            "technique": str(row.get('TECHNIQUE', 'Unknown')),
            "signature": str(row.get('SIGNATURE', 'Unknown')),
            "condition": str(row.get('CONDITION', 'Unknown')),
            "expert": str(row.get('EXPERT', 'Unknown')),
            "year": int(row.get('YEAR', 2000)) if pd.notna(row.get('YEAR')) else 2000,
            "width": 50.0,  # Default values since dimensions are N/A
            "height": 50.0,
            "image_url": None
        }
        
        # Calculate actual log values
        actual_price = float(row.get('PRICE', 0))
        actual_log10 = np.log10(actual_price)
        actual_log1p = np.log1p(actual_price)
        
        print(f"Actual Price: ${actual_price}")
        print(f"Actual Log10: {actual_log10:.4f}")
        print(f"Actual Log1p: {actual_log1p:.4f}")
        
        # Make prediction request
        try:
            response = requests.post(
                "http://localhost:8000/predict",
                json=prediction_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                predicted_price = result.get('predicted_price', 0)
                predicted_log = result.get('log_price', 0)
                confidence = result.get('confidence', 0)
                popularity = result.get('artist_popularity', 'Unknown')
                
                print(f"Predicted Price: ${predicted_price:.2f}")
                print(f"Predicted Log: {predicted_log:.4f}")
                print(f"Confidence: {confidence}")
                print(f"Popularity: {popularity}")
                
                # Calculate errors
                price_error = abs(predicted_price - actual_price) / actual_price * 100
                log_error = abs(predicted_log - actual_log1p) / actual_log1p * 100 if actual_log1p > 0 else 0
                
                print(f"Price Error: {price_error:.1f}%")
                print(f"Log Error: {log_error:.1f}%")
                
                # Determine accuracy
                if price_error <= 20:
                    accuracy = "EXCELLENT"
                elif price_error <= 50:
                    accuracy = "GOOD"
                elif price_error <= 80:
                    accuracy = "FAIR"
                else:
                    accuracy = "POOR"
                
                print(f"Accuracy: {accuracy}")
                
                results.append({
                    "price": actual_price,
                    "artist": row.get('ARTIST', 'Unknown'),
                    "actual_log": actual_log1p,
                    "predicted_log": predicted_log,
                    "predicted_price": predicted_price,
                    "price_error": price_error,
                    "log_error": log_error,
                    "accuracy": accuracy
                })
                
            else:
                print(f"Prediction failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error making prediction: {e}")
    
    # Summary statistics
    if results:
        print("\n" + "=" * 80)
        print("SUMMARY STATISTICS")
        print("=" * 80)
        
        avg_price_error = np.mean([r['price_error'] for r in results])
        avg_log_error = np.mean([r['log_error'] for r in results])
        
        print(f"Average Price Error: {avg_price_error:.1f}%")
        print(f"Average Log Error: {avg_log_error:.1f}%")
        
        # Count accuracy levels
        accuracy_counts = {}
        for result in results:
            acc = result['accuracy']
            accuracy_counts[acc] = accuracy_counts.get(acc, 0) + 1
        
        print("\nAccuracy Distribution:")
        for acc, count in accuracy_counts.items():
            print(f"  {acc}: {count}/{len(results)} ({count/len(results)*100:.0f}%)")
        
        # Show all results in a table format
        print("\n" + "=" * 80)
        print("DETAILED RESULTS TABLE")
        print("=" * 80)
        print(f"{'Artist':<25} {'Actual':<8} {'Predicted':<10} {'Error%':<8} {'Accuracy':<10}")
        print("-" * 80)
        
        for result in results:
            artist_name = result['artist'][:24] if len(result['artist']) > 24 else result['artist']
            print(f"{artist_name:<25} ${result['price']:<7} ${result['predicted_price']:<9.0f} {result['price_error']:<7.1f}% {result['accuracy']:<10}")
        
        # Show best and worst predictions
        print("\nBEST PREDICTIONS (Lowest Error):")
        print("-" * 40)
        best_predictions = sorted(results, key=lambda x: x['price_error'])[:3]
        for result in best_predictions:
            print(f"  ${result['price']} - {result['artist']}: {result['price_error']:.1f}% error")
        
        print("\nWORST PREDICTIONS (Highest Error):")
        print("-" * 40)
        worst_predictions = sorted(results, key=lambda x: x['price_error'], reverse=True)[:3]
        for result in worst_predictions:
            print(f"  ${result['price']} - {result['artist']}: {result['price_error']:.1f}% error")
        
        print(f"\nOverall Assessment:")
        if avg_price_error < 50:
            print("EXCELLENT: Model performs very well on real data!")
        elif avg_price_error < 80:
            print("GOOD: Model performs reasonably well on real data!")
        else:
            print("NEEDS IMPROVEMENT: Model needs better scaling for real data!")
    
    return results

if __name__ == "__main__":
    test_10_artists_predictions()
