from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/src')  # Adjust to your src path
from extract import extract_data
from transform import transform_data
from load import load_to_s3, load_to_postgres

# Default Airflow args
default_args = {
    'owner': 'autonomous_etl',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 10, 16),
}

# Define DAG
dag = DAG(
    'autonomous_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline for autonomous driving data',
    schedule='@daily',
    catchup=False,
)

# ETL task
def run_etl(**context):
    # Extract
    source_path = '/opt/airflow/data/autonomous_data.csv'
    df_raw = extract_data(source_path)
    
    # Transform
    df_transformed = transform_data(df_raw)
    
    # Load to S3 (optional - comment out if not using AWS)
    # s3_bucket = 'your-autonomous-bucket'  # Replace with your S3 bucket
    # s3_key = f'telemetry/{context["ds"]}/processed.parquet'
    # load_to_s3(df_transformed, s3_bucket, s3_key, 'YOUR_AWS_ACCESS_KEY', 'YOUR_AWS_SECRET_KEY')
    
    # Load to PostgreSQL
    postgres_conn = {
        'host': 'postgres',
        'dbname': 'autonomous_db',
        'user': 'user',
        'password': 'pass',
        'port': '5432'
    }
    load_to_postgres(df_transformed, postgres_conn)

# Define task
etl_task = PythonOperator(
    task_id='run_etl',
    python_callable=run_etl,
    dag=dag,
)

etl_task