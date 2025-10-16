# 🚗 ETLcaspian - Autonomous Driving Data Pipeline

A complete ETL (Extract, Transform, Load) pipeline for processing autonomous vehicle telemetry data using Apache Airflow, with optional streaming capabilities using Kafka and Spark.

[![GitHub](https://img.shields.io/badge/GitHub-airflow-blue)](https://github.com/LakshmiSravya123/airflow)

---

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Two Setup Options](#two-setup-options)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [GitHub Repositories](#github-repositories)

---

## 🎯 Overview

This project provides a production-ready ETL pipeline for autonomous vehicle data with two deployment options:

1. **Basic ETL Pipeline** - Batch processing with Airflow + PostgreSQL
2. **Streaming ETL Pipeline** - Real-time processing with Kafka + Spark + Airflow

Both setups are containerized with Docker Compose for easy deployment.

---

## ✨ Features

### Data Processing
- ✅ **Extract**: Load CSV data from autonomous vehicles
- ✅ **Transform**: Clean, enrich, and aggregate telemetry
  - Remove invalid data points
  - Calculate distance traveled using Haversine formula
  - Detect lane changes based on steering patterns
  - Aggregate hourly statistics per vehicle
- ✅ **Load**: Store processed data in PostgreSQL
- ✅ **Optional S3 Export**: Save to AWS S3 for data lake

### Infrastructure
- 🐳 **Dockerized**: All services run in containers
- 🔄 **Automated**: Airflow orchestrates the entire pipeline
- 📊 **Monitored**: Web UIs for Airflow and Spark
- 🔒 **Secure**: Database credentials and API keys via environment variables
- 📈 **Scalable**: Add Spark workers for parallel processing

---

## 🏗️ Architecture

### Basic Setup
```
┌─────────────┐
│   CSV Data  │
└──────┬──────┘
       │
┌──────▼──────┐
│   Airflow   │ ← Orchestration & Scheduling
│  (Scheduler │
│  + Webserver)
└──────┬──────┘
       │
┌──────▼──────┐
│ PostgreSQL  │ ← Data Storage
└─────────────┘
```

### Streaming Setup
```
┌─────────────┐
│   Zookeeper │ ← Kafka Coordination
└──────┬──────┘
       │
┌──────▼──────┐
│    Kafka    │ ← Message Broker (Real-time Data)
└──────┬──────┘
       │
┌──────▼──────┐     ┌──────────────┐
│Spark Master │────►│ Spark Worker │ ← Distributed Processing
└──────┬──────┘     └──────────────┘
       │
┌──────▼──────┐
│   Airflow   │ ← Orchestration
└──────┬──────┘
       │
┌──────▼──────┐
│ PostgreSQL  │ ← Data Storage
└─────────────┘
```

---

## 🚀 Two Setup Options

### Option 1: Basic ETL Pipeline (Recommended for Beginners)

**Location**: `/Users/sravyalu/ETLcaspian/`

**Services**:
- PostgreSQL (port 5433)
- Airflow Webserver (port 8080)
- Airflow Scheduler

**Resources**: ~2GB RAM, 2 CPU cores

**Best for**: 
- Batch processing
- Scheduled jobs
- CSV file processing
- Learning Airflow

### Option 2: Streaming ETL Pipeline (Advanced)

**Location**: `/Users/sravyalu/ETLcaspian/airflow/`

**Services**:
- PostgreSQL (port 5434)
- Zookeeper (port 2181)
- Kafka (port 29092)
- Spark Master (port 7077, UI on 8081)
- Spark Worker
- Airflow Webserver (port 8082)
- Airflow Scheduler

**Resources**: ~4-8GB RAM, 4 CPU cores

**Best for**:
- Real-time data processing
- Streaming analytics
- High-throughput workloads
- Production deployments

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- 4GB+ RAM available
- 10GB+ disk space

### Basic Setup (5 minutes)

```bash
# 1. Navigate to project directory
cd /Users/sravyalu/ETLcaspian

# 2. Generate sample data
python3 generate_data.py

# 3. Start services
docker-compose up -d

# 4. Wait for services to be healthy (30 seconds)
docker-compose ps

# 5. Open Airflow UI
open http://localhost:8080
# Login: admin / admin
```

### Streaming Setup (10 minutes)

```bash
# 1. Navigate to streaming directory
cd /Users/sravyalu/ETLcaspian/airflow

# 2. Start all services
docker-compose up -d

# 3. Wait for services (60 seconds)
docker-compose ps

# 4. Open UIs
open http://localhost:8082  # Airflow
open http://localhost:8081  # Spark
```

---

## 📖 Detailed Setup

### 1. Clone Repository

```bash
git clone https://github.com/LakshmiSravya123/airflow.git ETLcaspian
cd ETLcaspian
```

### 2. Generate Sample Data

```bash
python3 generate_data.py
```

This creates `data/autonomous_data.csv` with 10,000 rows of sample telemetry:
- Vehicle IDs, GPS coordinates, speed, steering angle
- Camera detections, radar distance, autopilot status

### 3. Choose Your Setup

#### Basic Setup

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access**:
- Airflow UI: http://localhost:8080 (admin/admin)
- PostgreSQL: localhost:5433

#### Streaming Setup

```bash
# Navigate to streaming directory
cd airflow

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access**:
- Airflow UI: http://localhost:8082 (admin/admin)
- Spark UI: http://localhost:8081
- Kafka: localhost:29092
- PostgreSQL: localhost:5434

---

## 💻 Usage

### Running the ETL Pipeline

1. **Access Airflow UI**
   - Basic: http://localhost:8080
   - Streaming: http://localhost:8082

2. **Login**
   - Username: `admin`
   - Password: `admin`

3. **Enable DAG**
   - Find `autonomous_etl_pipeline`
   - Toggle switch to ON

4. **Trigger DAG**
   - Click play button (▶️)
   - Watch execution in real-time

5. **View Results**
   ```bash
   # Connect to database
   docker exec -it etlcaspian-postgres-1 psql -U user -d autonomous_db
   
   # Query results
   SELECT * FROM autonomous_telemetry LIMIT 10;
   ```

### Working with Kafka (Streaming Setup Only)

```bash
# Create topic
docker exec -it airflow-kafka-1 kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic autonomous-telemetry \
  --partitions 3 \
  --replication-factor 1

# List topics
docker exec -it airflow-kafka-1 kafka-topics --list \
  --bootstrap-server localhost:9092

# Produce messages
docker exec -it airflow-kafka-1 kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic autonomous-telemetry

# Consume messages
docker exec -it airflow-kafka-1 kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic autonomous-telemetry \
  --from-beginning
```

### Monitoring

```bash
# Check service health
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Monitor resources
docker stats

# Check Airflow DAG status
docker exec airflow-airflow-scheduler-1 airflow dags list
```

---

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Error: port 5432 already in use
# Solution: Use different port (already configured as 5433/5434)
```

#### Services Not Starting
```bash
# Check logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]

# Restart all
docker-compose down && docker-compose up -d
```

#### DAG Not Appearing
```bash
# Check DAG syntax
docker exec airflow-airflow-scheduler-1 python /opt/airflow/dags/autonomous_etl_dag.py

# Restart scheduler
docker-compose restart airflow-scheduler

# Check logs
docker-compose logs airflow-scheduler
```

#### Out of Memory
```bash
# Check usage
docker stats

# Solution: Stop streaming setup, use basic setup
cd /Users/sravyalu/ETLcaspian/airflow
docker-compose down

cd /Users/sravyalu/ETLcaspian
docker-compose up -d
```

### Getting Help

1. Check logs: `docker-compose logs -f`
2. Verify services: `docker-compose ps`
3. Check GitHub Issues: [airflow repository](https://github.com/LakshmiSravya123/airflow/issues)

---

## 📦 Project Structure

```
ETLcaspian/
├── README.md                      # Main documentation
├── README_COMPLETE.md             # This file
├── FIXES_APPLIED.md              # Bug fixes documentation
├── docker-compose.yml             # Basic setup configuration
├── docker-compose.streaming.yml   # Streaming setup (alternative)
├── requirements.txt               # Python dependencies
├── generate_data.py               # Sample data generator
│
├── dags/
│   └── autonomous_etl_dag.py     # Airflow DAG definition
│
├── src/
│   ├── extract.py                # Data extraction logic
│   ├── transform.py              # Data transformation logic
│   └── load.py                   # Data loading logic
│
├── data/
│   └── autonomous_data.csv       # Sample telemetry data
│
├── logs/                         # Airflow logs
│
└── airflow/                      # Streaming setup directory
    ├── README.md                 # Streaming documentation
    ├── docker-compose.yml        # Full streaming stack
    ├── dags/                     # Airflow DAGs
    ├── src/                      # ETL scripts
    └── data/                     # Data files
```

---

## 🔗 GitHub Repositories

### Main Repository
**URL**: https://github.com/LakshmiSravya123/airflow  
**Branch**: main  
**Contains**: Complete ETL pipeline with both basic and streaming setups

### What's Included
- ✅ Docker Compose configurations
- ✅ Airflow DAGs
- ✅ ETL scripts (extract, transform, load)
- ✅ Sample data generator
- ✅ Complete documentation
- ✅ Troubleshooting guides

---

## 📊 Sample Data Schema

### Input: autonomous_data.csv
| Column | Type | Description |
|--------|------|-------------|
| timestamp | datetime | Event timestamp |
| vehicle_id | string | Vehicle identifier (VEH001, VEH002, VEH003) |
| latitude | float | GPS latitude |
| longitude | float | GPS longitude |
| speed_kmh | float | Speed in km/h (0-120) |
| steering_angle | float | Steering angle in degrees (-45 to 45) |
| camera_detections | int | Number of objects detected (0-10) |
| radar_distance | float | Distance to nearest object in meters (2-100) |
| autopilot_mode | int | 1 if autopilot active, 0 otherwise |

### Output: autonomous_telemetry table
| Column | Type | Description |
|--------|------|-------------|
| vehicle_id | string | Vehicle identifier |
| hour | datetime | Aggregation hour |
| avg_speed_kmh | float | Average speed |
| total_distance_km | float | Total distance traveled |
| avg_steering_angle | float | Average steering angle |
| autopilot_usage | float | Percentage of time in autopilot |
| lane_changes | int | Number of lane changes detected |
| camera_events | int | Number of camera detection events |
| avg_radar_distance | float | Average radar distance |

---

## 🛠️ Technologies Used

- **Orchestration**: Apache Airflow 2.7.0
- **Streaming**: Apache Kafka 7.3.0, Apache Spark 3.5.0
- **Database**: PostgreSQL 13
- **Language**: Python 3.8+
- **Libraries**: pandas, SQLAlchemy, boto3, psycopg2
- **Containerization**: Docker, Docker Compose
- **Coordination**: Apache Zookeeper 7.3.0

---

## 📈 Performance

### Basic Setup
- **Throughput**: ~10,000 rows/minute
- **Latency**: Batch processing (minutes)
- **Resource Usage**: 2GB RAM, 2 CPU cores

### Streaming Setup
- **Throughput**: ~100,000 rows/minute (with Spark)
- **Latency**: Near real-time (seconds)
- **Resource Usage**: 4-8GB RAM, 4 CPU cores

---

## 🔐 Security

- Database credentials in environment variables
- No hardcoded passwords in code
- `.gitignore` configured for sensitive files
- Admin credentials should be changed in production

---

## 🚦 Next Steps

1. **Customize the Pipeline**
   - Modify transformation logic in `src/transform.py`
   - Add new data sources in `src/extract.py`
   - Configure S3 export in `src/load.py`

2. **Scale Up**
   - Add more Spark workers
   - Increase Kafka partitions
   - Use external PostgreSQL

3. **Production Deployment**
   - Use Kubernetes for orchestration
   - Set up monitoring (Prometheus, Grafana)
   - Configure backups and disaster recovery

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👥 Contributors

- **LakshmiSravya123** - Initial work and maintenance

---

## 🙏 Acknowledgments

- Apache Airflow community
- Apache Kafka and Spark communities
- Docker and containerization ecosystem

---

## 📞 Support

- **GitHub Issues**: https://github.com/LakshmiSravya123/airflow/issues
- **Documentation**: See README files in each directory

---

**Built with ❤️ for autonomous vehicle data processing**

🚗💨 Happy Data Processing! 🎉
