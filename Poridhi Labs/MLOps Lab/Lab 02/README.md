# Ray Cluster Deployment Automation

Welcome to this lab. In this we will deep dive into infrastructure deployment using Pulumi, an open-source infrastructure as code project. We will also **automate** the deployment of Ray clusters. Ray is a high-performance distributed execution framework targeted at large-scale machine learning and reinforcement learning applications.

By the end of this lab, you will have hands-on experience with Pulumi, how to automate the Ray cluster deployment.

## Overall Architecture

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/arch.png)

In this lab, we’ll create a ray cluster with 3 nodes, 

1. One Head Node,
2. Two Worker Nodes, 

Supported by the compute and networking infrastructure of AWS.

## Infrastructure Needed to set up Ray Cluster on AWS

Having the right network configurations and setup in AWS for Ray clusters is crucial for efficient distributed computing.  The compute setup, including the choice of EC2 instances and their configurations, directly impacts the performance and cost-effectiveness of the Ray cluster. 

### Compute Instances Configurations

1. **EC2 Instances**: AWS EC2 instances are used to host the Ray nodes. The instance type (e.g., t3.medium, t3.small) determines the hardware of the host computer.
2. **AMI (Amazon Machine Image)**: Provides the information required to launch an instance, which is a virtual server in the cloud.
3. **User Data Scripts**: These are used to bootstrap instances, installing necessary software and starting services. In the case of Ray, this might include installing Python, setting up a virtual environment, and installing and starting Ray.

4. **EBS (Elastic Block Store)**: Provides persistent block storage volumes for use with EC2 instances. It's used to store data that should persist beyond the life of the instance.

5. **Key Pair**: Used to securely connect to instances which you have already created and obtained from AWS console. It's crucial for managing the Ray cluster.

### Storage Capabilities

1. **S3 Buckets:** S3 is an object storage of AWS where data is stored in objects, which have three main components: the object’s content or data, a unique identifier for the object, and descriptive metadata including the object’s name, URL, and size

### Networking Configurations

1. **VPC (Virtual Private Cloud)**: An isolated network environment in AWS. It's the foundation of the AWS Cloud network.
2. **Internet Gateway**: Connects the VPC to the internet, enabling Ray nodes to communicate with the outside world.
3. **Subnet**: A segment of the VPC's IP address range where you can place groups of isolated resources. Ray nodes are placed in subnets.
4. **Route Table**: Directs traffic in the VPC. It's important to route traffic correctly between nodes and to/from the internet.
5. **Route Table Association**: Associates a subnet with a route table, ensuring that the Ray nodes in the subnet follow the correct routing rules.
6. **Security Group**: Acts as a virtual firewall for controlling inbound and outbound traffic. It's crucial to allow specific traffic (like SSH) for cluster management and inter-node communication.

## Task Description

In this hands-on lab we will learn 

- How to setup the required infrastructur (VPC, EC2 instances, S3 buckets) using pulumi. In the previous lab, we have installed and configured Ray cluster **manullay**. In this lab we will learn how to install the Ray clusters and necessary libraries in our EC2 instances automatically using **PULUMI**. 

- We will also create a **config** file **dynamically** to SSH into our ray nodes. This file allows us to define shortcuts and advanced SSH options, making the SSH process smoother and more efficient.

- We will config hostname for our EC2 instances so that we can easily identify them in our environment.

> **Note:** This lab is intended to be done in poridhi VS Code. So we will skip the aws cli installation, pulumi installation, and python installation steps as we these are already installed in the VS code environment.


## Step 01: AWS CLI Configuration

Run the following command to configure AWS CLI:

```bash
aws configure
```
![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image.png)


This command prompts you for your AWS Access Key ID, Secret Access Key, region, and output format.


##  Step 02: Set Up a Pulumi Project

### 1. Set Up a new directory
Create a new directory for your project and navigate into it:

```sh
mkdir MLOPS-Ray-cluster
cd MLOPS-Ray-cluster
```

### 2. Install python `venv`

```sh 
sudo apt update
sudo apt install python3.8-venv
```

### 3. Initialize a New Pulumi Project
Run the following command to create a new Pulumi project:

```sh
pulumi new aws-python
```
Follow the prompts to set up your project.

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-1.png)

### 4. Create Key Pair

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

## Step 03: Write Code for infrastructure creation

### Create a VPC

1. We start by creating a VPC using `aws.ec2.Vpc()`. The VPC has a CIDR block of `10.0.0.0/16`, providing up to 65,536 private IPv4 addresses. DNS support and DNS hostnames are enabled by setting `enable_dns_support=True` and `enable_dns_hostnames=True`. This is essential for our Ray cluster to operate in a secure, isolated network environment.
2. The VPC ID is stored in the `vpc.id` variable.

### Create an Internet Gateway

1. Next, an Internet Gateway is created using `aws.ec2.InternetGateway()`.
2. This Internet Gateway is attached to the VPC using the `vpc_id` parameter.
3. **Why we need an Internet Gateway (IGW):** It connects the VPC to the internet, enabling Ray nodes to communicate with the outside world, such as downloading dependencies.

### Create a Public Subnet

1. A public subnet is created using `aws.ec2.Subnet()` within the VPC.
2. The subnet has a CIDR block of `10.0.1.0/24` and is configured to map public IP addresses on launch by setting `map_public_ip_on_launch=True`.
3. **Why a Subnet is Needed:** It provides a segmented IP address range within the VPC where isolated resources, like Ray nodes, can be placed.

### Create a Route Table

1. A route table is created using `aws.ec2.RouteTable()` and associated with the VPC.
2. A route is added to this table, directing all traffic (`0.0.0.0/0`) to the Internet Gateway created earlier.
3. **Importance for Ray:** This setup ensures proper routing of traffic between Ray nodes and external networks.

### Associate the Subnet with the Route Table

1. The public subnet is associated with the route table using `aws.ec2.RouteTableAssociation()`.
2. The `subnet_id` and `route_table_id` parameters link the subnet and the route table, ensuring that traffic within the subnet follows the correct routing rules.

### Create a Security Group

1. A security group is created using `aws.ec2.SecurityGroup()` and is associated with the VPC.
2. The security group is configured with inbound rules to allow traffic on specific ports necessary for Ray:
    - **Port 22:** SSH access to remotely manage the nodes.
    - **Ports 80 and 443:** HTTP and HTTPS traffic for downloading dependencies or data.
    - **Port 6379:** Redis, used by Ray as its primary data store.
    - **Port 8265:** Ray dashboard access.
    - **Ports 1024-65535:** Ephemeral ports required for inter-node communication and various monitoring tools.
3. An outbound rule is added, allowing all traffic (`0.0.0.0/0`) to exit the VPC.

### Create the Head Node

1. The head node (EC2 instance) is created using `aws.ec2.Instance()` with the following configurations:
    - Instance type: `t3.medium`
    - AMI: `ami-01811d4912b4ccb26` (replace with the correct AMI ID)
    - Security group: the one created earlier
    - Subnet: the public subnet created earlier
    - Key pair: `key-pair-poridhi-poc` (replace with your key pair name)
    - EBS block device: a 20 GB GP3 volume
    - User Data: Injects the `head_node_user_data` script (from an external file) into the `headnode` on launch to run custom commands to install the necessary libraries and dependencies.

### Create the Worker Nodes

1. Two worker nodes (EC2 instances) are created using a loop and `aws.ec2.Instance()` with configurations similar to the head node:
    - Instance type: `t3.small`
    - AMI: `ami-01811d4912b4ccb26` (replace with the correct AMI ID)
    - Security group: the one created earlier
    - Subnet: the public subnet created earlier
    - Key pair: `key-pair-poridhi-poc` (replace with your key pair name)
    - EBS block device: a 20 GB GP3 volume
    - User Data: Injects the `worker_node_user_data` script (from an external file) into the `worker nodes` on launch to run custom commands to install the necessary libraries and dependencies.

### Create S3 Buckets

1. The code creates four S3 bucketseach with a unique name and versioning enabled. These buckets will serve as storage for

    - Staging raw datasets `(staging_data_store_bucket)`
    - Feature stores `(feature_store_bucket)`
    - Model training data `(model_store_bucket)`
    - Model outputs. `(results_store_bucket)`

### Export Outputs

The **public IP**, **private IP** addresses of the head node and worker nodes are exported as Pulumi outputs, along with the **names** of the S3 buckets.

## Write the scripts

### **1. Open a directory named `scripts`**

```sh
mkdir scripts
cd scripts
```
### **2. Create a file named `head_node_user_data.txt` and add the following code to it**

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
**3. Create a file named `worker_node_common_data.txt` and add the following code to it**

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

## Explanation of the script file

This script is designed to set up an environment on an EC2 instance to run distributed machine learning workloads with Ray, along with other essential tools. Here’s a breakdown of each part of the script:

### **Change to Home Directory**
```bash
cd /home/ubuntu/
```
This ensures that the commands are executed in the `/home/ubuntu/` directory, which is the home directory of the `ubuntu` user.

### **Update the Package List and Install Dependencies**

```bash
sudo apt-get update
sudo apt-get install -y software-properties-common
```
- **`sudo apt-get update`** refreshes the package list to ensure the latest versions of software are available for installation.
- **`software-properties-common`** is a utility that allows managing software repositories, such as adding third-party PPAs (Personal Package Archives).

### **Add the Deadsnakes PPA and Install Python 3.9**

```bash
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev
```
- **Deadsnakes PPA** provides newer versions of Python not available by default in the Ubuntu repositories. 
- **Python 3.9** is installed because it is needed for modern applications that may require features from this specific version.
- **`python3.9-venv`** provides the ability to create isolated Python environments, and **`python3.9-dev`** includes development headers needed for compiling Python extensions.

### **Create and Activate a Virtual Environment**

```bash
python3.9 -m venv ray_env
source ray_env/bin/activate
```
- A **virtual environment** (`ray_env`) is created to isolate the Python packages used for this project, preventing conflicts with other system packages.
- The **`source`** command activates the virtual environment, so that subsequent Python package installations and executions happen inside it.

### **Install Essential Python Libraries**

```bash
pip install boto3 pyarrow numpy pandas matplotlib seaborn plotly scikit-learn xgboost -U ipywidgets
```
Several popular Python libraries are installed:
- **`boto3`**: AWS SDK for Python, allowing interaction with AWS services like S3, EC2, etc.
- **`pyarrow`**: A cross-language development platform for in-memory data processing, useful with large datasets.
- **`numpy`**: Library for numerical operations.
- **`pandas`**: Data manipulation and analysis.
- **`matplotlib`, `seaborn`, `plotly`**: Visualization libraries for plotting and graphing data.
- **`scikit-learn`**: Machine learning library.
- **`xgboost`**: A powerful gradient boosting framework for supervised learning tasks.
- **`ipywidgets`**: Adds interactivity to Jupyter notebooks.

### **Install JupyterLab**

```bash
pip install jupyterlab
```
- **JupyterLab** is installed to provide an interactive notebook interface for development and experimentation with the above packages where we will run our notebooks.

### **Install Ray and Start the Head Node**

```bash
pip install "ray[default] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp39-cp39-manylinux2014_x86_64.whl"
```
- **Ray** is a distributed computing framework that allows running Python code on multiple machines (or nodes). This line installs Ray from a specific pre-built wheel compatible with Python 3.9.

```bash
ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --include-dashboard=True
```
- **Ray Head Node**: This command starts the Ray cluster in "head" mode, making this machine the central controller.

  - `--port=6379` specifies the Redis port that Ray uses for communication between nodes.
  - `--dashboard-host=0.0.0.0` exposes the Ray dashboard to external traffic.
  - `--dashboard-port=8265` sets the port for the Ray dashboard, providing a web-based interface to monitor cluster health and performance.

### **Install Additional Libraries**

```bash
pip install ray[serve] modin[ray] mlflow py-ubjson missingno
```
- **Ray Serve**: A library for building scalable machine learning models and applications with Ray.
- **Modin[ray]**: A library for accelerating pandas operations using Ray.
- **MLflow**: A platform for managing machine learning experiments, including tracking, deployment, and versioning.
- **Py-UBJSON**: A Python library for Universal Binary JSON, used for fast data serialization.
- **Missingno**: A visualization library for handling missing data in datasets.

### **Check Ray Status**

```bash
ray status
```
- This command checks the current status of the Ray cluster, showing which nodes are connected, resource availability, etc.

### Why These Installations are Necessary:
- **Distributed Computing**: Ray is essential for distributing the workload across multiple nodes in a cluster. Installing it as a head node on one machine and having worker nodes connect to it enables large-scale parallelism.
- **Data Science Tools**: Libraries like `numpy`, `pandas`, `scikit-learn`, and `xgboost` are fundamental for scientific computing, data processing, and machine learning tasks.
- **JupyterLab** provides a user-friendly interface for writing and testing Python code interactively.
- **MLflow** helps manage machine learning models and experiments, while **Modin[ray]** and **Ray Serve** are used to scale these workflows.

### **4. Write the infrastructure creation code in `__main__.py` file in your Pulumi project directory:**

```python
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
    key_name='key-pair-poridhi-poc', # Created Key-pair
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
        user_data=worker_node_user_data, # pass the worker_node_user_data
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

### Explanation of the `create_config_file(ip_list)`:

Here is the explanation of the `create_config_file` function in bullet points:

- **Purpose:** Generates a dynamic SSH configuration file for simplified SSH access to nodes in a distributed system.
- **Input:** A list of IP addresses corresponding to the head node and worker nodes.
- **Hostname assignment:** Predefined hostnames (`headnode`, `worker1`, `worker2`) are mapped to the IP addresses.
- **SSH configuration:** For each node, it adds:
  - Hostname (e.g., `headnode`, `worker1`, `worker2`)
  - IP address (`HostName`)
  - SSH user (`ubuntu`)
  - SSH private key (`~/.ssh/key-pair-poridhi-poc.pem`)
- **File output:** Writes the configuration to the `~/.ssh/config` file.
- **Function trigger:** Executed after all the EC2 instances are provisioned and their IP addresses are collected.
- **Result:** Allows SSH access using simple commands like `ssh headnode` or `ssh worker1`, instead of manually entering IP addresses and key details.


## Step 04: Deploy the Pulumi Stack

Deploy the stack using the following command:

```sh
pulumi up
```
Review the changes and confirm by typing `yes`.

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-2.png)

### Check the Created resources

**1. Go to `~/.ssh/` directory and check if config file is created dynamically**

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-3.png)

**2. Go to the AWS management console to check the created resources**

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-4.png)

**3. Check the SSH connection**

```sh
ssh headnode
ssh worker1
ssh worker2
```

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-5.png)


## Step 05: Set the hostname of the instances

We can set the hostname for our instances by using the `hostnamectl` command. This will help us to easily identify at which instance we are now after we ssh into any instance.


- SSH into the headenode instance and use the following command:

    ```bash
    sudo hostnamectl set-hostname headnode
    ```

    Exit and SSH again to see if it works.

    ![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-6.png)

- SSH into the workernode 1 using `ssh worker1` and do the same here as well:

    ```bash
    sudo hostnamectl set-hostname worker-1
    ```

    Now, exit and ssh again to see if it works.

-  SSH into the workernode 2 using `ssh worker2`:

    ```bash
    sudo hostnamectl set-hostname worker-2
    ```

    Now, exit and ssh again to see if it works.

## Step 06: Check the Ray Status on the Head Node

To verify the status of your Ray cluster, first SSH into the head node of your Ray deployment. Use the following steps to check whether the cluster is operating as expected:

1. **SSH into the Head Node:**

   First, log into the head node using SSH.

   ```sh
   ssh headnode
   ```
2. **Virtual environment:**

    Activate the virtual environment for python

    ```sh
    source ray_env/bin/activate
    ```
2. **Check Ray Cluster Status:**

   After logging in, run the following command to check the status of the Ray cluster:

   ```sh
   ray status
   ```

   ![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-7.png)

   The output of this command will show the current status of the Ray cluster, including the details of the head node and any worker nodes connected to it. If everything is configured correctly, you will see both the head node and the worker nodes listed, and their statuses should indicate that they are running properly.

   > **Note:** It may take a few minutes for all nodes to connect and the cluster to become fully operational after deployment. Be patient while the system initializes.

## Step 07: Check the Ray Dashboard

The Ray dashboard provides a visual interface to monitor the cluster. To access the dashboard:

1. Open a web browser and navigate to the following URL:

   ```sh
   http://<headnode-public-ip>:8265
   ```

   Replace `<headnode-public-ip>` with the public IP address of your head node.


2. In the dashboard, you can see a graphical representation of the Ray cluster, including the head node and worker nodes. It will also display metrics such as resource utilization, node status, and any errors or logs from the cluster. This helps you monitor the health and performance of your deployment in real-time.

![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-9.png)

<!-- ---

## Step 08: Change File Ownership and Permissions

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

   This ensures the `ubuntu` user has the necessary permissions to manage Ray processes, which often store temporary files in this location.

   ![](https://github.com/Konami33/poridhi.io.intern/raw/main/MLOps%20Lab/Lab%2002/images/image-8.png) -->


## Conclusion

In this lab, we successfully leveraged Pulumi to automate the deployment of critical AWS infrastructure components and Ray Cluster Deployment, setting the stage for efficient and scalable machine learning operations. By automating the creation of VPCs, subnets, EC2 instances, security groups, and S3 buckets, we laid a robust foundation for deploying a distributed Ray cluster.