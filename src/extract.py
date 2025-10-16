import pandas as pd
from typing import Dict, Any

def extract_data(source_path: str) -> pd.DataFrame:
    """Extract autonomous driving data from CSV."""
    try:
        df = pd.read_csv(source_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        print(f"Extracted {len(df)} rows from {source_path}")
        return df
    except Exception as e:
        print(f"Error extracting data: {e}")
        raise