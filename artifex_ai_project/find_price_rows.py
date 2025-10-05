"""
Find random rows from Excel file with specific actual prices
"""

import pandas as pd
import numpy as np
import random

def find_price_rows():
    """Find random rows with specific actual prices"""
    print("FINDING RANDOM ROWS WITH SPECIFIC ACTUAL PRICES")
    print("=" * 70)
    
    # Read the Excel file
    try:
        df = pd.read_excel('C:/Users/angel/OneDrive - Sri Lanka Institute of Information Technology/Desktop/ArtifexAI/art_auction_project/auction/auction/results_2024_05_11.xlsx')
        print(f"Successfully loaded Excel file with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return
    
    # Target prices
    target_prices = [8000, 5000, 2000, 1000, 500, 250, 100, 75, 50, 25]
    
    # Find rows with these exact prices
    found_rows = {}
    
    for price in target_prices:
        # Find rows with this exact price
        price_rows = df[df['PRICE'] == price]
        if len(price_rows) > 0:
            # Get a random row
            random_row = price_rows.sample(n=1).iloc[0]
            found_rows[price] = random_row
            print(f"Found {len(price_rows)} rows with price ${price}")
        else:
            print(f"No rows found with exact price ${price}")
    
    print(f"\nFound {len(found_rows)} rows with target prices")
    
    # Display the found rows
    print("\n" + "=" * 70)
    print("RANDOM ROWS WITH TARGET PRICES")
    print("=" * 70)
    
    for price, row in found_rows.items():
        print(f"\nPRICE: ${price}")
        print("-" * 30)
        print(f"Artist: {row.get('ARTIST', 'N/A')}")
        print(f"Title: {row.get('TITLE', 'N/A')}")
        print(f"Technique: {row.get('TECHNIQUE', 'N/A')}")
        print(f"Signature: {row.get('SIGNATURE', 'N/A')}")
        print(f"Condition: {row.get('CONDITION', 'N/A')}")
        print(f"Dimensions: {row.get('DIMENSIONS', 'N/A')}")
        print(f"Year: {row.get('YEAR', 'N/A')}")
        print(f"Expert: {row.get('EXPERT', 'N/A')}")
        print(f"Object: {row.get('OBJECT', 'N/A')}")
        print(f"Actual Price: ${row.get('PRICE', 'N/A')}")
        
        # Calculate log values
        actual_price = row.get('PRICE', 0)
        if actual_price > 0:
            log_price = np.log10(actual_price)
            log1p_price = np.log1p(actual_price)
            print(f"Log10 Price: {log_price:.4f}")
            print(f"Log1p Price: {log1p_price:.4f}")
    
    return found_rows

if __name__ == "__main__":
    found_rows = find_price_rows()
