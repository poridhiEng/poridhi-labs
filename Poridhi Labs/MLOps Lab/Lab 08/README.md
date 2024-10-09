# Remote MLflow Tracking Server: Deploying on EC2 with PostgreSQL Backend and S3 Registries Using Pulumi


In this lab, we'll set up an MLflow tracking server on an EC2 instance, leveraging Pulumi to manage the infrastructure. The tracking server will use PostgreSQL as the backend store (running on the same EC2 instance) and configure two S3 buckets for artifact and model registries. This setup is highly scalable, providing a robust MLOps infrastructure for managing the lifecycle of machine learning experiments.

![](./images/x3.svg)

### Objectives
- Set up infrastructure (VPC, EC2, S3) using Pulumi
- Install and configure PostgreSQL for the MLflow backend
- Configure S3 buckets for storing artifacts and models
- Install MLflow and run the tracking server on EC2
- Connect a remote client to the MLflow tracking server and run a sample experiment



## Task description

1. Set up Infrastructure with Pulumi
2. Install and Configure PostgreSQL
3. Install and Configure MLflow
4. Start MLflow Tracking Server
5. Configure Client for Remote Tracking
6. Run a Sample MLflow Experiment



## Step 1: Set Up Infrastructure with Pulumi

In this step, we'll set up the necessary AWS resources like VPC, EC2 instance, and S3 buckets using Pulumi.

### 1. Configure AWS CLI
If you haven't configured your AWS CLI yet, do it now:
```bash
aws configure
```
Enter your AWS Access Key ID, Secret Access Key, and preferred region.

### 2. Set up Pulumi Project
1. Create a directory for the project and initialize the Pulumi project:
    ```bash
    mkdir mlops-lab-test
    cd mlops-lab-test
    ```

2. Install Python 3.8 virtual environment if it's not already available:
    ```bash
    sudo apt update
    sudo apt install python3.8-venv
    ```

3. Initialize a Pulumi project:
    ```bash
    pulumi new aws-python
    ```

### 3. Create Key Pair for EC2 Instance
To securely access your EC2 instance, create an SSH key pair:
```bash
aws ec2 create-key-pair --key-name key-pair-poridhi-poc --query 'KeyMaterial' --output text > key-pair-poridhi-poc.pem
```

Provide permisssion for this key:
```bash
chmod 400 key-pair-poridhi-poc.pem
```


### 4. Python Code for Infrastructure Setup

In the same directory, use the following Pulumi Python code to set up your EC2 instance, VPC, security groups, and S3 buckets:

```python
import pulumi
import pulumi_aws as aws
import os

# Create a VPC
vpc = aws.ec2.Vpc("poridhi-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={
        'Name': 'poridhi-vpc',
    }
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway("poridhi-igw",
    vpc_id=vpc.id,
)

# Create a Public Subnet
subnet = aws.ec2.Subnet("poridhi-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True
)

# Create a route table
route_table = aws.ec2.RouteTable("poridhi-route-table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=internet_gateway.id,
    )]
)

# Associate the subnet with the route table
route_table_association = aws.ec2.RouteTableAssociation("poridhi-rt-association",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Security Group allowing SSH, Custom TCP, and PostgreSQL
security_group = aws.ec2.SecurityGroup("poridhi-security-group",
    description="Security group for SSH, Custom TCP, and PostgreSQL",
    vpc_id=vpc.id,
    ingress=[
        { 'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ["0.0.0.0/0"] },
        { 'protocol': 'tcp', 'from_port': 5000, 'to_port': 5000, 'cidr_blocks': ["0.0.0.0/0"] },
        { 'protocol': 'tcp', 'from_port': 5432, 'to_port': 5432, 'cidr_blocks': ["0.0.0.0/0"] }
    ],
    egress=[
        { 'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0'] }
    ]
)

# Create the EC2 instance
mlflow_server = aws.ec2.Instance('mlflow-server',
    instance_type='t3.small',
    ami='ami-01811d4912b4ccb26',
    vpc_security_group_ids=[security_group.id],
    subnet_id=subnet.id,
    key_name='key-pair-poridhi-poc', 
    ebs_block_devices=[
        aws.ec2.InstanceEbsBlockDeviceArgs(
            device_name="/dev/sda1",
            volume_type="gp3",
            volume_size=20,
            delete_on_termination=True,
        ),
    ],
    tags={
        'Name': 'mlflow-server',
    }
)

# Output the public and private IP addresses
pulumi.export('mlflow_server_private_ip', mlflow_server.private_ip)
pulumi.export('mlflow_server_public_ip', mlflow_server.public_ip)

# Create artifacts store bucket
mlflow_artifacts_bucket = aws.s3.Bucket("poridhi-mlflow-artifacts-123",
    acl="private",  
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create model store bucket
mlflow_models_bucket = aws.s3.Bucket("poridhi-mlflow-models-123",
    acl="private",  
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Export the names of the created buckets
pulumi.export('mlflow_artifacts_bucket_name', mlflow_artifacts_bucket.id)
pulumi.export('mlflow_models_bucket_name', mlflow_models_bucket.id)
```

### 5. Preview pulumi creation
Prevew the resources to be created by pulumi:
```bash
pulumi preview
```

Expected output:

![alt text](./images/image-1.png)

### 6. Run Pulumi:
Run the pulumi command to create the infrastructure:
```bash
pulumi up --yes
```
This will create the infrastructure on AWS.

Expected output:

![alt text](./images/image-2.png)



## Step 2: Install and Configure PostgreSQL

### 1. SSH into your EC2 instance
```bash
ssh -i key-pair-poridhi-poc.pem ubuntu@<your-ec2-public-ip>
```
Replace <your-ec2-public-ip> with valid Public IP address of your EC2 instance.

### 2. Update the system and install PostgreSQL
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

### 3. Initialize and start PostgreSQL:

On Ubuntu, PostgreSQL is automatically initialized, so you only need to start and enable the service:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4. Set up PostgreSQL for MLflow:

Go to the postgresql:
```bash
sudo -u postgres psql
```

Crate database, user and set necessary permissions:
```bash
CREATE DATABASE mlflow;

CREATE USER mlflow WITH ENCRYPTED PASSWORD 'mlflow';

GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow;
\c mlflow
GRANT ALL PRIVILEGES ON SCHEMA public TO mlflow;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mlflow;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO mlflow;

\q
```
Explanation for PostgreSQL operations:

1. **Create MLflow Database**: Set up a dedicated PostgreSQL database for MLflow.

2. **Create MLflow User**: Create a user named `mlflow` with an encrypted password for secure access.

3. **Grant Privileges on Database**: Assign full privileges to the `mlflow` user on the newly created database.

4. **Connect to MLflow Database**: Switch to the `mlflow` database to continue with schema and table privilege setup.

5. **Grant Privileges on Schema**: Ensure `mlflow` user has all privileges on the public schema.

6. **Grant Privileges on Tables**: Provide `mlflow` user full control over all tables in the public schema.

7. **Set Default Privileges**: Configure default privileges for any future tables created in the public schema to automatically grant all privileges to `mlflow` user.


### 5. Configure PostgreSQL to Accept Remote Connections
Open the PostgreSQL configuration file (`postgresql.conf`) and modify the `listen_addresses` setting to allow connections from any IP address by setting it to `'*'`.

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```
Uncomment and modify:
```
listen_addresses = '*'
```

### 6. Modify `pg_hba.conf`

Edit the `pg_hba.conf` file to enable authentication for remote connections. Add a rule to allow all users from any IP address (`0.0.0.0/0`) to connect using password-based authentication (`md5`).

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add the following:

```
host    all             all             0.0.0.0/0               md5
```

### 7. Restart PostgreSQL
```bash
sudo systemctl restart postgresql
```



## Step 3: Install and Configure MLflow

In the `EC2 instace`, run the following command:

1. Install Python 3:
    ```bash
    sudo apt install python3-pip -y
    ```
2. Setup and activate virtual environment:

    ```bash
    sudo apt update
    sudo apt install -y python3-venv
    python3 -m venv mlflow-venv
    source mlflow-venv/bin/activate
    ```

3. Install mlflow and boto3:
    ```
    pip3 install mlflow boto3 psycopg2-binary
    ```

4. Varify mlflow installation:
    ```bash
    mlflow --version
    ```    


## Step 4: Start MLflow Tracking Server

In the `EC2 instace`, run the following command:

1. Install AWS CLI:
    ```bash
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    sudo apt update && sudo apt install unzip
    unzip awscliv2.zip
    sudo ./aws/install
    ```

1. Configure AWS CLI on the EC2 instance:
    ```bash
    aws configure
    ```

2. Create a startup script for the MLflow server:
    ```bash
    nano ~/start_mlflow.sh
    ```
    Add the following content:
    ```bash
    mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri postgresql://mlflow:mlflow@localhost/mlflow \
    --default-artifact-root s3://<your-mlflow-artifacts> \
    --artifacts-destination s3://<your-mlflow-artifacts> \
    --serve-artifacts
    ```

    Replace `<your-mlflow-artifacts>` with your s3 bucket name for artifacts store.

3. Make the script executable:
    ```bash
    chmod +x ~/start_mlflow.sh
    ```

4. Start the MLflow server:
    ```bash
    ~/start_mlflow.sh
    ```

    Expected output:

    ![alt text](./images/image.png)

5. MLflow server has been started successfully. Now visit `<EC2-public-IP>:5000` from browser, you will see the server:

    ![alt text](./images/image-5.png)


## Step 5: Configure Client for Remote Tracking

Now exit from the EC2 server and run the following command in your local environment:

1. Install MLflow and its dependencies on your local machine:
    ```bash
    pip install mlflow boto3
    ```

2. Set environment variables:
    ```bash
    export MLFLOW_TRACKING_URI=http://<your-ec2-public-ip>:5000
    export MLFLOW_S3_ENDPOINT_URL=https://s3.<your-region>.amazonaws.com
    ```

    Replace `<your-ec2-public-ip>` with the public IP address of your EC2 instance and  `<your-region>` with `ap-southeast-1`.


## Step 6: Run a Sample MLflow Experiment

Create a new Python file `mlflow_example.py`.

Create and run a simple MLflow experiment to test the tracking server:

```python
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Set the experiment name
mlflow.set_experiment("diabetes-prediction")

# Load the diabetes dataset
diabetes = load_diabetes()
X, y = diabetes.data, diabetes.target

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Calculate MSE
mse = mean_squared_error(y_test, predictions)

# Log parameters, metrics, and model with MLflow
with mlflow.start_run():
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("mse", mse)
    mlflow.sklearn.log_model(model, "random_forest_model")

print(f"Model trained and logged to MLflow. MSE: {mse}")
```

Run the example:
```bash
python3 mlflow_example.py
```

Expected output:

![alt text](./images/image-4.png)

After running the experiment, you can visit the MLflow UI at `http://<your-ec2-public-ip>:5000` and check the stored artifacts and model registries in the respective S3 buckets.

![alt text](./images/image-3.png)

## Conclusion

You have successfully set up an MLflow tracking server on an EC2 instance with PostgreSQL and S3 for artifact and model storage. This infrastructure enables seamless tracking and management of machine learning experiments.