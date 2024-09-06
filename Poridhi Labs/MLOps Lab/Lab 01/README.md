# Ray Cluster Deployment In AWS 

Welcome to this  lab where we will deep dive into infrastructure deployment using Pulumi, an open-source infrastructure as code project. We will not just stop there but also manually deploy Ray clusters. Ray is a high-performance distributed execution framework targeted at large-scale machine learning and reinforcement learning applications.

By the end of this lab, you will have hands-on experience with Pulumi, Ray clusters.

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image.png?raw=true)


### What is Ray?

Ray is an open-source unified framework for distributed computing, and scaling AI and Python applications like machine learning. It provides the compute layer for parallel processing so that you don’t need to be a distributed systems expert. Ray minimizes the complexity of running your distributed individual and end-to-end machine learning workflows with these components:

- Scalable libraries for common machine learning tasks such as data preprocessing, distributed training, hyperparameter tuning, reinforcement learning, and model serving.
- Pythonic distributed computing primitives for parallelizing and scaling Python applications.
- Integrations and utilities for integrating and deploying a Ray cluster with existing tools and infrastructure such as Kubernetes, AWS, GCP, and Azure.

Ray works by **creating a cluster of nodes** and **scheduling tasks** across them. It uses ***dynamic task*** ***scheduling***, ***a shared memory object store*** for efficient data sharing, supports the actor model for stateful computations, and has native support for Python and Java. It's a powerful tool for distributed computing, providing efficient task scheduling, data sharing, and support for stateful computations.

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-8.png?raw=true)

In this lab, we’ll create a ray cluster with 3 nodes, 

1. One Head Node,
2. Two Worker Nodes, 

Supported by the compute and networking infrastructure of AWS.



## Infrastructure Needed to set up Ray Cluster on AWS

Having the right network configurations and setup in AWS for Ray clusters is crucial for efficient distributed computing.  The compute setup, including the choice of EC2 instances and their configurations, directly impacts the performance and cost-effectiveness of the Ray cluster. 

Moreover, we need robust and dynamic storage support to ingest dataset, store the transformed and computed feature data to a feature store, store the model training and output data.

### Compute Instances Configurations

1. **EC2 Instances**: AWS EC2 instances are used to host the Ray nodes. The instance type (e.g., t3.medium) determines the hardware of the host computer.
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

**Creating these components manually on AWS console are very time-consuming and gruesome tasks.** And, in the context of ML engineering, it’s very necessary to build up your infrastructure fast and focus on the ML tasks. So, we'll be using pulumi. 


## Task Description

In this hands-on lab we will learn how to setup the required infrastructur (VPC, EC2 instances, S3 buckets) for our upcoming MLOps Labs using pulumi. We will also learn how to install the Ray clusters in our EC2 instance. 

We will create config file to SSH into our ray nodes. This file allows you to define shortcuts and advanced SSH options, making the SSH process smoother and more efficient.

We will config hostname for our EC2 instances so that we can easily identify them in our environment.

At last, we will set up ray cluster in our EC2 instance.

> Note: This lab is intended to be done in poridhi VS Code. So we will skip the aws cli installation, pulumi installation, and python installation steps as we these are already installed in the VS code environment.

## Step 1. AWS CLI Configuration

Run the following command to configure AWS CLI:

```bash
aws configure
```
![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-1.png?raw=true)


This command prompts you for your AWS Access Key ID, Secret Access Key, region, and output format.


##  Step 2: Set Up a Pulumi Project

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

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-2.png?raw=true)

### Create Key Pair

Create a new key pair for our instances using the following command:

```sh
aws ec2 create-key-pair --key-name key-pair-poridhi-poc --query 'KeyMaterial' --output text > key-pair-poridhi-poc.pem
```

These commands will create key pair for our instances.

### Set File Permissions of the key files
```sh
chmod 400 key-pair-poridhi-poc.pem
```

### Write Code for infrastructure creation

#### Create a VPC

1. We start by creating a VPC using `aws.ec2.Vpc()`. The VPC has a CIDR block of `10.0.0.0/16`, providing up to 65,536 private IPv4 addresses. DNS support and DNS hostnames are enabled by setting `enable_dns_support=True` and `enable_dns_hostnames=True`. This is essential for our Ray cluster to operate in a secure, isolated network environment.
2. The VPC ID is stored in the `vpc.id` variable.

#### Create an Internet Gateway

1. Next, an Internet Gateway is created using `aws.ec2.InternetGateway()`.
2. This Internet Gateway is attached to the VPC using the `vpc_id` parameter.
3. **Why we need an Internet Gateway (IGW):** It connects the VPC to the internet, enabling Ray nodes to communicate with the outside world, such as downloading dependencies.

#### Create a Public Subnet

1. A public subnet is created using `aws.ec2.Subnet()` within the VPC.
2. The subnet has a CIDR block of `10.0.1.0/24` and is configured to map public IP addresses on launch by setting `map_public_ip_on_launch=True`.
3. **Why a Subnet is Needed:** It provides a segmented IP address range within the VPC where isolated resources, like Ray nodes, can be placed.

#### Create a Route Table

1. A route table is created using `aws.ec2.RouteTable()` and associated with the VPC.
2. A route is added to this table, directing all traffic (`0.0.0.0/0`) to the Internet Gateway created earlier.
3. **Importance for Ray:** This setup ensures proper routing of traffic between Ray nodes and external networks.

#### Associate the Subnet with the Route Table

1. The public subnet is associated with the route table using `aws.ec2.RouteTableAssociation()`.
2. The `subnet_id` and `route_table_id` parameters link the subnet and the route table, ensuring that traffic within the subnet follows the correct routing rules.

#### Create a Security Group

1. A security group is created using `aws.ec2.SecurityGroup()` and is associated with the VPC.
2. The security group is configured with inbound rules to allow traffic on specific ports necessary for Ray:
    - **Port 22:** SSH access to remotely manage the nodes.
    - **Ports 80 and 443:** HTTP and HTTPS traffic for downloading dependencies or data.
    - **Port 6379:** Redis, used by Ray as its primary data store.
    - **Port 8265:** Ray dashboard access.
    - **Ports 1024-65535:** Ephemeral ports required for inter-node communication and various monitoring tools.
3. An outbound rule is added, allowing all traffic (`0.0.0.0/0`) to exit the VPC.

#### Create the Head Node

1. The head node (EC2 instance) is created using `aws.ec2.Instance()` with the following configurations:
    - Instance type: `t3.medium`
    - AMI: `ami-01811d4912b4ccb26` (replace with the correct AMI ID)
    - Security group: the one created earlier
    - Subnet: the public subnet created earlier
    - Key pair: `key-pair-poridhi-poc` (replace with your key pair name)
    - EBS block device: a 20 GB GP3 volume

#### Create the Worker Nodes

1. Two worker nodes (EC2 instances) are created using a loop and `aws.ec2.Instance()` with configurations similar to the head node:
    - Instance type: `t3.small`
    - AMI: `ami-01811d4912b4ccb26` (replace with the correct AMI ID)
    - Security group: the one created earlier
    - Subnet: the public subnet created earlier
    - Key pair: `key-pair-poridhi-poc` (replace with your key pair name)
    - EBS block device: a 20 GB GP3 volume

#### Create S3 Buckets

1. The code creates four S3 buckets, each with a unique name and versioning enabled. These buckets will serve as storage for staging raw datasets, feature stores, model training data, and model outputs.

#### Export Outputs

1. The private IP addresses of the head node and worker nodes are exported as Pulumi outputs, along with the names of the S3 buckets.


Now, **Open `__main__.py` file in your project directory**:

```python
import pulumi
import pulumi_aws as aws

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

# Security Group allowing SSH, HTTP, and necessary ports for Ray
security_group = aws.ec2.SecurityGroup("micro-sec-group",
    vpc_id=vpc.id,
    description="Allow SSH, HTTP, and necessary ports for Ray",
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
            protocol="tcp",
            from_port=6379,
            to_port=6379,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=8265,
            to_port=8265,
            cidr_blocks=["0.0.0.0/0"],
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

# User data to install Python 3.9
instances_user_data = """#!/bin/bash
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev
"""

# Create the head node
head_node = aws.ec2.Instance('head-node',
    instance_type='t3.medium',
    ami='ami-01811d4912b4ccb26',  # Replace with the correct AMI ID
    vpc_security_group_ids=[security_group.id],
    subnet_id=subnet.id,
    user_data=instances_user_data,
    key_name='key-pair-poridhi-poc',  # Replace with your key pair name
    ebs_block_devices=[
        aws.ec2.InstanceEbsBlockDeviceArgs(
            device_name="/dev/sda1",
            volume_type="gp3",
            volume_size=20,  # Size in GB
            delete_on_termination=True,
        ),
    ],
    tags={
        'Name': 'head-node',
    }
)

# Create worker nodes
worker_nodes = []

for i in range(2):
    worker_node = aws.ec2.Instance(f'worker-node-{i+1}',
        instance_type='t3.small',
        ami='ami-01811d4912b4ccb26',  # Replace with the correct AMI ID
        vpc_security_group_ids=[security_group.id],
        subnet_id=subnet.id,
        user_data=instances_user_data,
        key_name='key-pair-poridhi-poc',  # Replace with your key pair name
        ebs_block_devices=[
            aws.ec2.InstanceEbsBlockDeviceArgs(
                device_name="/dev/sda1",
                volume_type="gp3",
                volume_size=20,  # Size in GB
                delete_on_termination=True,
            ),
        ],
        tags={
            'Name': f'worker-node-{i+1}',
        }
    )
    worker_nodes.append(worker_node)

# Output the private IP addresses
pulumi.export('head_node_private_ip', head_node.private_ip)
for i, worker_node in enumerate(worker_nodes):
    pulumi.export(f'worker_node_{i}_private_ip', worker_node.private_ip)


# Create specific S3 buckets with unique names
staging_data_store_bucket = aws.s3.Bucket("stagingdatastorebucket-unique-name",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

feature_store_bucket = aws.s3.Bucket("featurestorebucket-unique-name",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

model_store_bucket = aws.s3.Bucket("modelstorebucket-unique-name",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

results_store_bucket = aws.s3.Bucket("resultsstorebucket-unique-name",
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

This Pulumi code creates a VPC, an Internet Gateway, a public subnet, a route table, a security group, a head node, and worker nodes for a Ray cluster. 


### Preview the deployment plan

To preview the deployment plan, run the following command:

```bash
pulumi preview
```

This will show all the components ready to be deployed and provisioned.

### Deploy the Pulumi Stack

Deploy the stack using the following command:

```sh
pulumi up
```
Review the changes and confirm by typing "yes".

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-3.png?raw=true)



### Verify the Deployment

You can varify the creteated resources such as VPC, Subnet, EC2 instance using AWS console.

- **EC2 Instaces:**

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-4.png?raw=true)

- **S3 buckets:**

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-5.png?raw=true)

## Step 3: SSH simplification using SSH Config File

We can solve the issues of using the long command with instance-ip and key-pair every time we want to ssh into our instance by configuring the `~/.ssh/config` file. This file allows you to define shortcuts and advanced SSH options, making the SSH process smoother and more efficient. 

Create a `config` file in the `~/.ssh/` directory and open it using `vim`.

```bash
cd ~/.ssh
vim config
```

Edit the `config` file as follows for our instaces:

```bash
Host headnode
    HostName <headnode-intance-public-ip>
    User ubuntu
    IdentityFile <path-to-the-instances-key-pair>

Host worker1
    HostName <workernode1-intance-public-ip>
    User ubuntu
    IdentityFile <path-to-the-instances-key-pair>

Host worker2
    HostName <workernode2-intance-public-ip>
    User ubuntu
    IdentityFile <path-to-the-instances-key-pair>
```

The configuration defines SSH shortcuts for easy access to three EC2 instances: `headnode`, `worker1`, and `worker2`. For each instance, it specifies the public IP address, the user (ubuntu), and the SSH key file. This setup allows you to connect to any of these instances with a simple command like `ssh headnode`, without needing to manually enter connection details each time.


The `config` file will look something like this in our case:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-6.png?raw=true)


Now save and exit the vim editor and try to SSH into the head-node and worker-node instances using the following commands from 3 different terminal:

```bash
ssh headnode
ssh worker1
ssh worker2
```

Using these commands we can easily SSH into the desided instance without mentioning the IP or DNS names of the instances as well as the key-pair.

## Step 4: Set the hostname of the instances

We can set the hostname for our instances by using the `hostnamectl` command. This will help us to easily identify at which instance we are now after we ssh into any instance.


- SSH into the headenode instance and use the following command:

    ```bash
    sudo hostnamectl set-hostname headnode
    ```

    Exit and SSH again to see if it works.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-7.png?raw=true)

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



## Step 5: Setting up The Ray Cluster in EC2 instance

We have set up the AWS components needed to set up the Ray cluster with IaaC but the installation of Ray and its dependencies will be installed manually to contextualize better. Eventually, the head node and the worker nodes of the Ray cluster would be added manually.

### Connect to our instances

Open 3 different terminals for our 3 instances. SSH into them using the following command:

- For head node:

    ```bash
    ssh headnode
    ```

- For worker node 1:

    ```bash
    ssh worker1
    ```

- For head node 2:

    ```bash
    ssh worker2
    ```
### Set up the Python Virtual Environment

Use the following command to create a virtual environment inside `each` instances:

```bash
python3.9 -m venv ray_env
```
    
Activate the vertual environment:

```bash
source ray_env/bin/activate
```
    
    
### Install Ray with pip

Use the following command to update the pip and install Ray with pip inside `each` of the instance.
    
```bash
pip install --upgrade pip
pip install "ray[default] @ https://s3-us-west-2.amazonaws.com/ray-wheels/latest/ray-3.0.0.dev0-cp39-cp39-manylinux2014_x86_64.whl"
```
    

### Start the ray cluster inside the Head node 
    
Use the following command to start the ray cluster inside the head node:
        
```bash
ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --include-dashboard=True
```

Expected output:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-12.png?raw=true)


### Start the ray cluster inside each worker nodes

Use the following command to connect the worker nodes to the head node and start ray:

```bash
ray start --address='<head-node-instance-private-ip>:6379'
```

Replace `<head-node-instance-private-ip>` with the actual private IP address of the instance working as head node.

- Inside worker 1:
    
    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-9.png?raw=true)   

- Inside worker 2:

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-10.png?raw=true)     

### check the status of the Ray cluster
To check the status of the Ray cluster, run the following command inside head node:

```bash
ray status
```

Expected output:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/MLOps%20Lab/Lab%2001/images/image-11.png?raw=true)

This ensures that the status of the Ray cluster is correct and that the Ray cluster is running properly.






## Conclusion

In this lab, we successfully leveraged Pulumi to automate the deployment of critical AWS infrastructure components, setting the stage for efficient and scalable machine learning operations. By automating the creation of VPCs, subnets, EC2 instances, security groups, and S3 buckets, we laid a robust foundation for deploying a distributed Ray cluster. This hands-on experience not only simplifies the infrastructure setup but also empowers you to focus on building and scaling your machine learning applications with Ray. As you continue to explore and integrate these tools, you'll find that combining infrastructure-as-code with powerful distributed computing frameworks like Ray can greatly enhance the agility and effectiveness of your machine learning workflows.