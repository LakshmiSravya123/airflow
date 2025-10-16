# ETLcaspian - Autonomous Driving Data Pipeline

An Apache Airflow-based ETL pipeline for processing autonomous vehicle telemetry data.

## 🚀 Features

- **Extract**: Load autonomous driving data from CSV files
- **Transform**: Clean, enrich, and aggregate telemetry data
  - Remove invalid data points
  - Calculate distance traveled using Haversine formula
  - Detect lane changes based on steering angle changes
  - Aggregate hourly statistics per vehicle
- **Load**: Store processed data in PostgreSQL and optionally S3
- **Orchestration**: Automated scheduling with Apache Airflow

## 📋 Prerequisites

- Docker & Docker Compose
- Python 3.8+ (for local testing)

## 🏗️ Architecture

```
ETLcaspian/
├── dags/
│   └── autonomous_etl_dag.py    # Airflow DAG definition
├── src/
│   ├── extract.py               # Data extraction logic
│   ├── transform.py             # Data transformation logic
│   └── load.py                  # Data loading logic
├── data/
│   └── autonomous_data.csv      # Sample input data
├── logs/                        # Airflow logs
├── docker-compose.yml           # Docker services configuration
├── requirements.txt             # Python dependencies
└── generate_data.py             # Sample data generator
```

## 🚀 Quick Start

### 1. Generate Sample Data

```bash
python3 generate_data.py
```

This creates `data/autonomous_data.csv` with 10,000 rows of sample autonomous vehicle telemetry.

### 2. Start the Pipeline

```bash
docker-compose up -d
```

This will:
- Start PostgreSQL database
- Initialize Airflow database
- Create admin user (username: `admin`, password: `admin`)
- Start Airflow webserver and scheduler

### 3. Access Airflow UI

Open your browser and navigate to:
```
http://localhost:8080
```

Login credentials:
- **Username**: `admin`
- **Password**: `admin`

### 4. Enable the DAG

1. In the Airflow UI, find the `autonomous_etl_pipeline` DAG
2. Toggle it to "On" to enable automatic scheduling
3. Click "Trigger DAG" to run it manually

## 📊 Data Flow

1. **Extract**: Reads CSV data from `/opt/airflow/data/autonomous_data.csv`
2. **Transform**: 
   - Filters invalid speed/steering data
   - Calculates distance between GPS points
   - Detects lane changes
   - Aggregates to hourly statistics per vehicle
3. **Load**: 
   - Saves to PostgreSQL table `autonomous_telemetry`
   - Optionally saves to S3 (requires AWS credentials)

## 🔧 Configuration

### Database Connection

The pipeline connects to PostgreSQL with these settings (defined in `docker-compose.yml`):
- **Host**: `postgres`
- **Database**: `autonomous_db`
- **User**: `user`
- **Password**: `pass`
- **Port**: `5432`

### S3 Configuration (Optional)

To enable S3 loading, update `dags/autonomous_etl_dag.py`:

```python
s3_bucket = 'your-bucket-name'
aws_access_key = 'YOUR_AWS_ACCESS_KEY'
aws_secret_key = 'YOUR_AWS_SECRET_KEY'
```

## 🐛 Fixes Applied

### 1. **load.py** - Fixed PostgreSQL Loading
- **Issue**: Used `psycopg2` connection with `pandas.to_sql()` (incompatible)
- **Fix**: Created SQLAlchemy engine for proper database connection

### 2. **transform.py** - Fixed Distance Calculation
- **Issue**: Incorrect `groupby().apply()` usage causing errors
- **Fix**: Used vectorized operations with `shift()` for better performance

### 3. **docker-compose.yml** - Added Airflow Initialization
- **Issue**: Airflow database not initialized before starting services
- **Fix**: Added `airflow-init` service with proper dependency management

### 4. **Data Directory**
- **Issue**: Missing `data/` and `logs/` directories
- **Fix**: Created directories and generated sample data

## 📈 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
```

### Check Database

```bash
docker exec -it etlcaspian-postgres-1 psql -U user -d autonomous_db

# Inside psql:
\dt                                    # List tables
SELECT * FROM autonomous_telemetry LIMIT 10;  # View data
```

## 🛑 Stop the Pipeline

```bash
docker-compose down
```

To remove all data (including database):
```bash
docker-compose down -v
```

## 🧪 Testing Locally

Test individual components without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Test extraction
python3 -c "from src.extract import extract_data; df = extract_data('data/autonomous_data.csv'); print(df.head())"

# Test transformation
python3 -c "from src.extract import extract_data; from src.transform import transform_data; df = extract_data('data/autonomous_data.csv'); transformed = transform_data(df); print(transformed.head())"
```

## 📝 Sample Data Schema

### Input Data (autonomous_data.csv)
- `timestamp`: Event timestamp
- `vehicle_id`: Vehicle identifier
- `latitude`: GPS latitude
- `longitude`: GPS longitude
- `speed_kmh`: Speed in km/h
- `steering_angle`: Steering angle in degrees
- `camera_detections`: Number of objects detected
- `radar_distance`: Distance to nearest object (m)
- `autopilot_mode`: 1 if autopilot active, 0 otherwise

### Output Data (autonomous_telemetry table)
- `vehicle_id`: Vehicle identifier
- `hour`: Aggregation hour
- `avg_speed_kmh`: Average speed
- `total_distance_km`: Total distance traveled
- `avg_steering_angle`: Average steering angle
- `autopilot_usage`: Percentage of time in autopilot
- `lane_changes`: Number of lane changes detected
- `camera_events`: Number of camera detection events
- `avg_radar_distance`: Average radar distance

## 🤝 Contributing

Feel free to submit issues or pull requests for improvements!

## 📧 Support

For issues, check:
1. Docker logs: `docker-compose logs`
2. Airflow UI task logs
3. Ensure all containers are running: `docker-compose ps`

---

**Happy Data Processing! 🚗💨**
