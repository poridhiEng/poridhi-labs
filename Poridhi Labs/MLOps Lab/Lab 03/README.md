# Feature Engineering With Ray And AWS

The following diagram demonstrates data pipeline for this lab as well as the upcoming lab. In this lab, we will be doing only half of the pipeline.

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-9.png?raw=true)


You will use the `stagingdatastorebucket` to utilize as a staging data store where all the raw data will be stored from the sources. In this scenario, you won't connect any data connectors, API, databases or any other sources but this data engineering practice would be common throughout the course and other labs.

After ingesting the raw dataset into our transformation script you would perform some transformations and feature engineering/creation tasks. After processing the raw dataset and computing the necessary features for the ML model training, the transformed data would be stored in `featurestorebucket`. We will discuss a lot about this in the upcoming section. The remaining part of the pipeline will be explained in the next lab.


## Task Description

In this lab, we will:

- AWS CLI configuration
- Create AWS infrastructure (VPC, instance, S3 bucket) using Pulumi
- Clone the repository that contains the notebook for this lab
- Run the jupyter lab 
- Attach an IAM Role to the EC2 Instances for S3 Buckets permissions
- Run the notebook `1. data-transformation-and-feature-store.ipynb`


## AWS CLI Configuration

Run the following command to configure AWS CLI:

```bash
aws configure
```

This command prompts you for your AWS Access Key ID, Secret Access Key, region, and output format.


## Set Up a Pulumi Project

### Set Up a new directory
Create a new directory for your project and navigate into it:

```sh
mkdir aws-pulumi-infra
cd aws-pulumi-infra
```

### Install python `venv`

```sh 
sudo apt update
sudo apt install python3.8-venv
```

### Initialize a New Pulumi Project
Run the following command to create a new Pulumi project:

```sh
pulumi new aws-python
```
Follow the prompts to set up your project.

### Create Key Pair

Create a new key pair in the `~/.ssh/` directory for the instances using the following command:

```sh
cd ~/.ssh/

aws ec2 create-key-pair --key-name key-pair-poridhi-poc --query 'KeyMaterial' --output text > key-pair-poridhi-poc.pem
```

These commands will create key pair for our instances.

### Set File Permissions of the key files

```sh
chmod 400 key-pair-poridhi-poc.pem
```


### Write the scripts

1. Open a directory named `scripts`

    ```sh
    mkdir scripts
    ```

2. Create a file named `head_node_user_data.txt` and add the following code to it

    ```sh
    #!/bin/bash

    # Change to the home directory
    cd /home/ubuntu/

    # Update the package list and install necessary software properties
    sudo apt-get update
    sudo apt-get install -y software-properties-common

    # Add the deadsnakes PPA and install Python 3.9 and related packages
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.9 python3.9-venv python3.9-dev

    # Create a Python virtual environment and activate it
    python3.9 -m venv ray_env
    source ray_env/bin/activate

    # Install Python libraries within the virtual environment
    pip install boto3 pyarrow numpy pandas matplotlib seaborn plotly scikit-learn xgboost -U ipywidgets

    # Install jupyter lab
    pip install jupyterlab

    # Install Ray and start Ray as the head node
    pip install "ray[default] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp39-cp39-manylinux2014_x86_64.whl"

    # Install ray server
    pip install "ray[serve]"

    # Install py-ubjson
    pip install py-ubjson

    # Install modin-ray
    pip install modin[ray]

    # Install mlflow
    pip install mlflow

    # Install missingno
    pip install missingno

    ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --include-dashboard=True

    # Check Ray's status
    ray status
    ```
3. Create a file named `worker_node_common_data.txt` and add the following code to it

    ```sh
    #!/bin/bash

    cd /home/ubuntu/

    # Update the package list and install necessary software properties
    sudo apt-get update
    sudo apt-get install -y software-properties-common

    # Add the deadsnakes PPA and install Python 3.9 and related packages
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.9 python3.9-venv python3.9-dev

    # Create a Python virtual environment and activate it
    python3.9 -m venv ray_env
    source ray_env/bin/activate

    # Install Python libraries within the virtual environment
    pip install boto3 pyarrow numpy pandas matplotlib seaborn plotly scikit-learn xgboost -U ipywidgets

    # Install jupyter lab
    pip install jupyterlab

    # Install Ray and start Ray as the head node
    pip install "ray[default] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp39-cp39-manylinux2014_x86_64.whl"

    # Install ray server
    pip install "ray[serve]"

    # Install py-ubjson
    pip install py-ubjson

    # Install modin-ray
    pip install modin[ray]

    # Install mlflow
    pip install mlflow

    # Install missingno
    pip install missingno
    ```



### Edit the pulumi code in `__main__.py` file:

```py
import pulumi
import pulumi_aws as aws
import os

# Create a VPC
vpc = aws.ec2.Vpc("micro-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway("micro-igw",
    vpc_id=vpc.id
)

# Create a Public Subnet
subnet = aws.ec2.Subnet("micro-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True
)

# Create a route table
route_table = aws.ec2.RouteTable("micro-route-table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=internet_gateway.id,
    )]
)

# Associate the subnet with the route table
route_table_association = aws.ec2.RouteTableAssociation("micro-route-table-association",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Security Group allowing SSH and HTTP
security_group = aws.ec2.SecurityGroup("micro-sec-group",
    vpc_id=vpc.id,
    description="Allow SSH and HTTP",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=6379,
            to_port=6382,
            cidr_blocks=['0.0.0.0/0'],  # Allow from anywhere
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=1024,
            to_port=65535,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)

# Read the head_node_user_data.txt file. Update your path accordingly
with open('/root/code/scripts/head_node_user_data.txt', 'r') as file:
    head_node_user_data = file.read()

# Create the head node
head_node = aws.ec2.Instance('head-node',
    instance_type='t3.medium',
    ami='ami-01811d4912b4ccb26',
    vpc_security_group_ids=[security_group.id],
    subnet_id=subnet.id,
    user_data=head_node_user_data, # pass the head-node-user-data
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
      'Name': 'head-node',
    }
)

# Read the worker_node_common_data.txt user. Update your path accordingly
with open('/root/code/scripts/worker_node_common_data.txt', 'r') as file:
    worker_node_common_data = file.read()


# Create worker nodes
worker_nodes = []
for i in range(2):
    worker_node_user_data = head_node.private_ip.apply(lambda ip: worker_node_common_data  + f"""
ray start --address='{ip}:6379'
""") # The private IP of the head node is passed dynamically to the worker nodes, so they can connect to the head node via Ray (ray start command).
    worker_node = aws.ec2.Instance(f'worker-node-{i+1}',
        instance_type='t3.small',
        ami='ami-01811d4912b4ccb26',
        vpc_security_group_ids=[security_group.id],
        subnet_id=subnet.id,
        user_data=worker_node_user_data, # pass the worker node user data
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
            'Name': f'worker-node-{i+1}',
        }
    )
    worker_nodes.append(worker_node)

# Output the public and private IP addresses
pulumi.export('head_node_private_ip', head_node.private_ip)
pulumi.export('head_node_public_ip', head_node.public_ip)

# Export the worker node public and private ip
for i, worker_node in enumerate(worker_nodes):
    pulumi.export(f'worker_node_{i+1}_private_ip', worker_node.private_ip)
    pulumi.export(f'worker_node_{i+1}_public_ip', worker_node.public_ip)


# Create a dynamic config file for SSH access
def create_config_file(ip_list):
    # Define the hostnames for each IP address
    hostnames = ['headnode', 'worker1', 'worker2']
    
    config_content = ""
    
    # Iterate over IP addresses and corresponding hostnames
    for hostname, ip in zip(hostnames, ip_list):
        config_content += f"Host {hostname}\n"
        config_content += f"    HostName {ip}\n"
        config_content += f"    User ubuntu\n"
        config_content += f"    IdentityFile ~/.ssh/key-pair-poridhi-poc.pem\n\n"
    
    # Write the content to the SSH config file
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

# Collect the IPs for all nodes
all_ips = [head_node.public_ip] + [worker_node.public_ip for worker_node in worker_nodes]

# Create the config file with the IPs once the instances are ready
pulumi.Output.all(*all_ips).apply(create_config_file)


# Create Staging S3 bucket with unique names
staging_data_store_bucket = aws.s3.Bucket("stagingdatastorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create Feature store bucket
feature_store_bucket = aws.s3.Bucket("featurestorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create Model store bucket
model_store_bucket = aws.s3.Bucket("modelstorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create Results store bucket
results_store_bucket = aws.s3.Bucket("resultsstorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Export the names of the created buckets
pulumi.export('staging_data_store_bucket_name', staging_data_store_bucket.id)
pulumi.export('feature_store_bucket_name', feature_store_bucket.id)
pulumi.export('model_store_bucket_name', model_store_bucket.id)
pulumi.export('results_store_bucket_name', results_store_bucket.id)
```

### Deploy the Pulumi Stack

Deploy the stack using the following command:

```sh
pulumi up
```
Review the changes and confirm by typing `yes`.

### Check the Ray Status on the Head Node

1. **SSH into the Head Node:**

   First, log into the head node using SSH and activate the `ray_env`.

   ```sh
   ssh headnode
   source ray_env/bin/activate
   ```

2. **Check Ray Cluster Status:**

   After logging in, run the following command to check the status of the Ray cluster:

   ```sh
   ray status
   ```

   > **Note:** It may take a few minutes for all nodes to connect and the cluster to become fully operational after deployment. Be patient while the system initializes.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-7.png?raw=true)

   


## Change File Ownership and Permissions

In some cases, certain directories or files may have restricted permissions or be owned by the `root` user, which can interfere with the smooth operation of Ray or cause permission-related issues. To prevent this, adjust the ownership and permissions as follows:

1. **Change Ownership of the Ray Environment Directory:**

   To change ownership of the Ray environment directory to the `ubuntu` user, run the following command:

   ```sh
   sudo chown -R ubuntu:ubuntu /home/ubuntu/ray_env
   ```

   This command recursively modifies the ownership of all files and directories under `/home/ubuntu/ray_env`, ensuring the `ubuntu` user has full control.

2. **Change Ownership of the Ray Temporary Files:**

   Similarly, you may also need to adjust the ownership of the Ray-related files in the `/tmp/ray` directory. Run:

   ```sh
   sudo chown -R ubuntu:ubuntu /tmp/ray/*
   ```

   ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-8.png?raw=true)

   This ensures the `ubuntu` user has the necessary permissions to manage Ray processes, which often store temporary files in this location.




## Clone the Repository of this Lab

```bash
git clone https://github.com/Galadon123/ML.git
```

All the necessary files, notebooks are in this repo, change the directory to see the files. We’ll interact with them through Jupyter Lab later in this lab.
The notebook required for this lab is in the `MLOPS-LAB-2` directory. We will running `1.data-transformation-and-feature-store.ipynb` notebook.

```bash
cd ML
cd MLOPS-LAB-2
```

## Run Jupyter Lab

SSH into headnode and activate the ray_env:

```bash
ssh headnode
source ray_env/bin/activate
```

Run the following commands to create a configuration file for the Jupyter Lab:

```bash
jupyter lab --generate-config
mkdir -p ~/.jupyter
touch ~/.jupyter/jupyter_lab_config.py
nano ~/.jupyter/jupyter_lab_config.py
```

This commands will open a config file as follows:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-10.png?raw=true)

Add the following configuration:

```
# Allow all IP addresses to connect
c.ServerApp.ip = '0.0.0.0'

# Allow the server to be accessible from the public internet
c.ServerApp.open_browser = False

# Set the port (default is 8888)
c.ServerApp.port = 8888
```

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-11.png?raw=true)

Now, save and exit the file. 

Head back to the head node and change the directory to the cloned repo. Start the jupyter lab (Make sure you are in the right directory). 

```bash
jupyter lab
```

Jupyter lab will be started on port `8888`.

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-5.png?raw=true)

Go to a browser and paste the URL marked in the picture. Replace `headnode` with the `public-ip` of the headnode instance.

All the necessary files for our problem are already in this working directory.

## Attach an IAM Role to the EC2 Instances for S3 Buckets permissions

Let’s create an IAM role with the necessary permissions for EC2 instances to write to our S3 buckets.

### Create an IAM Role

- Go to the IAM console and create a new role.
- Select trusted entity type as `AWS service` and usecase as `EC2` as we are creating the role for EC2 instances.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image.png?raw=true)

- Give a name to the role and click `Create role`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-2.png?raw=true)

### Attach Policy for Permissions

- On the role summary page, under the "Permissions" tab, click on the "Add permissions" button.
- Choose `Create inline policy`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-1.png?raw=true)
    

- Attach the following `json` file in the policy editor:

    Replace the bucket names with your actual bucket names.

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:ListBucket",
                    "s3:ListBucketVersions"
                ],
                "Resource": [
                    "arn:aws:s3:::stagingdatastorebucket-unique-name-321-bf73fa4",
                    "arn:aws:s3:::stagingdatastorebucket-unique-name-321-bf73fa4/staging-directory/*",
                    "arn:aws:s3:::featurestorebucket-unique-name-321-0c6657a",
                    "arn:aws:s3:::featurestorebucket-unique-name-321-0c6657a/*",
                    "arn:aws:s3:::modelstorebucket-unique-name-321-9847f67",
                    "arn:aws:s3:::modelstorebucket-unique-name-321-9847f67/*",
                    "arn:aws:s3:::resultsstorebucket-unique-name-321-0876e55",
                    "arn:aws:s3:::resultsstorebucket-unique-name-321-0876e55/*"
                ]
            }
        ]
    }
    ```
    

  ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-1.jpg?raw=true)

### Attach the Role to EC2 instances

- Go to the EC2 Dashboard.
- Select the instances you created (`headnode`, `worker1`, `worker2`), to attach the role.
- Click on Actions > Security > Modify IAM Role.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-6.png?raw=true)

- In the dropdown list, you should see the role you created. Select it and click `Update IAM Role`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-4.png?raw=true)

- Repeat these steps for worker nodes also.

## Run the `Data Transformation & Feature Store` Notebook

Here’s a detailed explanation of the steps and why each of them is important in the context of preparing a dataset for machine learning, specifically for our dataset.

### 1. **Setting Up the Environment**
   - **AWS Setup with `boto3`**: 
     -    AWS S3 is being used as a data storage solution, particularly because it’s scalable, durable, and can handle large datasets efficiently. Setting up `boto3`, the AWS SDK for Python, allows you to interact programmatically with S3 buckets where the data will be stored, processed, and later retrieved.
     -  This setup is critical because it ensures secure and organized storage of the datasets, which is essential for a reproducible and scalable machine learning workflow.

   - **S3 Bucket Interaction**:
     -    Listing the S3 buckets helps in verifying that the necessary storage infrastructure (like buckets for staging, feature store, and model store) is in place.
     -  This is necessary to confirm that the data pipelines will function as expected, with each bucket serving a specific purpose in the workflow (e.g., storing raw data, processed features, or model outputs).

### 2. **Data Ingestion**
   - **Upload Raw Data**:
     -    The raw dataset is uploaded to a staging S3 bucket. This dataset contains the energy consumption data, which is the primary input for the machine learning model.
     -  Staging the data in S3 ensures that it is securely stored and easily accessible for further processing steps. This also allows for version control of data and easy integration with various data processing tools.

        ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-12.png?raw=true)

   - **Load Data from S3**:
     -    The dataset is read from the staging bucket into a `Ray` dataset, a distributed data processing framework that can handle large-scale data operations efficiently.
     -  Using `Ray` allows for parallelized data processing, which speeds up the workflow, making it more efficient and scalable, especially for large datasets.

### 3. **Exploratory Data Analysis (EDA)**
   - **Visualization with `plotly`**:
     -    Visualize the energy consumption trends over time to understand the data's underlying patterns, such as peak usage hours or seasonal variations.
     -  EDA is crucial for uncovering insights and identifying trends in the data that will inform feature engineering and model selection. Visualizing data helps in making informed decisions about which features are important for predicting energy consumption.

   - **Key Findings**:
     -    Identify the key trends, such as high energy consumption during summer months and lower usage in other seasons.
     -  Understanding these patterns is essential for building accurate predictive models. It highlights the need to account for seasonality and time-based trends in the modeling process.

### 4. **Feature Engineering**
   - **New Features Creation**:
     -    Develop new features that capture temporal and seasonal patterns, such as `TimeOfDay` and `Season`.
     -  These new features help the machine learning model better understand the context in which energy is consumed, leading to more accurate predictions. For example, energy usage patterns differ significantly between morning and evening, so creating a `TimeOfDay` feature allows the model to learn these differences.

   - **Batch Transformation**:
     -    Apply transformations to the dataset in batches to compute the new features across the entire dataset efficiently.
     -  Batch processing is efficient and scalable, allowing for the transformation of large datasets without overwhelming system resources.

### 5. **Data Cleaning and Preprocessing**
   - **Drop Unnecessary Columns**:
     -    Remove columns that are not needed for modeling to reduce noise and improve model performance.
     -  Simplifying the dataset by removing irrelevant columns can help in focusing the model on the most important features, thereby improving accuracy and reducing overfitting.

   - **Inspect Column Types**:
     -    Identify which columns are categorical and which are numerical to determine the appropriate preprocessing steps (like encoding for categorical variables).
     -  Proper identification of column types is essential for applying the right transformations, such as one-hot encoding for categorical data or scaling for numerical data.

### 6. **Encoding Categorical Variables**
   - **One-Hot Encoding**:
     -    Convert categorical variables (like `TimeOfDay` and `Season`) into numerical format using one-hot encoding.
     -  Machine learning models typically require numerical input. One-hot encoding allows the model to use categorical information without assuming any ordinal relationship between categories.

### 7. **Aggregation**
   - **Data Aggregation**:
     -    Group the data by `Year`, `Month`, `Day`, and `Hour` and aggregate values such as temperature and power consumption using methods like mean and sum.
     -  Aggregating the data into hourly intervals helps to reduce data dimensionality and focus on patterns over more significant time periods, which is important for time-series analysis and prediction. It also smooths out noise and makes the dataset more manageable for modeling.

### 8. **Lag Feature Creation**
   - **Lag Shifting**:
     -    Create lag features that represent previous values of key variables, such as temperature or power consumption, at different time intervals (e.g., 4 hours ago, 24 hours ago).
     -  Lag features help capture temporal dependencies in time-series data. For instance, energy consumption at a certain time is often influenced by consumption patterns in the preceding hours. Including lag features allows the model to learn from past behaviors, which is crucial for accurate forecasting.

### 9. **Feature Scaling**
   - **Scaling**:
     -    Normalize or scale the features so they have a common range, typically between 0 and 1 or -1 and 1.
     -  Scaling is important because many machine learning algorithms are sensitive to the range of input data. Features with larger ranges can disproportionately influence the model's predictions. Scaling ensures that each feature contributes equally to the model's decision-making process.

### 10. **Ray Dashboard**
   - **Monitor Processing**:
     -    Use the Ray dashboard `http://<head-node-public-ip>:8265` to monitor the execution of jobs on the dataset, ensuring that all tasks (like transformations, aggregations, and feature engineering) are completed correctly.
     -  Monitoring helps in identifying bottlenecks or errors in the data processing pipeline. It provides visibility into the progress of distributed tasks and ensures that the data is processed as expected before moving on to modeling.

        ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2003/images/image-13.png?raw=true)





Now open the Notebook: `1. data-transformation-and-feature-store.ipynb` and start running it on jupyter lab.


## Conclusion
The goal of this entire workflow is to transform raw energy consumption data into a well-structured, feature-rich dataset that can be used to train accurate and efficient machine learning models. Each step in this process—ranging from data ingestion and exploratory analysis to feature engineering and scaling—ensures that the data is clean, relevant, and prepared for predictive modeling, ultimately leading to better and more reliable predictions of energy consumption patterns.

