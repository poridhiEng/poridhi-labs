# Airflow for ETL and Data Lake Management

This guide explores using Apache Airflow to orchestrate ETL pipelines for data lake management, leveraging Docker for seamless deployment and scalability.

## What is ETL?

ETL (Extract, Transform, Load) is a crucial process in data engineering, enabling data extraction from various sources, transformation into usable formats, and loading into data warehouses or lakes for analysis and application. Managing ETL workflows with Apache Airflow provides powerful automation, scheduling, and monitoring capabilities, particularly useful in modern data lakes.

![alt text](./images/ETL.svg)

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


## Overview of ETL

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


## Implementation of Apache Airflow in ETL and Data Lake Management

### Open VS Code and Create Necessary Files

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
CONSTRAINT_URL="[https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt](https://raw.githubusercontent.com/apache/airflow/constraints-$%7BAIRFLOW_VERSION%7D/constraints-$%7BPYTHON_VERSION%7D.txt)"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

### Initialise the Docker Compose YAML File

##### Automatically Generate Docker Compose File

```bash
curl -LfO '[https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml](https://airflow.apache.org/docs/apache-airflow/2.10.3/docker-compose.yaml)'
```

This will create a `docker-compose.yaml` file in the current directory.

![alt text](./images/image.png)

##### Alternative Docker Compose File Example

```yaml
# docker-compose.yml
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
from airflow.decorators import task
from airflow.utils.dates import days_ago
import requests
import json

#Latitude and longitude for the desired location (London in this case)
LATITUDE= '51.5074'
LONGITUDE= '-0.1278'
POSTGRES_CONN_ID= 'postgres_default'
API_CONN_ID= 'open_meteo_api'

default_args= {
    'owner': 'airflow',
    'start_date': days_ago(1)
}

def extract_weatherdata():
        """Extract weather data from Open meteo api using airflow connection"""

        #Use http hook to get connection details from airflow connection
        http_hook= HttpHook(http_conn_id=API_CONN_ID, method='GET')

        ##Build api endpoint
        ## https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true
        endpoint= f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=true'

        #Make the request via httphook
        response= http_hook.run(endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code}")
        

    
def transform_weatherdata(weather_data):
        """Transform the extracted weather data"""
        current_weather= weather_data['current_weather']
        transformed_data={
            'latitude' : float(LATITUDE),
            'longitude': float(LONGITUDE),
            "temperature": current_weather['temperature'],
            'windspeed': current_weather['windspeed'],
            'winddirection': current_weather['winddirection'],
            'weathercode': current_weather['weathercode'],

        }
        return transformed_data
    
    
def load_weatherdata(transformed_data):
        """Load transformed data to postgres"""
        pg_hook= PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn= pg_hook.get_conn()
        cursor= conn.cursor()

        #create table if it doesn't exist
        cursor.execute(
            """create table if not exist weather_data(
            latitude FLOAT
            longitude FLOAT
            temperature INT
            windspeed INT
            winddirection INT
            weathercode INT
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );"""
        )

        #Insert transformed data into the table
        cursor.execute(
            """INSERT INTO weather_data (latitude, longitude, temperature, windspeed, winddirection, weathercode)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (
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

with DAG(dag_id='etl_weather_pipeline',
         default_args=default_args,
         schedule_interval='@daily',
         catchup=False
         ) as dag:
        
        extract_task= PythonOperator(
               task_id='extract_weather',
               python_callable=extract_weatherdata
        )

        transform_task= PythonOperator(
               task_id='transform_weatherdata',
               python_callable=transform_weatherdata,
               op_args=[extract_task.output]
        )

        load_task= PythonOperator(
               task_id='load_weatherdata',
               python_callable=load_weatherdata,
               op_args=[transform_task.output]
        )
        
        #DAG workflow
        
        extract_task >> transform_task >> load_task
```

Here we have used the weather data information for data extracting as real time data and used it for transformation and loaded it in postgres database.

**Key Points**:

- **Extract**: Fetches weather data from the OpenMeteo API.
- **Transform**: Cleans and normalises the data.
- **Load**: Stores the transformed data in a PostgreSQL database.

The output for the data that we used:

![alt text](./images/image-1.png)

## Launching the Project Using Load Balancer

### Initialising Docker

```bash
docker-compose up airflow-init
```
In the above command, the `airflow-init` service initialises the Airflow database.

![alt text](./images/image-2.png)

Here you can see we have created a default Airflow user with the role Admin.

### Running Docker Containers

```bash
docker-compose up -d
```

![alt text](./images/image-3.png)

Here, we have started the containers.

### Checking Active Containers

```bash
docker ps
```

This will show you the active containers.

![alt text](./images/image-4.png)

### Stopping Docker Containers

```bash
docker-compose down
```

![alt text](./images/image-5.png)

Successfully stopped the containers.

### Expose Airflow UI

- Find the local IP using:

  ```bash
  ip addr show eth0
  ```

  ![alt text](./images/image-6.png)

- Go to the load balancer icon in the `Poridhi Lab`.

  ![alt text](./images/image-7.png)

- Create a load balancer using the IP and port.

  ![alt text](./images/image-8.png)

### Login to Apache Airflow

- Navigate to the Airflow dashboard.
- Default credentials:
  - **Username**: admin
  - **Password**: admin

  ![alt text](./images/image-9.png)

### Finalising the Creation of DAG

![alt text](./images/image-10.png)

Here we have created a DAG and scheduled it to run daily.

#### Triggering and Monitoring DAGs

- Use the Airflow UI to monitor pipeline execution.

![alt text](./images/image-11.png)

Here we can see the DAG has been triggered and the data has been loaded in the database.

## Conclusion

This document demonstrates setting up an ETL pipeline using Apache Airflow, showcasing its integration with Docker and real-time weather data extraction. The guide highlights the workflow from setup to deployment and monitoring using Airflow’s powerful orchestration features.

