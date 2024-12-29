# Airflow for ETL and Data Lake Management

## Introduction

ETL (Extract, Transform, Load) is a crucial process in data engineering, enabling data extraction from various sources, transformation into usable formats, and loading into data warehouses or lakes for analysis and application. Managing ETL workflows with Apache Airflow provides powerful automation, scheduling, and monitoring capabilities, particularly useful in modern data lakes.

This guide explores using Apache Airflow to orchestrate ETL pipelines for data lake management, leveraging Docker for seamless deployment and scalability.


## Objectives

- Understand the ETL process and its role in data engineering.
- Set up Apache Airflow for ETL pipeline management.
- Use Docker to deploy and manage Airflow environments.
- Implement a weather data ETL pipeline.
- Monitor and visualise ETL pipelines via the Airflow web interface.

## Table of Contents

1. Overview of ETL  
2. Implementations of Apache Airflow on ETL project scheduling
3. Launching the project using Load Balancer


### 1. Overview of ETL

ETL stands for Extract, Transform, Load, a process foundational in data warehousing, analysis, and MLOps.

#### **Extract**

- Gather data from diverse sources such as databases, APIs, or real-time streams.

#### **Transform**

- Clean, normalise, and enrich data to ensure consistency and usability. Common tasks include handling missing values, converting data types, and feature engineering.

#### **Load**

- Store transformed data in target systems like data warehouses, databases, or data lakes.

**ETL in MLOps**:

- Ensures data consistency.
- Facilitates feature engineering.
- Enables model retraining.
- Supports automation and scalability.


### 2. Implementation of Apache Airflow in ETL and Data Lake Management

#### Open VS Code and Create Necessary Files

##### Update and Upgrade System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

##### Install Python Virtual Environment

```bash
sudo apt install python3-venv
```

##### Create and Activate Virtual Environment

```bash
python3 -m venv etl
source etl/bin/activate
```

##### Install Apache Airflow

```bash
AIRFLOW_VERSION=2.7.3
PYTHON_VERSION="$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

#### Step 2.2: Initialise the Docker Compose YAML File

##### Automatically Generate Docker Compose File

```bash
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml'
```

##### Alternative Docker Compose File Example

```yaml
version: '3'
services:
  airflow:
    build: .
    restart: always
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
      - AIRFLOW__CORE__LOAD_EXAMPLES=False
    user: "${AIRFLOW_UID:-50000}:0"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs:rw
    ports:
      - "8081:8080"
    depends_on:
      - postgres
    command: bash -c "airflow db init && airflow users create --username admin --password admin --firstname Anonymous --lastname Admin --role Admin --email admin@example.com && airflow webserver & airflow scheduler"

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

##### Create Necessary Directories

```bash
mkdir -p ./dags ./logs ./plugins ./config
```

### Write the Code

#### ETL Pipeline Code

```python
from airflow import DAG
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

LATITUDE = '51.5074'
LONGITUDE = '-0.1278'
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

def extract_weatherdata():
    http_hook = HttpHook(http_conn_id=API_CONN_ID, method='GET')
    endpoint = f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'
    response = http_hook.run(endpoint)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def transform_weatherdata(weather_data):
    current_weather = weather_data['current_weather']
    return {
        'latitude': float(LATITUDE),
        'longitude': float(LONGITUDE),
        'temperature': current_weather['temperature'],
        'windspeed': current_weather['windspeed'],
        'winddirection': current_weather['winddirection'],
        'weathercode': current_weather['weathercode'],
    }

def load_weatherdata(transformed_data):
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS weather_data (
        latitude FLOAT,
        longitude FLOAT,
        temperature INT,
        windspeed INT,
        winddirection INT,
        weathercode INT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
    )
    cursor.execute(
        """INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode'],
        )
    )
    conn.commit()
    cursor.close()
    conn.close()

with DAG(
    dag_id='etl_weather_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
) as dag:
    extract_task = PythonOperator(
        task_id='extract_weather',
        python_callable=extract_weatherdata
    )
    transform_task = PythonOperator(
        task_id='transform_weatherdata',
        python_callable=transform_weatherdata,
        op_args=[extract_task.output]
    )
    load_task = PythonOperator(
        task_id='load_weatherdata',
        python_callable=load_weatherdata,
        op_args=[transform_task.output]
    )
    extract_task >> transform_task >> load_task
```

**Key Points**:

- **Extract**: Fetches weather data from the OpenMeteo API.
- **Transform**: Cleans and normalises the data.
- **Load**: Stores the transformed data in a PostgreSQL database.

### 3. Launching the Project Using Load Balancer

#### Initialising Docker

```bash
docker-compose up airflow-init
```
In the above command, the `airflow-init` service initialises the Airflow database.


#### Running Docker Containers

```bash
docker-compose up -d
```

#### Checking Active Containers

```bash
docker ps
```

#### Stopping Docker Containers

```bash
docker-compose down
```

#### Expose Airflow UI

- Find the local IP using:

```bash
ip addr show eth0
```

- Create a load balancer using the IP and port.

#### Login to Apache Airflow

- Navigate to the Airflow dashboard.
- Default credentials:
  - **Username**: admin
  - **Password**: admin

#### Triggering and Monitoring DAGs

- Use the Airflow UI to monitor pipeline execution.


## Conclusion

This document demonstrates setting up an ETL pipeline using Apache Airflow, showcasing its integration with Docker and real-time weather data extraction. The guide highlights the workflow from setup to deployment and monitoring using Airflow’s powerful orchestration features.

