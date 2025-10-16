import pandas as pd
import numpy as np
from typing import Dict, Any

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in km."""
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform: Clean, enrich, and aggregate autonomous driving data."""
    # Clean: Remove invalid speeds or steering angles
    df = df[(df['speed_kmh'] >= 0) & (df['speed_kmh'] <= 200) & (df['steering_angle'].abs() <= 45)]
    
    # Sort by vehicle and timestamp for proper sequential calculations
    df = df.sort_values(['vehicle_id', 'timestamp']).reset_index(drop=True)
    
    # Enrich: Calculate distance traveled between consecutive points per vehicle
    df['lat_prev'] = df.groupby('vehicle_id')['latitude'].shift()
    df['lon_prev'] = df.groupby('vehicle_id')['longitude'].shift()
    df['distance_km'] = haversine_distance(
        df['lat_prev'], df['lon_prev'], 
        df['latitude'], df['longitude']
    )
    df['distance_km'] = df['distance_km'].fillna(0)
    df.drop(['lat_prev', 'lon_prev'], axis=1, inplace=True)
    
    # Detect lane changes (steering angle change > 10 degrees in 1s)
    df['steering_diff'] = df.groupby('vehicle_id')['steering_angle'].diff().abs()
    df['lane_change'] = (df['steering_diff'] > 10) & (df['speed_kmh'] > 20)
    
    # Aggregate: Hourly stats per vehicle
    df['hour'] = df['timestamp'].dt.floor('H')
    transformed = df.groupby(['vehicle_id', 'hour']).agg({
        'speed_kmh': 'mean',
        'distance_km': 'sum',
        'steering_angle': 'mean',
        'autopilot_mode': 'mean',  # % time in autonomous mode
        'lane_change': 'sum',      # Count of lane changes
        'camera_detections': 'count',
        'radar_distance': 'mean'
    }).reset_index()
    transformed.columns = [
        'vehicle_id', 'hour', 'avg_speed_kmh', 'total_distance_km',
        'avg_steering_angle', 'autopilot_usage', 'lane_changes', 'camera_events', 'avg_radar_distance'
    ]
    
    print(f"Transformed to {len(transformed)} aggregated rows")
    return transformed