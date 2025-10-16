import boto3
import psycopg2
from io import BytesIO
import pandas as pd
from typing import Dict, Any
from sqlalchemy import create_engine

def load_to_s3(df: pd.DataFrame, bucket: str, key: str, aws_access_key: str, aws_secret_key: str):
    """Load data to S3 as Parquet."""
    try:
        s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
        print(f"Loaded to S3: {bucket}/{key}")
    except Exception as e:
        print(f"Error loading to S3: {e}")
        raise

def load_to_postgres(df: pd.DataFrame, conn_params: Dict[str, Any]):
    """Load data to PostgreSQL."""
    try:
        # Create SQLAlchemy engine from connection parameters
        connection_string = f"postgresql://{conn_params['user']}:{conn_params['password']}@{conn_params['host']}:{conn_params['port']}/{conn_params['dbname']}"
        engine = create_engine(connection_string)
        
        # Load data using to_sql with SQLAlchemy engine
        df.to_sql('autonomous_telemetry', engine, if_exists='append', index=False)
        engine.dispose()
        print(f"Loaded {len(df)} rows to PostgreSQL table 'autonomous_telemetry'")
    except Exception as e:
        print(f"Error loading to PostgreSQL: {e}")
        raise