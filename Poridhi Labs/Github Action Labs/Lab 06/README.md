# Self Hosted Runner in k3s Cluster Running on AWS 

In this project, we set up infrastructure on AWS using Pulumi and configure a Kubernetes cluster (k3s) on AWS EC2 instances with Ansible. We then create a custom Docker image for a self-hosted GitHub Actions runner and deploy it in the Kubernetes cluster. Finally, we deploy an Nginx application as a test workload to validate the setup and ensure seamless CI/CD integration using GitHub Actions.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/diagram1.svg)


## What is Self-Hosted Runner?

A self-hosted GitHub Actions runner is a machine (virtual or physical) that you configure and manage yourself to run GitHub Actions workflows. Unlike GitHub-hosted runners, which are managed by GitHub and run on shared infrastructure, self-hosted runners give you greater control over the environment, resources, and dependencies used in your workflows.

## How Self-Hosted GitHub Action Runners Work?

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/Self-hosted.svg)

This diagram explains the workflow of a self-hosted runner in GitHub Actions. When a workflow is triggered, jobs are added to the **Job Queue**. The self-hosted runner, managed by the user, continuously polls the queue, retrieves jobs, and processes them.

The **Runner Listener** fetches the job, and the **Job Controller** breaks it into steps. The **Worker Process** then executes each step sequentially, such as running commands, executing scripts, or interacting with tools like Docker or Kubernetes. It ensures smooth execution, manages errors, and tracks the status of each step. Finally, the runner reports the job’s completion status (success or failure) back to GitHub, enabling a flexible and controlled workflow environment.

## **Why Kubernetes for Self-Hosted Runners?**

- **Scalability**: Automatically adjusts runner pods based on workload using Horizontal Pod Autoscaling (HPA), optimizing resource usage.
- **High Availability**: Restarts failed pods and distributes jobs across nodes to ensure uptime and prevent bottlenecks.
- **Resource Management**: Provides fine-grained control over CPU and memory, preventing resource overuse or underutilization.

## **Task Description**

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/diagram2.svg)

- Use pulumi to setup AWS network infrastructure (VPC, Subnets, Security groups, EC2) etc. 
- Setup k3s cluster in AWS instances using Ansible.
- Set up directories and initialize a GitHub repository for the project.  
- Build and push a custom GitHub runner Docker image to Docker Hub.  
- Create Kubernetes deployment files for the runner and configure secrets.  
- Deploy the GitHub runner in Kubernetes and verify pod status.  
- Write Kubernetes manifests for Nginx deployment and service.  
- Add a GitHub Actions workflow to automate Docker build and Kubernetes deployment.  
- Trigger the workflow and verify its successful execution.  
- Access the deployed Nginx application using the Kubernetes NodePort.  
- Confirm deployment by checking Kubernetes pods, deployments, and services. 

## Prerequisites

Before you begin, ensure you have the following:

- An AWS account with the required permissions.
- Docker installed on your system for building images.
- A GitHub account with a repository.
- A GitHub Personal Access Token (PAT) with the required permissions.
- Pulumi CLI installed on your system.
- Ansible installed on your system.


## Step 1: Create AWS Resources with Pulumi

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/b83239541dd39c17d025e506e159a24eb974bfb8/Poridhi%20Labs/Github%20Action%20Labs/Lab%2006/images/aws-infra.svg)

### Configure AWS CLI

1. Install and configure the AWS CLI with your credentials by running:
   ```bash
   aws configure
   ```
   Follow the prompts to input:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region
   - Output format (e.g., `json`)

2. Your access keys can be found on the lab description page where the credentials were generated.

### Set Up a Pulumi Project

#### Create and Initialise the Pulumi Project

1. Create a new directory for the Pulumi project:

   ```bash
   mkdir k3s-infra && cd k3s-infra
   pulumi new aws-javascript
   ```
   This sets up a basic Pulumi project. Follow the prompts to provide details like project name and description.

#### Create a Key Pair

2. Create an EC2 key pair to allow SSH access to the instances:
   ```bash
   aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem
   ```

3. Set file permissions for the key file:
   ```bash
   chmod 400 MyKeyPair.pem
   ```

#### Write Pulumi Code

Replace the contents of `index.js` with the following code:

```javascript
const pulumi = require("@pulumi/pulumi");
const aws = require("@pulumi/aws");

// Create a VPC
const vpc = new aws.ec2.Vpc("k3s-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: { Name: "k3s-vpc" },
});
exports.vpcId = vpc.id;

// Create a public subnet
const publicSubnet = new aws.ec2.Subnet("k3s-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "ap-southeast-1a",
    mapPublicIpOnLaunch: true,
    tags: { Name: "k3s-subnet" },
});
exports.publicSubnetId = publicSubnet.id;

// Internet Gateway
const internetGateway = new aws.ec2.InternetGateway("k3s-igw", {
    vpcId: vpc.id,
    tags: { Name: "k3s-igw" },
});
exports.igwId = internetGateway.id;

// Route Table
const publicRouteTable = new aws.ec2.RouteTable("k3s-rt", {
    vpcId: vpc.id,
    tags: { Name: "k3s-rt" },
});
exports.publicRouteTableId = publicRouteTable.id;

new aws.ec2.Route("igw-route", {
    routeTableId: publicRouteTable.id,
    destinationCidrBlock: "0.0.0.0/0",
    gatewayId: internetGateway.id,
});

new aws.ec2.RouteTableAssociation("rt-association", {
    subnetId: publicSubnet.id,
    routeTableId: publicRouteTable.id,
});

// Security Group
const k3sSecurityGroup = new aws.ec2.SecurityGroup("k3s-secgrp", {
    vpcId: vpc.id,
    description: "Allow SSH and K3s traffic",
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        // { protocol: "tcp", fromPort: 6443, toPort: 6443, cidrBlocks: ["0.0.0.0/0"] },
            // Allow Kubernetes API access
        {
            protocol: "tcp",
            fromPort: 6443,
            toPort: 6443,
            cidrBlocks: ["0.0.0.0/0"], // Replace with your trusted IP or CIDR block
            description: "Kubernetes API access",
        },
        // Allow Docker Daemon access (internal only)
        {
            protocol: "tcp",
            fromPort: 2375,
            toPort: 2375,
            cidrBlocks: ["0.0.0.0/0"], // Restrict to localhost (internal traffic only)
            description: "Docker daemon (non-secure)",
        },
        // Allow Node-to-Node communication for Kubernetes
        {
            protocol: "tcp",
            fromPort: 10250,
            toPort: 10250,
            cidrBlocks: ["0.0.0.0/0"], // Adjust to your cluster network
            description: "Kubelet API",
        },
        {
            protocol: "udp",
            fromPort: 8472,
            toPort: 8472,
            cidrBlocks: ["0.0.0.0/0"], // Adjust to your cluster network
            description: "Flannel VXLAN traffic",
        },
        // Allow NodePort services
        {
            protocol: "tcp",
            fromPort: 30000,
            toPort: 32767,
            cidrBlocks: ["0.0.0.0/0"], // Public or specific access as needed
            description: "NodePort services",
        },
        // Allow DNS resolution
        {
            protocol: "udp",
            fromPort: 53,
            toPort: 53,
            cidrBlocks: ["0.0.0.0/0"], // Adjust to your needs
            description: "DNS resolution",
        }, 
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
    tags: { Name: "k3s-secgrp" },
});
exports.k3sSecurityGroupId = k3sSecurityGroup.id;

// AMI and Instances
const amiId = "ami-01811d4912b4ccb26"; // Ubuntu 24.04 LTS
const createInstance = (name) => new aws.ec2.Instance(name, {
    instanceType: "t3.small",
    vpcSecurityGroupIds: [k3sSecurityGroup.id],
    ami: amiId,
    subnetId: publicSubnet.id,
    keyName: "MyKeyPair",
    associatePublicIpAddress: true,
    tags: { Name: name, Environment: "Development", Project: "K3sSetup" },
});

const masterNode = createInstance("k3s-master-node");
const workerNode1 = createInstance("k3s-worker-node-1");
const workerNode2 = createInstance("k3s-worker-node-2");

exports.masterNodeDetails = { id: masterNode.id, publicIp: masterNode.publicIp };
exports.workerNode1Details = { id: workerNode1.id, publicIp: workerNode1.publicIp };
exports.workerNode2Details = { id: workerNode2.id, publicIp: workerNode2.publicIp };
```

#### Deploy the Infrastructure
Run the following command to provision the EC2 instances:

```bash
pulumi up
```

## Step 2: Install K3S using Ansible

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/b83239541dd39c17d025e506e159a24eb974bfb8/Poridhi%20Labs/Github%20Action%20Labs/Lab%2006/images/ansible-to-infra.svg)

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/b83239541dd39c17d025e506e159a24eb974bfb8/Poridhi%20Labs/Github%20Action%20Labs/Lab%2006/images/Ansible-k3s.svg)

### Create Project Structure

This is the structure for ansible configurations we'll be creating:

```plaintext
ansible-k3s/
├── ansible.cfg
├── inventory
├── playbook.yml
├── roles/
    └── k3s/
        ├── tasks/
        │   ├── main.yml
        │   ├── master.yml
        │   └── worker.yml
        ├── vars/
            └── main.yml
```


Run the following commands to create the desired structure:

```bash 
# Create the main project directory
mkdir -p ansible-k3s/roles/k3s/tasks
mkdir -p ansible-k3s/roles/k3s/vars

# Create the necessary files
touch ansible-k3s/ansible.cfg
touch ansible-k3s/inventory
touch ansible-k3s/playbook.yml
touch ansible-k3s/roles/k3s/tasks/main.yml
touch ansible-k3s/roles/k3s/tasks/master.yml
touch ansible-k3s/roles/k3s/tasks/worker.yml
touch ansible-k3s/roles/k3s/vars/main.yml
```



### Install Ansible

Now navigate to the `ansible-k3s` directory. Then, install Ansible on your machine, run these commands:

```bash
sudo apt-get update -y
sudo apt install software-properties-common -y
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install -y ansible 
sudo ansible --version
```

### Configure Ansible

Populate the following files using the given configurations, playbook and role tasks.


#### `ansible.cfg`

```bash
[defaults]
inventory = inventory
roles_path = roles
deprecation_warnings = False
host_key_checking = False
```

#### `inventory`

```ini
[k3s-master]
master ansible_host=<public-ip-of-master> ansible_user=ubuntu ansible_ssh_private_key_file=../k3s-infra/MyKeyPair.pem

[k3s-workers]
worker1 ansible_host=<public-ip-of-worker-1> ansible_user=ubuntu ansible_ssh_private_key_file=../k3s-infra/MyKeyPair.pem
worker2 ansible_host=<public-ip-of-worker-2> ansible_user=ubuntu ansible_ssh_private_key_file=../k3s-infra/MyKeyPair.pem
```

#### `playbook.yml`

```yaml
- hosts: k3s-master
  roles:
    - role: k3s
      k3s_role: master

- hosts: k3s-workers
  roles:
    - role: k3s
      k3s_role: worker
```


#### `roles/k3s/tasks/main.yml`

```yaml
- name: Include tasks for K3s Master
  include_tasks: master.yml
  when: k3s_role == "master"

- name: Include tasks for K3s Worker
  include_tasks: worker.yml
  when: k3s_role == "worker"
```

#### `roles/k3s/tasks/master.yml`

```yaml
- name: Install K3s on Master
  shell: curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
  become: true

- name: Retrieve K3s Token
  shell: cat /var/lib/rancher/k3s/server/node-token
  become: true
  register: k3s_token

- name: Save K3s Token for Workers
  copy:
    content: "{{ k3s_token.stdout }}"
    dest: /tmp/k3s_token
  delegate_to: localhost
```

#### `roles/k3s/tasks/worker.yml`

```yaml
- name: Create local token directory
  file:
    path: "/tmp/k3s_token_workers"
    state: directory
    mode: '0755'
  delegate_to: localhost

- name: Read K3s Token
  command: cat /tmp/k3s_token
  register: k3s_token
  delegate_to: localhost

- name: Install K3s on Worker
  shell: |
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" K3S_URL="https://{{ hostvars[groups['k3s-master'][0]]['ansible_default_ipv4']['address'] }}:6443" K3S_TOKEN="{{ k3s_token.stdout }}" sh -
  become: true
```

#### `roles/k3s/vars/main.yml`

```bash
k3s_role: master
```

### **Run Playbook**

```bash
ansible-playbook playbook.yml
```

### **Check Installation**

SSH into instances using public IP of master node and run:

```bash
kubectl get nodes
```

## Step 3: Creating the Custom runner image

Now we will create a Dockerfile that defines the container image for the self-hosted runner, including all required dependencies and configurations.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/github-runner.svg)

### **Create Directory for github-runner:**

```bash
mkdir github-runner-k8s
cd github-runner-k8s
```

### **Create the necessary files:**

```bash
touch Dockerfile entrypoint.sh
```

Add the following content to the `Dockerfile`:

```dockerfile
FROM debian:bookworm-slim
ARG RUNNER_VERSION="2.302.1"
ENV GITHUB_PERSONAL_TOKEN ""
ENV GITHUB_OWNER ""
ENV GITHUB_REPOSITORY ""

# Install Docker
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
RUN echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update

# Install required packages
RUN apt-get install -y docker-ce-cli sudo jq

# Setup github user
RUN useradd -m github && \
    usermod -aG sudo github && \
    echo "%sudo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create directories with correct permissions
RUN mkdir -p /actions-runner && \
    chown -R github:github /actions-runner && \
    mkdir -p /work && \
    chown -R github:github /work

USER github
WORKDIR /actions-runner

# Download and install runner
RUN curl -Ls https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -o actions-runner.tar.gz && \
    tar xzf actions-runner.tar.gz && \
    rm actions-runner.tar.gz && \
    sudo ./bin/installdependencies.sh

COPY --chown=github:github entrypoint.sh /actions-runner/entrypoint.sh
RUN sudo chmod u+x /actions-runner/entrypoint.sh

ENTRYPOINT ["/actions-runner/entrypoint.sh"]
```

## Step 4: Entrypoint Script

The `entrypoint.sh` script handles runner registration, execution, and cleanup. Add the following content to the `entrypoint.sh` file:

```sh
#!/bin/sh
registration_url="https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPOSITORY}/actions/runners/registration-token"
echo "Requesting registration URL at '${registration_url}'"
payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PERSONAL_TOKEN}" ${registration_url})
export RUNNER_TOKEN=$(echo $payload | jq .token --raw-output)

./config.sh \
    --name $(hostname) \
    --token ${RUNNER_TOKEN} \
    --labels my-runner \
    --url https://github.com/${GITHUB_OWNER}/${GITHUB_REPOSITORY} \
    --work "/work" \
    --unattended \
    --replace

remove() {
    ./config.sh remove --unattended --token "${RUNNER_TOKEN}"
}

trap 'remove; exit 130' INT
trap 'remove; exit 143' TERM

./run.sh "$*" &
wait $!
```

### Make the script executable:

```sh
chmod +x entrypoint.sh
```

## Step 5: Build the docker image

To build the Docker image with the specified environment variables set in the Dockerfile, We need to create the `Github` personal access token (`PAT`).

### **Generate the Personal Access Token (PAT)**

#### **Log in to GitHub**:
   - Go to [GitHub](https://github.com) and log in to your account.

#### **Navigate to Developer Settings**:
   - Click on your profile picture in the top-right corner.
   - Go to **Settings** → **Developer Settings** (located near the bottom of the left sidebar).

#### **Generate a New Token**:
   - Click on **Personal access tokens** → **Tokens (classic)**.
   - Select **Generate new token (classic)**.

     ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/1.png)

#### **Set Permissions**:
   - Provide a meaningful **note** (e.g., `Self-Hosted Runner`).
   - Select **Expiration** (set a reasonable expiry based on your needs).
   - Under **Scopes**, select the following permissions:
     - `repo` (Full control of private repositories).
     - `admin:repo_hook` (Manage webhooks and services).
     - `workflow` (Update GitHub Actions workflows).

     ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/2.png)

#### **Generate and Save**:
   - Click **Generate token**.
   - Copy the generated token **immediately** (it won't be shown again, make sure to copy it in `notepad`).

#### **Docker Build Command**:

```bash
docker build \
  --build-arg RUNNER_VERSION="2.302.1" \
  --build-arg GITHUB_PERSONAL_TOKEN="<your-personal-access-token" \
  --build-arg GITHUB_OWNER="<your-github-username>" \
  --build-arg GITHUB_REPOSITORY="<your-github-repository-name" \
  -t <image-name> .
```

> NOTE: Make sure to replace all the environment variables with your credentials in docker build command.

## Step 6: Push the Image to DockerHub

### **Login to Docker**

```bash
docker login
```
- Enter your DockerHub **username** and **password** when prompted.
- If you're using an access token instead of a password (recommended for security), enter the token in place of the password.

### **Tag the Docker Image**

```bash
docker tag <image-name>:latest <dockerhub-username>/<image-name>:latest
```

### **Push the Image to DockerHub**

```bash
docker push <dockerhub-username>/<image-name>:latest
```
> NOTE: Replace `<dockerhub-username>`and `<image-name>` with your DockerHub username and with your image name.

### **Verify the Image on DockerHub**
- Log in to your DockerHub account at [DockerHub](https://hub.docker.com/).
- Navigate to the **Repositories** section.
- Ensure the `<your-image-name>` is listed under your account with the `latest` tag.


## Step 6: Configure the self hosted runner in k3s Cluster in `AWS`

### Get the `Public IP` of the `Master Node`:

Login to the AWS console and navigate to the EC2 dashboard. Copy the `Public IP` of the `Master Node` instance.

![](./images/1.jpg)

### SSH into the `Master Node`:

Navigate to the directory where the `MyKeyPair.pem` file ( `k3s-infra/` ) is located and run the following command to SSH into the `Master Node`:

```bash
ssh -i MyKeyPair.pem ubuntu@<public-ip-of-master>
```

### Create a Directory for the Runner Configuration in Kubernetes:

```bash
mkdir github-runner
cd github-runner
```

### **Create a Kubernetes namespace:**

```bash
kubectl create namespace host-runner
```

### **Create secrets (replace placeholder values):**

```bash
kubectl -n host-runner create secret generic github-secret \
  --from-literal=GITHUB_OWNER=<your-github-username> \
  --from-literal=GITHUB_REPOSITORY=<your-repo-name> \
  --from-literal=GITHUB_PERSONAL_TOKEN=<your-github-personal-access-token>
```

### **Create a `github-runner.yaml` with the following content:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: github-runner
  labels:
    app: github-runner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: github-runner
  template:
    metadata:
      labels:
        app: github-runner
    spec:
      containers:
      - name: github-runner
        imagePullPolicy: IfNotPresent
        image: <dockerhub-username>/<image-name>:latest
        env:
        - name: GITHUB_OWNER
          valueFrom:
            secretKeyRef:
              name: github-secret
              key: GITHUB_OWNER
        - name: GITHUB_REPOSITORY
          valueFrom:
            secretKeyRef:
              name: github-secret
              key: GITHUB_REPOSITORY
        - name: GITHUB_PERSONAL_TOKEN
          valueFrom:
            secretKeyRef:
              name: github-secret
              key: GITHUB_PERSONAL_TOKEN
        - name: DOCKER_HOST
          value: tcp://localhost:2375
        volumeMounts:
        - name: data
          mountPath: /work/
      - name: dind
        image: docker:24.0.6-dind
        env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
        resources:
          requests:
            cpu: 20m
            memory: 512Mi
        securityContext:
          privileged: true
        volumeMounts:
        - name: docker-graph-storage
          mountPath: /var/lib/docker
        - name: data
          mountPath: /work/
      volumes:
      - name: docker-graph-storage
        emptyDir: {}
      - name: data
        emptyDir: {}

```
> NOTE: Replace `<dockerhub-username>`and `<image-name>` with your DockerHub username and with your image name.

## Step 7: Deploying to Kubernetes

### **Apply the Kubernetes deployment:**

```bash
kubectl apply -f github-runner.yaml -n host-runner
```

### **Verify the deployment:**

```yaml
kubectl get pods -n host-runner
```

You should see the GitHub runner pod running successfully.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/10.png)

If the pod is not running, go to `github > settings > actions > Runners` self-hosted runners will be listed there. You can see the runner status there. Currently, it will be in `idle` state.

![](./images/2.jpg)

**Check runner logs**

```yaml
kubectl  logs <pod-name> -n host-runner
```

## Step 8: Testing the Runner with Nginx Deployment


### **Create a new repository:**

- Go to [GitHub](https://github.com) and create a new repository ( e.g., `github-runner-k8s` ) with a `README.md` file.


### Setup github in AWS `Master Node`:

SSH into the `Master Node` and run the following commands:

```bash
git remote set-url origin https://<your-github-username>:<your-token>@github.com/<your-github-username>/<repository>.git
```

> NOTE: Replace `<your-github-username>`, `<your-token>`, and `<repository>` with your GitHub username, token, and repository name.

```bash
git config user.email "<your-email>"
git config user.name "<Your Name>"
```

Replace `<your-email>` and `<your-name>` with your github email address and username.

### **Clone the repository:**

```bash 
git clone <github-repository>
```


### **Create Directory for github-runner:**

```bash
cd <github-repo>
mkdir -p nginx-deployment
cd nginx-deployment
```
> NOTE: Replace `<github-repo>` with your repository name.

### **Create the necessary files:**

```bash
touch namespace.yml deployment.yml service.yml
```

### **Kubernetes Manifest Files**

1. **Namespace Manifest**   
   Defines a namespace to isolate resources within the Kubernetes cluster.

   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
      name: ${NAMESPACE}
   ```

2. **Deployment Manifest**  
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: nginx-deployment
      namespace: ${NAMESPACE}
    spec:
      replicas: ${REPLICAS}
      selector:
        matchLabels:
          app: nginx
      template:
        metadata:
          labels:
            app: nginx
        spec:
          containers:
          - name: nginx
            image: ${DOCKER_REGISTRY}/${DOCKER_IMAGE}:${IMAGE_TAG}
            ports:
            - containerPort: 80 
    ```

3. **Service Manifest**  
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: nginx-service
      namespace: ${NAMESPACE}
    spec:
      type: NodePort
      selector:
        app: nginx
      ports:
        - port: 80
          targetPort: 80
          nodePort: ${NODE_PORT}
    ```

### **Dockerfile and Static Content**

Create a `Dockerfile.nginx` and an `index.html` file in the root (`github repository`) directory.

```bash
touch Dockerfile.nginx index.html
```

Add the following content in  `Dockerfile.nginx`:

```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
```

Add the following content in `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <h1>Hello from self-hosted runner!</h1>
</body>
</html>
```

### **GitHub Actions Workflow**

Create a `.github/workflows/deploy.yml` file in the root directory of the repository.

```bash
mkdir .github
cd .github
mkdir workflows
cd workflows
touch deploy.yml
```

Add the following content in`.github/workflows/deploy.yml`  to automate the process using a self-hosted runner.

```yaml
name: Self-Hosted Runner Test v2
on:
  push:
    branches:
      - main
env:
  DOCKER_REGISTRY: ${{ secrets.DOCKER_REGISTRY }}
  DOCKER_IMAGE: nginx-app
  NAMESPACE: dev
  REPLICAS: "2"
  NODE_PORT: "30080"
jobs:
  docker-build:
    runs-on: self-hosted
    steps:
      - name: repository checkout 
        uses: actions/checkout@v4
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: Dockerfile.nginx
          push: true
          tags: ${{ env.DOCKER_REGISTRY }}/${{ env.DOCKER_IMAGE }}:${{ github.sha }}
  k8s-deploy:
    needs: docker-build
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: Install kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'
    
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
      - name: Update Kubernetes Manifests
        run: |
          for file in nginx-deployment/*.yml; do
            sed -i "s|\${DOCKER_REGISTRY}|$DOCKER_REGISTRY|g" $file
            sed -i "s|\${DOCKER_IMAGE}|$DOCKER_IMAGE|g" $file
            sed -i "s|\${IMAGE_TAG}|${{ github.sha }}|g" $file
            sed -i "s|\${NAMESPACE}|$NAMESPACE|g" $file
            sed -i "s|\${REPLICAS}|$REPLICAS|g" $file
            sed -i "s|\${NODE_PORT}|$NODE_PORT|g" $file
          done
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f nginx-deployment/namespace.yml
          kubectl apply -f nginx-deployment/deployment.yml
          kubectl apply -f nginx-deployment/service.yml
```

### **Add GitHub Repository Secrets**
Ensure the following secrets are added to your GitHub repository for secure handling:

- **DOCKER_REGISTRY**: Docker registry name (e.g., Docker Hub username).  
- **DOCKER_USERNAME**: Docker Hub username.  
- **DOCKER_PASSWORD**: Docker Hub password.  
- **KUBE_CONFIG**: Kubernetes configuration file.  

### **Kubernetes Configuration File**

To get the `KUBE_CONFIG` file, you can use the following command:

```bash
cat /etc/rancher/k3s/k3s.yaml
```

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/5.png)

Copy the contents of the file and replace the `server ip` with kubernetes `master node ip`.

To get the master node ip, you can use the following command:

```bash
kubectl get nodes -o wide
```
![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/6.png)

and add it as a secret in your GitHub repository as `KUBE_CONFIG`.

### **Commit and Push to Repository**
After creating the required files and configuration, commit and push all files to the main branch of your repository.


## Step 9: **Verify the Workflow**
Monitor the **Actions** tab in your GitHub repository to ensure the workflow runs successfully. The workflow will:  
1. Build and push the Docker image.

   ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/3.png)

2. Update Kubernetes manifests dynamically. 

3. Deploy the application to the Kubernetes cluster.

    ![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/4.png)

## Access the Application

```bash
kubectl get namespaces
```
For successful deployment, you should see the `dev` namespace.

```bash
kubectl get deployments -n dev
```
For successful deployment, you should see the `nginx-deployment`.

```bash
kubectl get services -n dev
```
For successful deployment, you should see the `nginx-service` with a `NodePort` service.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/6675e03153be6538a11f09778dc2ebea53803fcb/Poridhi%20Labs/Github%20Action%20Labs/Lab%2005/images/7.png)

Now you can access the application with public ip of the master node and the nodeport of the service.


## Conclusion
In this lab, we successfully set up a self-hosted GitHub Actions runner in a Kubernetes cluster on AWS. We created a custom Docker image for the runner, deployed it in the Kubernetes cluster, and verified its status. We also automated the deployment of an Nginx application using GitHub Actions, ensuring seamless CI/CD integration and efficient workflow management. This setup provides greater control over the environment, resources, and dependencies used in GitHub Actions workflows, enabling a flexible and controlled workflow environment for CI/CD pipelines.

