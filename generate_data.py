import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from kafka import KafkaProducer
import json
import time

def generate_and_send_to_kafka(n_rows=1000, topic='telemetry', bootstrap_servers='localhost:9092'):
    np.random.seed(42)
    start_time = datetime(2025, 10, 16, 13, 0)  # Current time: 01:08 PM PDT, Oct 16, 2025
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                            value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    
    data = {
        'timestamp': [(start_time + timedelta(seconds=i)).isoformat() for i in range(n_rows)],
        'vehicle_id': np.random.choice(['VEH001', 'VEH002', 'VEH003'], n_rows),
        'latitude': 37.7749 + np.random.normal(0, 0.01, n_rows),
        'longitude': -122.4194 + np.random.normal(0, 0.01, n_rows),
        'speed_kmh': np.random.uniform(0, 120, n_rows),
        'steering_angle': np.random.uniform(-45, 45, n_rows),
        'camera_detections': np.random.randint(0, 10, n_rows),
        'radar_distance': np.random.uniform(2, 100, n_rows),
        'autopilot_mode': np.random.choice([1, 0], n_rows, p=[0.8, 0.2])
    }
    
    df = pd.DataFrame(data)
    for _, row in df.iterrows():
        producer.send(topic, row.to_dict())
        time.sleep(0.01)  # Simulate real-time stream
        print(f"Sent record: {row['vehicle_id']}")
    producer.flush()
    print(f"Sent {n_rows} records to Kafka topic {topic}")

if __name__ == "__main__":
    generate_and_send_to_kafka()