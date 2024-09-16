# Documentation for Creating AWS Infrastructure with GitHub Actions and SSH Access

This documentation outlines the steps to create AWS infrastructure using GitHub Actions, generate SSH keys, set up GitHub secrets, create workflows, and establish SSH connections.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-5/images/image-2.png)

## 1. Generate SSH Keys Locally

Generate a new SSH key pair on your local machine. This key pair will be used to SSH into the EC2 instances.

```sh
ssh-keygen -t rsa -b 2048
```

This will generate two files, typically in the `~/.ssh` directory:
- `id_rsa` (private key)
- `id_rsa.pub` (public key)

## 2. Go to the SSH Folder

Navigate to the `.ssh` directory where the keys were generated.

```sh
cd ~/.ssh
```

## 3. Get the Public Key and Add It to GitHub Secrets

1. Open the `id_rsa.pub` file and copy its contents.
   
   ```sh
   cat id_rsa.pub
   ```

2. Go to your GitHub repository.
3. Navigate to **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
4. Add a new secret named `PUBLIC_KEY` and paste the contents of your `id_rsa.pub` file.

## 4: Set Up a Pulumi Project

### 1. **Set Up a Pulumi Project**:
   - Create a new directory for your project and navigate into it:
     ```sh
     mkdir vpc-project
     cd vpc-project
     ```

### 2. **Initialize a New Pulumi Project**:

- Install Python venv

    ```sh
    sudo apt update
    sudo apt install python3.8-venv
    ```
- Run the following command to create a new Pulumi project:
     ```sh
     pulumi new aws-python
     ```
    Follow the prompts to set up your project. It will create the necessary folders for pulumi setup. 

### 3. Update the `__main__.py` file according to this:

```python
import pulumi
import pulumi_aws as aws
import os

# Read the public key from the environment (set by GitHub Actions)
public_key = os.getenv("PUBLIC_KEY")

# Create the EC2 KeyPair using the public key
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair",
    public_key=public_key)

# Define the VPC and subnet configurations
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
)

# Create Public Subnet
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True,
    availability_zone="ap-southeast-1a",
)

# Create Internet Gateway
igw = aws.ec2.InternetGateway("igw",
    vpc_id=vpc.id,
)

# Create Route Table
route_table = aws.ec2.RouteTable("route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id,
    }],
)

# Associate Route Table with Public Subnet
rt_assoc_public = aws.ec2.RouteTableAssociation("rt-assoc-public",
    subnet_id=public_subnet.id,
    route_table_id=route_table.id,
)

# Create Security Group
security_group = aws.ec2.SecurityGroup("web-secgrp",
    description='Enable SSH and K3s access',
    vpc_id=vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
    }],
)

# Create instances in the VPC and subnet
ami_id = "ami-008c09a18ce321b3c"  # Replace with a valid AMI ID for your region
instance_type = "t3.small"

master_node = aws.ec2.Instance("master-node",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "master-node"
    })

worker_node_1 = aws.ec2.Instance("worker-node-1",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "worker-node-1"
    })

worker_node_2 = aws.ec2.Instance("worker-node-2",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "worker-node-2"
    })


# Create Nginx instance
nginx_instance = aws.ec2.Instance("nginx-instance",
    instance_type=instance_type,
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name=key_pair.key_name,
    vpc_security_group_ids=[security_group.id],
    tags={
        "Name": "nginx-instance"
    })



# Export outputs
pulumi.export("master_public_ip", master_node.public_ip)
pulumi.export("worker1_public_ip", worker_node_1.public_ip)
pulumi.export("worker2_public_ip", worker_node_2.public_ip)
pulumi.export("nginx_instance", nginx_instance.public_ip)
```

## 5. Create GitHub Actions Workflow

Create a GitHub Actions workflow in this directory `.github/workflows/deploy.yml` of your project.

```yaml
name: Deploy Infrastructure

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install pulumi pulumi-aws

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-1

      # login
      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: pulumi login

      # select stack
      - name: Pulumi stack select
        run: pulumi stack select dev

      - name: Set public key environment variable
        run: echo "PUBLIC_KEY=${{ secrets.PUBLIC_KEY }}" >> $GITHUB_ENV

      # refresh
      - name: Pulumi refresh
        run: pulumi refresh --yes

      # up
      - name: Pulumi up
        run: pulumi up --yes

      # save outputs
      - name: Save Pulumi outputs
        id: pulumi_outputs
        run: |
          MASTER_IP=$(pulumi stack output master_public_ip)
          WORKER1_IP=$(pulumi stack output worker1_public_ip)
          WORKER2_IP=$(pulumi stack output worker2_public_ip)
          NGINX_IP=$(pulumi stack output nginx_instance)

          echo "MASTER_IP=$MASTER_IP" >> $GITHUB_ENV
          echo "WORKER1_IP=$WORKER1_IP" >> $GITHUB_ENV
          echo "WORKER2_IP=$WORKER2_IP" >> $GITHUB_ENV
          echo "NGINX_IP=$NGINX_IP" >> $GITHUB_ENV

        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}


      - name: Debug Environment Variables
        run: |
          echo "MASTER_IP=${{ env.MASTER_IP }}"
          echo "WORKER1_IP=${{ env.WORKER1_IP }}"
          echo "WORKER2_IP=${{ env.WORKER2_IP }}"
          echo "NGINX_IP=${{ env.NGINX_IP }}"
```

## 6. Push to GitHub

Commit your changes and push them to your GitHub repository.

```sh
git add .
git commit -m "Add Pulumi infrastructure and workflow"
git push origin main
```

## 7. Copy the Private Key for SSH Access

After the infrastructure is deployed, copy the private key to a file named `my-key-pair.pem`.

```sh
cp ./id_rsa ./my-key-pair.pem
```

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-5/images/image-11.png)

### 8. SSH Using `my-key-pair.pem`

To SSH into your EC2 instance, use the private key `my-key-pair.pem`.

```sh
ssh -i my-key-pair.pem ec2-user@<instance-public-ip>
```

Replace `<instance-public-ip>` with the public IP address of your EC2 instance.


![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-5/images/image-1.png)

### Summary

By following these steps, you have:
1. Generated SSH keys locally.
2. Navigated to the SSH folder and obtained the public key.
3. Added the public key as a GitHub secret.
4. Created the `__main__.py` file to define the AWS infrastructure.
5. Created a GitHub Actions workflow to deploy the infrastructure.
6. Pushed the changes to GitHub.
7. Copied the private key for SSH access.
8. Established an SSH connection using the private key.

This setup ensures a smooth and automated process for deploying and managing your AWS infrastructure with GitHub Actions.