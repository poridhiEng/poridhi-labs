# Integration of S3 with Apache Airflow

**Tags**: Airflow, Docker, MLOps, S3  
**Class**: AF3  
**Created**: November 21, 2024, 1:02 PM

---

## Introduction

Amazon Simple Storage Service (S3) is a highly scalable and durable object storage service provided by AWS. Integrating S3 with Apache Airflow allows us to automate workflows involving data storage and processing in S3 buckets. This experiment demonstrates how to set up this integration and schedule related tasks in Apache Airflow. The setup concludes with monitoring the process via Airflow's web interface deployed using a load balancer.

---

## Objectives

- Integrate Apache Airflow with AWS S3.
- Automate S3 operations such as creating, uploading to, and deleting buckets using Airflow.
- Monitor and manage tasks via the Airflow GUI.

---

## Table of Contents

1. What is S3?
2. Setup your environment
3. AWS account creation
4. Setting up the connection in Apache Airflow
5. VSCode environment setup
6. Issues and troubleshooting

---

### 1. What is S3?

Amazon Simple Storage Service (S3) is **a massively scalable object storage service** designed for high durability, availability, and performance. Data stored in S3 can be accessed via the Internet through the AWS Console or S3 API.

**Features:**
- Object-based storage
- Scalability and high availability
- Access via API or console

![S3 Diagram](Screenshots/Airflowlab3.svg)

---

### 2. Setup Your Environment

#### Step 2.1: Install Required Tools

1. **Install Homebrew:**
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Visual Studio Code:**
   ```bash
   brew install --cask visual-studio-code
   ```

3. **Install Docker:**
   ```bash
   brew install --cask docker
   ```

4. **Install Python:**
   ```bash
   brew install python
   ```

5. **Install AWS CLI:**
   ```bash
   brew install awscli
   ```

---

### 3. AWS Account Creation

#### Step 3.1: Install AWS CLI

1. Download and install AWS CLI:
   ```bash
   curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
   unzip awscliv2.zip
   sudo ./aws/install
   ```
2. Verify installation:
   ```bash
   aws --version
   ```

#### Step 3.2: Configure AWS CLI

1. Configure AWS CLI:
   ```bash
   aws configure
   ```
   - Provide **ACCESS_KEY** and **SECRET_ACCESS_KEY** (generated from Poridhi Lab).

![AWS Configuration](Screenshots/image-01.png)

---

### 4. Setting Up the Connection in Apache Airflow

1. Access the Airflow GUI:
   - Open [localhost:8080](http://localhost:8080) and log in using the previously created credentials.

2. Create a new connection:
   - Navigate to **Admin > Connections > Add [+]**.

3. Fill in the connection details:
   - Use the generated **Access Key** and **Secret Key**.

![Airflow Connection](Screenshots/image-02.png)

---

### 5. VSCode Environment Setup

#### Step 5.1: Update the System

1. Update and upgrade packages:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. Create a new directory for the project:
   ```bash
   mkdir airflow-s3-project
   cd airflow-s3-project
   ```

3. Create and activate a virtual environment:
   ```bash
   python3 -m venv s3
   source s3/bin/activate
   ```

#### Step 5.2: Install Required Libraries

1. Install Apache Airflow:
   ```bash
   pip install apache-airflow
   ```
   or with version constraints:
   ```bash
   AIRFLOW_VERSION=2.7.3
   PYTHON_VERSION="$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
   CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
   pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
   ```

2. Install Airflow with Amazon Provider:
   ```bash
   pip install apache-airflow apache-airflow-providers-amazon
   ```

#### Step 5.3: Set Up Docker Compose

1. Download the Docker Compose YAML file:
   ```bash
   curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.7.1/docker-compose.yaml'
   ```

2. Create an `.env` file:
   ```bash
   echo -e "AIRFLOW_UID=$(id -u)\nAIRFLOW_GID=0" > .env
   ```

3. Update the `docker-compose.yaml` file:
   ```yaml
   AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID}
   AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY}
   AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}
   ```
   Use the credentials generated from Poridhi Lab.

4. Create a DAGs folder:
   ```bash
   mkdir ./dags
   ```

5. Add a Python DAG file `s3_integration_dag.py` to the `dags` folder:
   ```python
   from airflow import DAG
   from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3DeleteBucketOperator
   from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
   from datetime import datetime, timedelta

   default_args = {
       'owner': 'airflow',
       'depends_on_past': False,
       'start_date': datetime(2024, 10, 6),
       'email_on_failure': False,
       'email_on_retry': False,
       'retries': 1,
       'retry_delay': timedelta(minutes=5),
   }

   dag = DAG(
       's3_integration_example',
       default_args=default_args,
       description='A simple DAG to demonstrate S3 integration',
       schedule=timedelta(days=1),
   )

   create_bucket = S3CreateBucketOperator(
       task_id='create_bucket',
       bucket_name='my-airflow-bucket-{}'.format(datetime.now().strftime('%Y%m%d%H%M%S')),
       region_name='us-east-1',
       aws_conn_id='aws_default',
       dag=dag,
   )

   upload_file = LocalFilesystemToS3Operator(
       task_id='upload_file',
       filename='/path/to/local/file.txt',
       dest_key='file.txt',
       dest_bucket='{{ task_instance.xcom_pull(task_ids="create_bucket") }}',
       aws_conn_id='aws_default',
       dag=dag,
   )

   delete_bucket = S3DeleteBucketOperator(
       task_id='delete_bucket',
       bucket_name='{{ task_instance.xcom_pull(task_ids="create_bucket") }}',
       force_delete=True,
       aws_conn_id='aws_default',
       dag=dag,
   )

   create_bucket >> upload_file >> delete_bucket
   ```

#### Step 5.4: Start Airflow Services

1. Build and start Airflow services:
   ```bash
   docker-compose up --build
   ```

2. Start services in detached mode:
   ```bash
   docker-compose up -d
   ```

---

### 6. Launch the Airflow GUI Using the Load Balancer

1. Access the Airflow dashboard.
   - Log in using the credentials created earlier.

2. Enable and trigger the DAG from the Airflow UI.

3. Monitor the DAG execution and view results.

4. Stop Docker containers when done:
   ```bash
   docker-compose down
   ```

---

## Issues and Troubleshooting

**Issue 1: Unable to Log In to Airflow GUI**

- Verify user creation:
   ```bash
   docker exec -it s3airflow-airflow-webserver-1 airflow users list
   ```
- Synchronise the database:
   ```bash
   docker-compose restart airflow-webserver
   ```
   or:
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

**Issue 2: DAG Not Triggering**

- Check if the DAG file is in the `dags` folder.
- Ensure the DAG ID matches the file name.
   ```bash
   ls -l dags/s3_integration_example.py
   ```
- Restart services:
   ```bash
   docker-compose restart
   ```

---

## Conclusion

This guide demonstrates integrating AWS S3 with Apache Airflow, automating bucket operations, and scheduling tasks. By leveraging Airflow's orchestration capabilities, you can streamline workflows involving S3 while efficiently monitoring and managing them through the Airflow GUI.