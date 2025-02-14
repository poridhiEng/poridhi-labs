# Database Replication using PostgreSQL

Database replication is the process of copying and synchronizing data across multiple database servers. This ensures that all copies of the database remain consistent, available, and up to date. Replication is widely used to improve data availability, disaster recovery, load balancing, and performance in distributed database systems.

In this lab, we will create a master-slave database replication setup using PostgreSQL on AWS. Here's an overview of the architecture:


## AWS Infrastructure

In this setup, we will design and deploy AWS Infrastructure to support Database Cluster. The cluster will

Consist of three public instances: 

- `master-0`
- `replica-0`
- `replica-1`


To enable connectivity and access we will create necessary route tables, internet gateway, subnets, security groups and configure the rules.

We will use **Pulumi python** to create and manage this AWS infrastructure.

## Setting up the AWS CLI and Pulumi

The AWS CLI is a command-line tool that allows you to interact with AWS services programmatically. It simplifies provisioning resources, such as EC2 instances and load balancers, which are required to host our database cluster and application server.

### Configure AWS CLI

```bash
aws configure
```

- `AWS Access Key ID:` Your access key to authenticate AWS API requests.
- `AWS Secret Access Key:` A secret key associated with your access key.
- `Default region:` The AWS region in which you want to provision your resources (ap-southeast-1).
- `Default output format:` You can choose the output format (JSON, text, table).

> Get your access key and secret access key from Poridhi's lab account by generating AWS credentials.


## Provisioning Compute Resources

In this step, we will provision the necessary AWS resources that will host our database cluster and application server.

**1. Create a Directory for Your Infrastructure**

Before starting, it’s best to create a dedicated directory for the infrastructure files:

```bash
mkdir db-cluster-aws
cd db-cluster-aws
```

**2. Install Python venv**

Set up a Python virtual environment (venv) to manage dependencies for Pulumi or other Python-based tools:

```bash
sudo apt update
sudo apt install python3.8-venv -y
```

This will set up a Python virtual environment which will be useful later when working with Pulumi.

**3. Initialize a New Pulumi Project**

Pulumi is an Infrastructure-as-Code (IaC) tool used to manage cloud infrastructure. In this tutorial, you'll use Pulumi python to provision the AWS resources required for Database Cluster.

Run the following command to initialize a new Pulumi project:

```bash
pulumi new aws-python
```

**4. Update the Pulumi program (__main__.py) to create the infrastructure  ** 

```python
import pulumi
import pulumi_aws as aws
import os

# Create a VPC
vpc = aws.ec2.Vpc(
    'db-cluster-vpc',
    cidr_block='10.0.0.0/16',
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={'Name': 'db-cluster-vpc'}
)

# Create a subnet
subnet = aws.ec2.Subnet(
    'db-cluster-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.1.0/24',
    map_public_ip_on_launch=True,
    tags={'Name': 'db-cluster-subnet'}
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway(
    'db-cluster-internet-gateway',
    vpc_id=vpc.id,
    tags={'Name': 'db-cluster-internet-gateway'}
)

# Create a Route Table
route_table = aws.ec2.RouteTable(
    'db-cluster-route-table',
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            gateway_id=internet_gateway.id,
        )
    ],
    tags={'Name': 'db-cluster-route-table'}
)

# Associate the route table with the subnet
route_table_association = aws.ec2.RouteTableAssociation(
    'db-cluster-route-table-association',
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Create a security group with egress and ingress rules
security_group = aws.ec2.SecurityGroup(
    'db-cluster-security-group',
    vpc_id=vpc.id,
    description="db-cluster security group",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1',  # -1 allows all protocols
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],  # Allow all outbound traffic
        )
    ],
    tags={'Name': 'db-cluster-security-group'}
)

# Create EC2 Instances for MasterDB
master_instances = []
for i in range(1):
    master = aws.ec2.Instance(
        f'master-{i}',
        instance_type='t2.small',
        ami='ami-01811d4912b4ccb26',  # Update with correct Ubuntu AMI ID
        subnet_id=subnet.id,
        key_name="db-cluster",
        vpc_security_group_ids=[security_group.id],
        associate_public_ip_address=True,
        private_ip=f'10.0.1.1{i}',
        tags={
            'Name': f'master-{i}'
        }
    )
    master_instances.append(master)

# Create EC2 Instances for Replicas
replica_instances = []
for i in range(2):
    replica = aws.ec2.Instance(
        f'replica-{i}',
        instance_type='t2.small',
        ami='ami-01811d4912b4ccb26',  # Update with correct Ubuntu AMI ID
        subnet_id=subnet.id,
        key_name="db-cluster",
        vpc_security_group_ids=[security_group.id],
        associate_public_ip_address=True,
        private_ip=f'10.0.1.2{i}',
        tags={'Name': f'replica-{i}'}
    )
    replica_instances.append(replica)

# Export Public and Private IPs of Controller and Worker Instances
master_public_ips = [master.public_ip for master in master_instances]
master_private_ips = [master.private_ip for master in master_instances]
replica_public_ips = [replica.public_ip for replica in replica_instances]
replica_private_ips = [replica.private_ip for replica in replica_instances]

pulumi.export('master_public_ips', master_public_ips)
pulumi.export('master_private_ips', master_private_ips)
pulumi.export('replica_public_ips', replica_public_ips)
pulumi.export('replica_private_ips', replica_private_ips)

# Export the VPC ID and Subnet ID for reference
pulumi.export('vpc_id', vpc.id)
pulumi.export('subnet_id', subnet.id)

# create config file
def create_config_file(ip_list):
    # Define the hostnames for each IP address
    hostnames = ['master-0', 'replica-0', 'replica-1']
    
    config_content = ""
    
    # Iterate over IP addresses and corresponding hostnames
    for hostname, ip in zip(hostnames, ip_list):
        config_content += f"Host {hostname}\n"
        config_content += f"    HostName {ip}\n"
        config_content += f"    User ubuntu\n"
        config_content += f"    IdentityFile ~/.ssh/db-cluster.id_rsa\n\n"
    
    # Write the content to the SSH config file
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

# Collect the IPs for all nodes
all_ips = [master.public_ip for master in master_instances] + [replica.public_ip for replica in replica_instances]

# Create the config file with the IPs once the instances are ready
pulumi.Output.all(*all_ips).apply(create_config_file)
```


**5. Create an AWS Key Pair**

Database Cluster nodes need to communicate securely. This key pair will be used to authenticate when accessing EC2 instances.

**Generate the Key Pair**

Use the following AWS CLI command to create a new SSH key pair named kubernetes:

```bash
cd ~/.ssh/
aws ec2 create-key-pair --key-name db-cluster --output text --query 'KeyMaterial' > db-cluster.id_rsa
chmod 400 db-cluster.id_rsa
```

This will save the private key as db-cluster.id_rsa in the `~/.ssh/` directory and restrict its permissions.

**6. Provision the Infrastructure**

Run the following command to provision the infrastructure:

```bash
pulumi up --yes
```

This will create the necessary resources and output the public and private IPs of the instances. This will also create a config file in `~/.ssh/config` file with the IPs of the instances.


## SSH into the Database Cluster

First, connect to the master DB and replicas. As we have created the config file in `~/.ssh/config` file, we can connect to the instances by running the following command:

```bash
ssh master-0
```

You will be connected to the master DB. You may change the hostname to `master-0` by running the following command:

```bash
sudo hostnamectl set-hostname master-0
```

In the same way, you can connect to the replicas by running the following command:

Connect to the first replica:

```bash
ssh replica-0
```

Connect to the second replica:

```bash
ssh replica-1
```

You may change the hostname to `replica-0` and `replica-1` by running the following command in each of the instances:

```bash
sudo hostnamectl set-hostname replica-0
sudo hostnamectl set-hostname replica-1
```

## Configure the Database Cluster

We will configure the database cluster on the master DB and replicas. This will include configuring the `postgresql.conf` file and `pg_hba.conf` file. 

### 1. Master Server Configuration (master-0)

**1.1 Configure postgresql.conf**

Edit the `postgresql.conf` file:

```bash
sudo vim /etc/postgresql/16/main/postgresql.conf
```

Add/modify these settings:

```bash
listen_addresses = '*'
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
wal_keep_size = 1GB
```

**1.2 Configure pg_hba.conf**

Edit the `pg_hba.conf` file:

```bash
sudo vim /etc/postgresql/16/main/pg_hba.conf
```

Add these lines at the end (using private IPs):

```bash
host    replication     replicator      10.0.2.20/32        md5
host    replication     replicator      10.0.2.21/32        md5
host    all            replicator      10.0.2.20/32        md5
host    all            replicator      10.0.2.21/32        md5
host    all             app_user       10.0.1.30/32      md5
```

These lines allow the master DB to connect to the replicas and the application server to connect to the master DB.

**1.3 Create Replication User**

Connect to the master DB and create a replication user.

```bash
sudo -u postgres psql

-- Drop user if exists (if needed)
DROP USER IF EXISTS replicator;

-- Create replication user with proper permissions
CREATE USER replicator WITH LOGIN REPLICATION PASSWORD 'db-cluster';

-- Verify the user was created
\du replicator

-- Exit psql
\q
```

> Note: We are using the password `db-cluster` for the replication user. You can change it to any other password.

**1.4 Restart PostgreSQL on Master**

As we have modified the `postgresql.conf` file and `pg_hba.conf` file, we need to restart the PostgreSQL service.

```bash
sudo systemctl restart postgresql

# Verify PostgreSQL is running
sudo systemctl status postgresql
```

## 2. Replica Servers Configuration

Now, we will configure the replicas. Run the following commands on both replicas. First check the network connectivity to the master DB.

```bash
nc -zv 10.0.1.10 5432
```

If the connection is successful, you can proceed with the following steps.

**2.1 Stop PostgreSQL on Replicas**

Stop the PostgreSQL service on both replicas.

```bash
sudo systemctl stop postgresql
sudo systemctl status postgresql  # Verify it's stopped
```

**2.2 Prepare Data Directory on Replicas**

Remove the entire directory and recreate it.

```bash
sudo rm -rf /var/lib/postgresql/16/main
sudo mkdir /var/lib/postgresql/16/main
sudo chown postgres:postgres /var/lib/postgresql/16/main
sudo chmod 700 /var/lib/postgresql/16/main
```

Verify directory is empty and has correct permissions.

```bash
sudo ls -la /var/lib/postgresql/16/main
```

**2.3 Configure postgresql.conf**

Edit the `postgresql.conf` file:

```bash
sudo vim /etc/postgresql/16/main/postgresql.conf
```

Add/modify these settings:

```bash
listen_addresses = '*'
port = 5432
```

**2.4 Configure pg_hba.conf**

Edit the `pg_hba.conf` file:

```bash
sudo vim /etc/postgresql/16/main/pg_hba.conf
```

Add these lines:

```bash
host    all             app_user         10.0.1.0/24         md5
host    all             app_user         10.0.2.0/24         md5
```

**2.5 Create Base Backup on Replicas**

Create a base backup on both replicas.

On replica-0:

```bash
sudo -u postgres pg_basebackup -h 10.0.1.10 -D /var/lib/postgresql/16/main \
    -U replicator -P -v -R -X stream -C -S replica0
```

On replica-1:

```bash
sudo -u postgres pg_basebackup -h 10.0.1.10 -D /var/lib/postgresql/16/main \
    -U replicator -P -v -R -X stream -C -S replica1
```

> When prompted for password, enter: your password or the password `db-cluster` if you have not changed it.

**2.6 Start PostgreSQL on Replicas**

Start the PostgreSQL service on both replicas.

```bash
sudo systemctl start postgresql
sudo systemctl status postgresql
```

## 3. Verify Replication Setup

### 3.1 Check Replica Status

Connect to the replicas and check the status of the replicas.

```bash
sudo -u postgres psql

-- Verify replica mode
SELECT pg_is_in_recovery();  -- Should return 't'

-- Check replication lag
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;

\q
```

### 3.2 Check Master Status

Connect to the master and check the status of the master.

```bash
sudo -u postgres psql

-- Check replication connections
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn 
FROM pg_stat_replication;

-- Check replication slots
SELECT slot_name, active FROM pg_replication_slots;

\q
```

### Test Replication

**1. Connect to the master and create a test database and table.**

```bash
sudo -u postgres psql

-- Create test database and table
CREATE DATABASE test_db;
\c test_db
CREATE TABLE replication_test (id serial primary key, data text);
INSERT INTO replication_test (data) VALUES ('test data');
```

This will create a test database and table on the master.


**2. Connect to the replicas and check the status of the replicas.**

```bash
sudo -u postgres psql

\c test_db
SELECT * FROM replication_test;
```


Here we can see that the data is replicated to the replicas.




