# Automated Deployment of K3S on AWS

This project aims to automate the deployment of a *lightweight Kubernetes distribution (k3s)* on AWS using `GitHub Actions` for orchestration, `Pulumi` for infrastructure as code (IaC), and `Ansible` for configuration management.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/k3s-deployment/images/k3s-deployment1.drawio.svg)

### Key Components

- **GitHub Actions**: Automates workflows triggered by events in GitHub repositories.
- **Pulumi**: Infrastructure as Code tool to provision AWS resources.
- **Ansible**: Configuration management tool for installing and configuring k3s on AWS EC2 instances.

### Prerequisites

Before proceeding, ensure you have the following:

- An AWS account with appropriate `IAM` permissions.
- `Pulumi` installed locally and authenticated with your Pulumi account and a `PULUMI access token`.
- GitHub repository set up to host your Pulumi project.
- Access to GitHub `Secrets` to securely store credentials and sensitive information.

## Project Structure
The project is organized into the following structure:

```sh
K3s-deployment-automation/
├── Infra/                    # Pulumi project directory
│   ├── __main__.py           # Pulumi Python script defining AWS resources
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.yaml
│   ├── requirements.txt
│   ├── venv/                 # Virtual environment for Python dependencies 
│   └── ...                   # Other Pulumi project files and configurations
├── .github/                  # GitHub Actions workflows directory
│   └── workflows/
│       ├── infra.yml          # GitHub Actions workflow file for deploying infra
│       ├── setup-git-runner.yml         # GitHub Actions workflow for setup git runner
│       └── k3s-deploy.yml    # GitHub Actions workflow for deploying K3s
│       
├── ansible/
│    ├── ansible.cfg           # ansible configuration file
|    ├── inventory/            # inventory direcory for hostnames
|    │   └── hosts.ini
|    ├── roles/                  
|    │   ├── common/
|    │   │   └── tasks/
|    │   │       └── main.yml
|    │   ├── k3s-master/
|    │   │   └── tasks/
|    │   │       └── main.yml
|    │   └── k3s-worker/
.    │       └── tasks/
.    │           └── main.yml
.    └── site.yml
.
.
...                            # Other project files and directories
```

## Deployment Process

The deployment process involves the following steps:
1. **GitHub Actions 1**: A GitHub Actions workflow will be triggered by a push event to the main branch of specific directory which will run the Pulumi script to provision the AWS resources.
2. **GitHub Action 2**: A second GitHub Actions workflow is triggered to install self-hosted Git runner and install Ansible in the Git-runner public instance making it the control node for Ansible automation.
5. **GitHUb Action 3**: This action will run the Ansible playbook which will install and configure k3s on the private EC2 instances.

![alt text](https://github.com/Konami33/k3s-deployment/raw/main/images/image-1.png)


## Step 01: Setup Pulumi Project

**1. Create a new directory for your Pulumi project:**

```bash
mkdir Infra
cd Infra
```
**2. Install python venv**

```sh
sudo apt-get update
sudo apt install
```
**3. Initialize a new Pulumi AWS Python project:**

```bash
pulumi new aws-python
```

**4. Define AWS Resources to be created using PULUMI**

Edit the Python scripts (`__main__.py`) in your PULUMI project:

```python
import os
import pulumi
import pulumi_aws as aws
import pulumi_aws.ec2 as ec2
from pulumi_aws.ec2 import SecurityGroupRuleArgs


# Configuration setup
config = pulumi.Config()
instance_type = 't2.micro'
ami = "ami-060e277c0d4cce553"


# Create a VPC
vpc = ec2.Vpc(
    'my-vpc',
    cidr_block='10.0.0.0/16',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        'Name': 'my-vpc',
    }
)

# Create subnets
public_subnet = ec2.Subnet('public-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.1.0/24',
    map_public_ip_on_launch=True,
    availability_zone='ap-southeast-1a',
    tags={
        'Name': 'public-subnet',
    }
)

private_subnet = ec2.Subnet('private-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.2.0/24',
    map_public_ip_on_launch=False,
    availability_zone='ap-southeast-1a',
    tags={
        'Name': 'private-subnet',
    }
)

# Internet Gateway
igw = ec2.InternetGateway('internet-gateway', vpc_id=vpc.id)

# Route Table for Public Subnet
public_route_table = ec2.RouteTable('public-route-table', 
    vpc_id=vpc.id,
    routes=[{
        'cidr_block': '0.0.0.0/0',
        'gateway_id': igw.id,
    }],
    tags={
        'Name': 'public-route-table',
    }
)

# Associate the public route table with the public subnet

public_route_table_association = ec2.RouteTableAssociation(
    'public-route-table-association',
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)

# Elastic IP for NAT Gateway
eip = ec2.Eip('nat-eip', vpc=True)

# NAT Gateway
nat_gateway = ec2.NatGateway(
    'nat-gateway',
    subnet_id=public_subnet.id,
    allocation_id=eip.id,
    tags={
        'Name': 'nat-gateway',
    }
)

# Route Table for Private Subnet 
private_route_table = ec2.RouteTable(
    'private-route-table', 
    vpc_id=vpc.id,
    routes=[{
        'cidr_block': '0.0.0.0/0',
        'nat_gateway_id': nat_gateway.id,
    }],
    tags={
        'Name': 'private-route-table',
    }
)

# Associate the private route table with the private subnet
private_route_table_association = ec2.RouteTableAssociation(
    'private-route-table-association',
    subnet_id=private_subnet.id,
    route_table_id=private_route_table.id
)

# Security Group for allowing SSH and k3s traffic
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
    tags={
        'Name': 'k3s-secgrp',
    }
)

# collect the public key from github workspace
public_key = os.getenv("PUBLIC_KEY")

# Create the EC2 KeyPair using the public key
key_pair = aws.ec2.KeyPair("my-key-pair",
    key_name="my-key-pair",
    public_key=public_key)

# EC2 instances
master_instance = ec2.Instance(
    'master-instance',
    instance_type=instance_type,
    ami=ami,
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    tags={
        'Name': 'Master Node',
    }
)

worker_instance_1 = ec2.Instance('worker-instance-1',
    instance_type=instance_type,
    ami=ami,
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    tags={
        'Name': 'Worker Node 1',
    }
)

worker_instance_2 = ec2.Instance('worker-instance-2',
    instance_type=instance_type,
    ami=ami,
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    tags={
        'Name': 'Worker Node 2',
    }
)

git_runner_instance = ec2.Instance('git-runner-instance',
    instance_type=instance_type,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name=key_pair.key_name,
    tags={
        'Name': 'Git Runner',
    }
)

# Output the instance IP addresses
pulumi.export('git_runner_public_ip', git_runner_instance.public_ip)
pulumi.export('master_private_ip', master_instance.private_ip)
pulumi.export('worker1_private_ip', worker_instance_1.private_ip)
pulumi.export('worker2_private_ip', worker_instance_2.private_ip)
```


## Step 02: Configure Github secrets

**1. Save secrets and AWS credentials as Github secrets**

- Go to your GitHub repository.
- Navigate to **Settings** > **Secrets and variables** > **Actions** > **New repository secret**.
- Add these secrets with these contents:

  - `AWS_ACCESS_KEY_ID`

  - `AWS_SECRET_ACCESS_KEY`

  - `PULUMI_ACCESS_TOKEN`

## Step 03: Configure GitHub Actions for Infrastructure Deployment

**1. Create GitHub Actions Workflow (`infra.yml`)**

This workflow will create the required AWS Infrastructure. It will create VPC, public-subnet, private-subnet, route-table with subent association, internet gateway, NAT gateway, security group, and Instances. 

```yaml
name: Deploy Infrastructure

on:
  push:
    branches:
      - main
    paths:
      - Infra/**

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
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
      
      - name: Set public key as github env
        run: echo "PUBLIC_KEY=${{ secrets.PUBLIC_KEY }}" >> $GITHUB_ENV

      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: pulumi login

      - name: Pulumi stack select
        run: pulumi stack select <YOUR_PULUMI_STACK_NAME> --cwd Infra

      - name: Pulumi refresh
        run: pulumi refresh --yes --cwd Infra

      - name: Pulumi up
        run: pulumi up --yes --cwd Infra
```

**2. Create the GitHub action workflow `setup-git-runner.yml`:**

This GitHub Actions workflow will run after the `Deploy Infrastructure` workflow completes. Its primary purpose is to configure a GitHub Runner on an EC2 instance, set up `Ansible` on that instance, and prepare the environment for deploying a k3s cluster using Ansible.

```yml
name: Setup GitHub Runner and Ansible

on:
  workflow_run:
    workflows: ["Deploy Infrastructure"]
    types:
      - completed

jobs:
  setup_runner:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-1
      
      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: pulumi login

      - name: Pulumi stack select
        run: pulumi stack select <YOUR_STACK_NAME> --cwd Infra

      - name: Pulumi refresh
        run: pulumi refresh --yes --cwd Infra
      
      - name: Save Pulumi outputs
        id: pulumi_outputs
        run: |
          GIT_RUNNER_IP=$(pulumi stack output git_runner_public_ip --cwd Infra)
          echo "GIT_RUNNER_IP=$GIT_RUNNER_IP" >> $GITHUB_ENV
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}

      - name: Set up SSH agent
        uses: webfactory/ssh-agent@v0.5.3
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: SSH into Runner EC2 and install Git Runner
        run: |
          ssh -o StrictHostKeyChecking=no ubuntu@${{ env.GIT_RUNNER_IP }} << 'EOF'
            if [ ! -d "actions-runner" ]; then
              mkdir actions-runner && cd actions-runner

              curl -o actions-runner-linux-x64-2.317.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.317.0/actions-runner-linux-x64-2.317.0.tar.gz

              echo "9e883d210df8c6028aff475475a457d380353f9d01877d51cc01a17b2a91161d  actions-runner-linux-x64-2.317.0.tar.gz" | shasum -a 256 -c

              tar xzf ./actions-runner-linux-x64-2.317.0.tar.gz

              ./config.sh --url https://github.com/<user_name>/<repo_name> --token <GIT_RUNNER_TOKEN> --name "Git-runner"

              sudo ./svc.sh install
              sudo ./svc.sh start
            else
              echo "actions-runner directory already exists. Skipping installation."
            fi
          EOF

      
      - name: SSH into Runner instance and install Ansible
        run: |
          ssh -o StrictHostKeyChecking=no ubuntu@${{ env.GIT_RUNNER_IP }} << 'EOF'
          sudo apt-get update -y
          sudo apt install software-properties-common -y
          sudo apt-add-repository --yes --update ppa:ansible/ansible
          sudo apt-get install -y ansible
          ansible --version
          EOF
```

**NOTE: Remember to Replace the `<>` values with your corresponding values.**

Now push it the Github repository to trigger these two workflow to create the AWS infra and setup Git-runner.

```sh
git add .
git commit -m "Infra create and config runner"
git push
```

## Step 04: Configure ansible

**1. Create a directory named `ansible`**

```sh
mkdir ansible && cd ansible
```
**2. Create the file structure with file contents according the folder structure shown at the beginning.**

### File Contents

- **Common/tasks/main.yml:**

```yml
---
- name: Update and upgrade apt packages
  apt:
    update_cache: yes
    upgrade: dist
    force_apt_get: yes

- name: Install dependencies
  apt:
    name: 
      - curl
      - wget
      - apt-transport-https
      - ca-certificates
    state: present
```

- **k3s-master/tasks/main.yml**

```yml
---
- name: Download and install k3s
  shell: |
    curl -sfL https://get.k3s.io | sh -

- name: Set file permission
  shell: |
    sudo chmod 644 /etc/rancher/k3s/k3s.yaml

- name: Get k3s token
  shell: "cat /var/lib/rancher/k3s/server/node-token"
  register: k3s_token
  changed_when: false

- name: Get master node IP
  shell: "hostname -I | awk '{print $1}'"
  register: master_ip
  changed_when: false
```

- **k3s-worker/tasks/main.yml**

```yml
---
- name: Join the k3s cluster
  shell: |
    curl -sfL https://get.k3s.io | K3S_URL=https://{{ hostvars['master-node']['master_ip'].stdout }}:6443 K3S_TOKEN={{ hostvars['master-node']['k3s_token'].stdout }} sh -
```

- **ansifile.cfg**

```sh
[defaults]
inventory = inventory/hosts.ini
remote_user = ubuntu
private_key_file = ~/.ssh/my-key-pair.pem
host_key_checking = False
```

- **site.yml**

```sh
---
- hosts: k3s_cluster
  become: true
  roles:
    - common

- hosts: master
  become: true
  roles:
    - k3s-master

- hosts: workers
  become: true
  roles:
    - k3s-worker
```

## Step 05: Github action to run the ansible playbook

This workflow will trigger the ansible script to run and ansible will do the deployment of k3s in the private instances.

```yml
---
name: K3s deployment using Ansible

on:
  push:
    branches:
      - main
    paths:
      - ansible/**

jobs:
  setup_runner:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-southeast-1
      
      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: pulumi login

      - name: Pulumi stack select
        run: pulumi stack select <YOUR_PULUMI_STACK> --cwd Infra

      - name: Pulumi refresh
        run: pulumi refresh --yes --cwd Infra
      
      - name: Save Pulumi outputs
        id: pulumi_outputs
        run: |
          GIT_RUNNER_IP=$(pulumi stack output git_runner_public_ip --cwd Infra)
          MASTER_NODE_IP=$(pulumi stack output master_private_ip --cwd Infra)
          WORKER_NODE1_IP=$(pulumi stack output worker1_private_ip --cwd Infra)
          WORKER_NODE2_IP=$(pulumi stack output worker2_private_ip --cwd Infra)
          echo "GIT_RUNNER_IP=$GIT_RUNNER_IP" >> $GITHUB_ENV
          echo "MASTER_NODE_IP=$MASTER_NODE_IP" >> $GITHUB_ENV
          echo "WORKER_NODE1_IP=$WORKER_NODE1_IP" >> $GITHUB_ENV
          echo "WORKER_NODE2_IP=$WORKER_NODE2_IP" >> $GITHUB_ENV
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}

      - name: Set up SSH agent
        uses: webfactory/ssh-agent@v0.5.3
        with:
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

      - name: Copy SSH Private Key to Public Instance Git-runner
        run: |
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > my-key-pair.pem
          chmod 600 my-key-pair.pem
          scp -o StrictHostKeyChecking=no my-key-pair.pem ubuntu@${{ env.GIT_RUNNER_IP }}:~/.ssh/
      
      - name: Copy Ansible directory to GitHub Runner
        run: |
          scp -o StrictHostKeyChecking=no -r $GITHUB_WORKSPACE/ansible ubuntu@${{ env.GIT_RUNNER_IP }}:/home/ubuntu/

      - name: SSH into GitHub Runner and Copy the host ips
        run: |
          ssh -o StrictHostKeyChecking=no ubuntu@${{ env.GIT_RUNNER_IP }} << 'EOF'

          # Update inventory file with dynamic IPs
          sed -i "s/^master-node ansible_host=.*/master-node ansible_host=${{ env.MASTER_NODE_IP }}/" /home/ubuntu/ansible/inventory/hosts.ini
          sed -i "s/^worker-node-1 ansible_host=.*/worker-node-1 ansible_host=${{ env.WORKER_NODE1_IP }}/" /home/ubuntu/ansible/inventory/hosts.ini
          sed -i "s/^worker-node-2 ansible_host=.*/worker-node-2 ansible_host=${{ env.WORKER_NODE2_IP }}/" /home/ubuntu/ansible/inventory/hosts.ini
          EOF

      - name: Run the Ansible playbook
        run: |
          ssh -o StrictHostKeyChecking=no ubuntu@${{ env.GIT_RUNNER_IP }} << 'EOF'
          cd ansible && ansible-playbook -i inventory/hosts.ini site.yml
          EOF
```

## Step 06: Push changes to the github repository

After creating the Ansible files locally, we have to push to the github repository which will trigger the GitHub action.

```sh
git add .
git commit -m "Run ansible to provision k3s"
git push
```
## Verification

**1. Check GitHub Actions logs**

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/k3s-deployment/images/actions.png)

**2. After successful completion of the workflows, we can SSH into the Git-runner instance**

- Open an Ubuntu terminal

- Convert the private key into a pem file.

- Run the following command to SSH into the Git-runner instance

  ```sh
  ssh -i ~/.ssh/my-key-pair.pem ubuntu@<git-runner-ip>
  ```
  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/k3s-deployment/images/Screenshot%202024-07-04%20061633.png)

- Now you are in the Git-runner instance
- You check if the ansible directory is copied successfully
  ```sh
  ls
  cd ansible
  ```  
  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/k3s-deployment/images/Screenshot%202024-07-05%20123554.png)

3. SSH into Master node instance

- In the Github action we copied the pem file to the Public instance in ~/.ssh directory. Using this pem file, we can ssh into Master node. Run this command

  ```sh
  ssh -i ~/.ssh/my-key-pair.pem ubuntu@<master-node-ip>
  ```
- Now you are in the Master node. Run this command to check if k3s is installed and working correctly

  ```sh
  kubectl get nodes
  ```
  here you can see the Master node and the worker node has been deployed successfully and in `ready` state

  ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/k3s-deployment/images/Screenshot%202024-07-05%20113714.png)

## Lets deploy a NGINX pod in the k3s cluster.

1. Create a file named `nginx-pod.yaml`

  ```yml
  apiVersion: v1
  kind: Pod
  metadata:
    name: nginx-pod
  spec:
    containers:
    - name: nginx
      image: nginx
      ports:
      - containerPort: 80
  ```

2. Apply the manifest file

  ```sh
  kubectl apply -f nginx-pod.yaml
  ```

3. Check that the pod is running and ready:

  ```sh
  kubectl get pods
  ```
4. Access Nginx Pod: Once the pod is running, you can access Nginx directly from within the pod:

  ```sh
  kubectl exec -it nginx-pod -- bash
  ```
5. Inside the pod, you can use tools like curl or wget to test Nginx:

  ```sh
  curl localhost
  ```

Here we can see our nginx pod is deployed in the k3s cluster and working  fine.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/k3s-deployment/images/Screenshot%202024-07-05%20114808.png)

---

### Conclusion

In summary, we have successfully automated the deployment of k3s on AWS using a combination of GitHub Actions, Pulumi, and Ansible. This approach leverages the strengths of each tool:

- **GitHub Actions**: Automates the CI/CD pipeline, ensuring that infrastructure and application deployments are consistent and repeatable.
- **Pulumi**: Manages the infrastructure as code, provisioning and configuring AWS resources seamlessly.
- **Ansible**: Handles the configuration management and application deployment, ensuring that the k3s cluster is set up and maintained correctly.

By integrating these tools, we have created a robust, automated deployment pipeline that simplifies the process of setting up and managing a k3s cluster on AWS.

