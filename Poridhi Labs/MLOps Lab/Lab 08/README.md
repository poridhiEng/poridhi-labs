
## Step 1: Infra Setup

1. Configure AWS CLI:
    ```
    aws configure
    ```

2. Setup pulumi project:
    ```
    mkdir mlops-lab-test
    cd mlops-lab-test
    ```

    ```
    sudo apt update
    sudo apt install python3.8-venv
    ```

    ```
    pulumi new aws-python
    ```

3. Create Key pair:
    ```
    aws ec2 create-key-pair --key-name key-pair-poridhi-poc --query 'KeyMaterial' --output text > key-pair-poridhi-poc.pem
    ```

    ```
    chmod 400 key-pair-poridhi-poc.pem
    ```

4. Python code for infra Setup: 

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
    instance_type='t2.micro',
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


5. pulumi up:

```bash
pulumi up
```


6. SSH into EC2 instance:

```bash
ssh -i "key-pair-poridhi-poc.pem" ubuntu@<public-IP>
```






### Step 2: Install and Configure PostgreSQL

#### Update the system and install PostgreSQL:

```bash
sudo apt update -y
sudo apt install -y postgresql postgresql-contrib libpq-dev
```

#### Initialize and start PostgreSQL:

On Ubuntu, PostgreSQL is automatically initialized, so you only need to start and enable the service:

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Configure PostgreSQL for MLflow:

Switch to the PostgreSQL user and access the PostgreSQL shell:

```bash
sudo -u postgres psql
```

#### In the PostgreSQL prompt, run the following commands:

```sql
CREATE DATABASE mlflow;
CREATE USER mlflow WITH ENCRYPTED PASSWORD 'mlflow';
GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow;
\q
```

#### Edit PostgreSQL configuration to allow external connections:

Open the `postgresql.conf` file:

```bash
sudo nano /etc/postgresql/16/main/postgresql.conf
```

Uncomment and modify the line for `listen_addresses` to allow connections from all IPs:

```bash
listen_addresses = '*'
```

#### Edit the `pg_hba.conf` file to allow external connections:

Open the `pg_hba.conf` file:

```bash
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

Add the following line at the end of the file to allow connections from any IP using password authentication:

```bash
host    all             all             0.0.0.0/0               md5
```

#### Restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```