from pyspark.sql import SparkSession
import psycopg2
from typing import Dict, Any

def load_to_s3(input_path: str, bucket: str, key: str, aws_access_key: str, aws_secret_key: str):
    """Load Parquet to S3 using PySpark."""
    spark = SparkSession.builder.appName("AutonomousETL").getOrCreate()
    try:
        sdf = spark.read.parquet(input_path)
        sdf.write.parquet(f"s3a://{bucket}/{key}", 
                         mode="overwrite",
                         sparkConf={"spark.hadoop.fs.s3a.access.key": aws_access_key,
                                    "spark.hadoop.fs.s3a.secret.key": aws_secret_key})
        print(f"Loaded to S3: {bucket}/{key}")
    except Exception as e:
        print(f"Error loading to S3: {e}")
        raise
    spark.stop()

def load_to_postgres(input_path: str, conn_params: Dict[str, Any]):
    """Load Parquet to PostgreSQL using PySpark."""
    spark = SparkSession.builder.appName("AutonomousETL").getOrCreate()
    try:
        sdf = spark.read.parquet(input_path)
        sdf.write.jdbc(
            url=f"jdbc:postgresql://{conn_params['host']}:{conn_params['port']}/{conn_params['dbname']}",
            table="autonomous_telemetry",
            mode="append",
            properties={"user": conn_params['user'], "password": conn_params['password'], "driver": "org.postgresql.Driver"}
        )
        print("Loaded to PostgreSQL")
    except Exception as e:
        print(f"Error loading to PostgreSQL: {e}")
        raise
    spark.stop()