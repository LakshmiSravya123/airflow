from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, mean, sum, count, floor_date, abs, when
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import numpy as np

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two lat/lon points in km."""
    R = 6371
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c

def transform_stream(kafka_servers='kafka:9092', topic='telemetry', output_path='data/streamed'):
    spark = SparkSession.builder.appName("AutonomousStreamETL").getOrCreate()
    
    # Schema for Kafka data
    schema = StructType([
        StructField("timestamp", StringType()),
        StructField("vehicle_id", StringType()),
        StructField("latitude", DoubleType()),
        StructField("longitude", DoubleType()),
        StructField("speed_kmh", DoubleType()),
        StructField("steering_angle", DoubleType()),
        StructField("camera_detections", IntegerType()),
        StructField("radar_distance", DoubleType()),
        StructField("autopilot_mode", IntegerType())
    ])
    
    # Read stream from Kafka
    sdf = spark.readStream.format("kafka") \
        .option("kafka.bootstrap.servers", kafka_servers) \
        .option("subscribe", topic) \
        .load()
    
    # Parse JSON data
    sdf = sdf.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
    sdf = sdf.withColumn("timestamp", col("timestamp").cast("timestamp"))
    
    # Clean: Filter invalid data
    sdf = sdf.filter((col("speed_kmh") >= 0) & (col("speed_kmh") <= 200) & (abs(col("steering_angle")) <= 45))
    
    # Enrich: Calculate distance (using window)
    from pyspark.sql.window import Window
    window = Window.partitionBy("vehicle_id").orderBy("timestamp")
    sdf = sdf.withColumn("prev_latitude", col("latitude").lag(1).over(window))
    sdf = sdf.withColumn("prev_longitude", col("longitude").lag(1).over(window))
    
    from pyspark.sql.functions import udf
    haversine_udf = udf(haversine_distance, DoubleType())
    sdf = sdf.withColumn("distance_km", 
        when(col("prev_latitude").isNotNull(), 
             haversine_udf(col("prev_latitude"), col("prev_longitude"), col("latitude"), col("longitude"))
        ).otherwise(0.0))
    
    # Detect lane changes
    sdf = sdf.withColumn("steering_diff", abs(col("steering_angle") - col("steering_angle").lag(1).over(window)))
    sdf = sdf.withColumn("lane_change", when((col("steering_diff") > 10) & (col("speed_kmh") > 20), 1).otherwise(0))
    
    # Aggregate: 1-minute windows per vehicle
    sdf = sdf.withColumn("window", floor_date(col("timestamp"), "1 minute"))
    transformed = sdf.groupBy("vehicle_id", "window").agg(
        mean("speed_kmh").alias("avg_speed_kmh"),
        sum("distance_km").alias("total_distance_km"),
        mean("steering_angle").alias("avg_steering_angle"),
        mean("autopilot_mode").alias("autopilot_usage"),
        sum("lane_change").alias("lane_changes"),
        count("camera_detections").alias("camera_events"),
        mean("radar_distance").alias("avg_radar_distance")
    )
    
    # Write stream to Parquet
    query = transformed.writeStream \
        .format("parquet") \
        .option("path", output_path) \
        .option("checkpointLocation", f"{output_path}/checkpoint") \
        .outputMode("append") \
        .partitionBy("vehicle_id", "window") \
        .start()
    
    query.awaitTermination()
    spark.stop()