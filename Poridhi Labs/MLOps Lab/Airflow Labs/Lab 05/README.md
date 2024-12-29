# ML Pipeline Orchestration with Apache Airflow

## Introduction

Machine Learning (ML) pipelines play a crucial role in automating and streamlining the process of developing, deploying, and monitoring machine learning models. Apache Airflow, a popular workflow orchestration tool, enables the efficient management of these pipelines, offering powerful scheduling, monitoring, and visualisation capabilities.

This guide covers the step-by-step implementation of an ML pipeline using Apache Airflow, incorporating Docker for containerised execution.

## Objectives

- Understand ML pipelines and their role in automating the machine learning workflow.
- Set up Apache Airflow for managing ML pipelines.
- Create Directed Acyclic Graphs (DAGs) to define pipeline workflows.
- Integrate Airflow with Docker for monitoring and execution.
- Test and visualise the ML pipeline via the Airflow web interface.

## Table of Contents

1. What is an ML pipeline?
2. Setting up the environment for Apache Airflow
3. Creating a DAG file to schedule Python operations
4. Creating the ML pipeline
5. Initialising Docker to monitor DAGs in the Apache Airflow webserver
6. Running and testing the DAGs


### 1. What is an ML Pipeline?

A Machine Learning (ML) pipeline is a structured workflow that automates and streamlines the process of developing and deploying a machine learning model. It encompasses several steps, starting from data collection and preprocessing to model training, evaluation, and deployment.


### 2. Setting up the Environment for Apache Airflow

#### Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
```

#### Install Python Development Tools
```bash
sudo apt install python3-pip python3-dev build-essential
```

#### Create and Activate the Virtual Environment
```bash
sudo pip3 install virtualenv
python3 -m venv newapp
source newapp/bin/activate
```

#### Set Airflow Home Directory
```bash
export AIRFLOW_HOME=~/airflow
```

#### Install Apache Airflow Using Pip
- Install with version constraints for compatibility:
```bash
AIRFLOW_VERSION=2.8.1
PYTHON_VERSION="$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
pip install "apache-airflow==${AIRFLOW_VERSION}" \
--constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
```

#### Initialise the Airflow Database
```bash
airflow db init
```

#### Start Airflow Webserver and Scheduler
```bash
airflow webserver --port 8080
airflow scheduler
```

### 3. Creating the DAG File to Schedule Python Operations

#### Example DAG File
```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from pipeline import (ingest_data, preprocess_data, train_model,
                      evaluate_model, deploy_model)

default_args = {
    'owner': 'your_name',
    'start_date': datetime(2024, 10, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'ml_pipeline',
    default_args=default_args,
    description='ML pipeline using Airflow',
    schedule_interval=timedelta(days=1),
)

t1 = PythonOperator(
    task_id='ingest_data',
    python_callable=ingest_data,
    dag=dag,
)

t2 = PythonOperator(
    task_id='preprocess_data',
    python_callable=preprocess_data,
    dag=dag,
)

t3 = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

t4 = PythonOperator(
    task_id='evaluate_model',
    python_callable=evaluate_model,
    dag=dag,
)

t5 = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
)

t1 >> t2 >> t3 >> t4 >> t5
```

### 4. Creating Python Functions for the Pipeline

#### Example Python Operators
```python
def ingest_data(**kwargs):
    # Your data ingestion code here
    pass

def preprocess_data(**kwargs):
    # Your data preprocessing code here
    pass

def train_model(**kwargs):
    # Your model training code here
    pass

def evaluate_model(**kwargs):
    # Your model evaluation code here
    pass

def deploy_model(**kwargs):
    # Your model deployment code here
    pass
```

### 5. Initialising Docker for Apache Airflow

#### Create a Docker Compose File
```yaml
services:
  airflow-init:
    image: apache/airflow:2.10.2
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    entrypoint: airflow db init

  airflow-webserver:
    image: apache/airflow:2.10.2
    depends_on:
      - airflow-init
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    ports:
      - "8081:8080"
    command: webserver

  airflow-scheduler:
    image: apache/airflow:2.10.2
    depends_on:
      - airflow-webserver
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    command: scheduler

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=airflow
      - POSTGRES_PASSWORD=airflow
      - POSTGRES_DB=airflow
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  postgres-data:
```

#### Create Required Directories
```bash
mkdir -p ./dags ./logs ./plugins ./config
```

#### Set Airflow User ID
```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```

#### Initialise the Airflow Database
```bash
docker compose up airflow-init
```

#### Start All Services
```bash
docker compose up -d
```

#### Monitor Running Containers
- Check running containers:
```bash
docker ps
```
- Stop all containers:
```bash
docker compose down
```

### 6. Running and Testing the Pipeline

#### Expose the Airflow GUI Using a Load Balancer
- Obtain the VM’s IP using `ifconfig`.
- Create a load balancer with the IP and port (e.g., 8081).

#### Access and Test DAGs
- Log in to the Airflow web interface.
- Visualise and monitor DAG execution.


## Conclusion

This guide demonstrates the orchestration of an ML pipeline using Apache Airflow, covering environment setup, DAG creation, and integration with Docker for streamlined execution and monitoring. The approach ensures efficiency, scalability, and ease of deployment for ML workflows.

