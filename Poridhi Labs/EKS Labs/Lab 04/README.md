# EKS with AWS Load Balancers: Classic Load Balancer

In this lab we will set up an Amazon EKS cluster with AWS Load Balancers (Classic & Network Load Balancers), deploy a Flask application, and test the deployment.

## **Table of Contents**
1. **Prerequisites**
2. **Create an EKS Cluster**
3. **Create NodeGroup Using `eksctl`**
4. **Update kubeconfig to connect to your cluster**
5. **Deploy a Flask Application on EKS**
6. **Expose the Flask Application Using AWS Load Balancers (Classic Load Balancer)**
7. **Test the Deployment**

## Overall Architecture

![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/eks-lb-6.drawio.svg)

---

## What is Classic Load Balancer(CLB)?

A Classic Load Balancer (CLB) is a type of load balancer provided by Amazon Web Services (AWS) that distributes incoming traffic across multiple instances of an application. CLB supports both Layer 4 (transport layer) and Layer 7 (application layer) routing. CLB can distribute traffic across instances in multiple Availability Zones. CLB can be associated with security groups to control incoming traffic.

### How CLB Works

- The client sends a request to the load balancer.
- The load balancer receives the request and checks the listener configuration to determine which target group to route the traffic to.
- The load balancer selects a healthy instance from the target group and routes the traffic to that instance.
- The instance processes the request and returns a response to the load balancer.
- The load balancer returns the response to the client.

## Prerequisites

**1. Install `eksctl` (if not already installed):**

- Download eksctl

  ```sh
  curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
  ```

- Move eksctl to `/usr/local/bin`

  ```sh
  sudo mv /tmp/eksctl /usr/local/bin
  ```

- Verify the Installation

  ```sh
  eksctl version
  ```
  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image.png)

**2. Install `kubectl` (if not already installed):**

- Download the kubectl Binary

  ```sh
  curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
  ```
- Make the Binary Executable and Move the kubectl binary to `/usr/local/bin`

  ```sh
  chmod +x kubectl
  sudo mv kubectl /usr/local/bin/
  ```

- Verify the Installation

  ```sh
  kubectl version --client
  ```
  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-1.png)

**3. Install `aws cli` (if not already installed):**

- Download the AWS CLI Installer

  ```bash
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  ```

- Unzip the Installer

  ```bash
  unzip awscliv2.zip
  ```

  If you don't have `unzip` installed, you can install it using your package manager:

  ```bash
  sudo apt-get install unzip   # For Debian/Ubuntu
  ```

- Run the Installer and Verify the Installation

  ```bash
  sudo ./aws/install
  aws --version
  ```
**4. Configure the AWS CLI**

- Configure AWS CLI. You will be prompted to enter your AWS Access Key ID, Secret Access Key, default region, and output format.

  ```sh
  aws configure
  ```

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-2.png)

# Step by step guide

## Step 01: Create an EKS Cluster

**1. Create an EKS Cluster Without a Node Group:**

Execute the following command to create an EKS cluster:

```bash
eksctl create cluster \
--name demo-cluster-1 \
--version 1.27 \
--region ap-southeast-1 \
--zones ap-southeast-1a,ap-southeast-1b \
--without-nodegroup
```

**Explanation:**

- **Name**: Specifies the name of your EKS cluster (`demo-cluster-1`).
- **Version**: Kubernetes version to use (`1.27`).
- **Region**: AWS region (`ap-southeast-1`).
- **Zones**: Availability zones to be used (`ap-southeast-1a`, `ap-southeast-1b`).
- **Without Node Group**: Creates the cluster without any associated node groups.

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-3.png)

**2. Monitor the Creation:**

- The command will initiate the creation of the necessary VPC components, such as subnets, route tables, and NAT gateways, along with the EKS control plane. It may take a few minutes `(8-10 minutes)` to complete.

- If the creation is successful, you will see messages indicating that the cluster has been successfully created.

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-4.png)

- Go to the AWS management console, check out the created resources

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-5.png)

- Go to `EKS > Clusters` and check the created cluster

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-6.png)



## Step 02: Create NodeGroup

After creating the EKS cluster, you can add a node group that will consist of EC2 instances acting as worker nodes. We will follow the following step in our lab.

**1. Use the command below to create NodeGroup**

```sh
eksctl create nodegroup \
    --cluster=demo-cluster-1 \
    --name=eks-node-group \
    --region=ap-southeast-1 \
    --node-type=t3.medium \
    --managed \
    --nodes=2 \
    --nodes-min=1 \
    --nodes-max=2 \
    --node-private-networking
```

### Command Breakdown:
1. **`eksctl create nodegroup`**: This creates a new node group (a collection of EC2 instances) within an existing EKS cluster(`demo-cluster-1`).

2. **`--name=eks-node-group`**: This sets the name of the node group (`eks-node-group`).

3. **`--region=ap-southeast-1`**: This specifies the AWS region (`ap-southeast-1`, Southeast Asia Pacific, Singapore) where both the EKS cluster and the node group will be created.

4. **`--node-type=t3.medium`**: This sets the instance type (`t3.medium`) for the EC2 instances that will be part of this node group.

5. **`--managed`**: This flag specifies that the node group is a "Managed Node Group." Managed node groups are automatically maintained by AWS;

6. **`--nodes=2`**: This specifies that the node group will be created with 2 EC2 instances (nodes) initially.

7. **`--nodes-min=1`**: This sets the minimum number of nodes to 1, meaning the node group will always maintain at least one running node, even if the cluster scales down.

8. **`--nodes-max=2`**: This sets the maximum number of nodes to 2, ensuring that the cluster cannot scale beyond 2 nodes automatically.

9. **`--node-private-networking`**: This ensures that the EC2 instances (nodes) in the node group will only have private IP addresses, meaning they will not be accessible directly from the internet. Instead, they will only communicate within the VPC using private IP addresses, which enhances security. If external communication is needed, it will occur through a `NAT` gateway or other networking solutions.

**Check the command status:**

![alt text](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-23.png)

**2. Wait for Completion**

It might take a few minutes for the Node Group to be fully created. You can monitor the progress in the EKS Console. The status of the Node Group will be updated to 'active' once it is fully created.

![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-10.png)


## Step 03: Update kubeconfig to connect to your cluster

Open terminal on your local machine and do the following:

- **Run the following command to update your kubeconfig file to connect to your cluster:**

  ```sh
  aws eks --region ap-southeast-1 update-kubeconfig --name demo-cluster-1
  ```
  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-16.png)

- **Confirm the connection:**

  ```sh
  kubectl get nodes
  ```
  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-17.png)

  You should see the worker nodes are in a "Ready" state.
  

## Step 04: Deploy a Flask Application on EKS

**1. Create a simple Flask application and save it as `app.py`:**

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World! This is a Flask application running on EKS."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

**2. Create a `Dockerfile` to containerize the Flask app:**

```Dockerfile
# Use the official Python image.
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install flask

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["python", "app.py", "--port=5001"]
```

**3. Create a `Makefile` to build, tag and push the docker image**

```Makefile
# Variables
DOCKER_USERNAME = <USERNAME>
IMAGE_NAME = flask-app
TAG = latest

# Build the Docker image
build:
  docker build -t $(IMAGE_NAME) .

# Tag the Docker image
tag:
  docker tag $(IMAGE_NAME):$(TAG) $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Push the Docker image to Docker Hub (or your preferred registry)
push:
  docker push $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

# Combined command to build, tag, and push the Docker image
all: build tag push

# Clean up local images (optional)
clean:
  docker rmi $(IMAGE_NAME):$(TAG) $(DOCKER_USERNAME)/$(IMAGE_NAME):$(TAG)

.PHONY: build tag push all clean
```
>**NOTE:** Make sure to login into `Dockerhub`

**4. Run the Makefile command**

```sh
make all
```

![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-12.png) 

**5. Create a kubernetes deployment YAML file (`flask-deployment.yaml`):**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: flask-app
  template:
    metadata:
      labels:
        app: flask-app
    spec:
      containers:
      - name: flask-container
        image: konami98/flask-app:latest
        ports:
        - containerPort: 5001
```

> **NOTE:** Update the *image* according to your docker image that you created earlier. You can also use this image as well.

**6. Deploy the application:**

```bash
kubectl apply -f flask-deployment.yaml
```
![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-14.png)

## Step 05: Expose the Flask Application Using AWS Load Balancers (Classic Load Balancer)

**1. Create a Service with Classic Load Balancer:**

- Create a service YAML file (`flask-service-classic.yaml`):
  ```yaml
  apiVersion: v1
  kind: Service
  metadata:
    name: flask-service-classic
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "classic"
  spec:
    type: LoadBalancer
    ports:
    - port: 80
      targetPort: 5001
    selector:
      app: flask-app
  ```

- Deploy the service:
  ```bash
  kubectl apply -f flask-service-classic.yaml
  ```

**2. Check the created AWS classic load-balancer service**

- Go to EC2 section and in the left bar search for `load balancers`. You will see the created load-balancer service.

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-15.png)

## Step 06: Test the Deployment

**1. Access the Flask Application:**
- Run the following command to get the external IP of the load balancer:

  ```sh
  kubectl get svc
  ```
  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-13.png)

- The `EXTERNAL-IP` field will show the `DNS name` of the Classic Load Balancer.

- Copy and Paste the URL into your web browser to access the Flask application.

  ```sh
  http://<EXTERNAL-IP>
  ```
- You should see the flask application.

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-9.png)

**2. Verify Load Balancer Functionality:**

Test the load balancing by refreshing the page multiple times. The request should be distributed across the Flask application replicas.

---

So, We have successfully created the EKS cluster and node group and deployed a Flask application on the EKS cluster and exposing it using Classic Load Balancer.