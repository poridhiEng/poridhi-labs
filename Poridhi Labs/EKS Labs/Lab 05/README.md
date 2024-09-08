# EKS with AWS Load Balancers: Network Load Balancer

In this lab, we will set up an Amazon EKS (Elastic Kubernetes Service) cluster and expose a Flask application using a Network Load Balancer (NLB). This exercise will demonstrate how to deploy a containerized Flask application to EKS and make it accessible through an NLB, which is ideal for handling high-volume TCP traffic with minimal latency.

## **Table of Contents**
1. **Create an EKS Cluster**
2. **Create a Node Group Using the AWS Console**
3. **Deploy an Apache HTTP Server on EKS**
4. **Expose the Apache Server Using AWS Load Balancers**
5. **Test the Deployment**

## Overall Architecture

![](https://raw.githubusercontent.com/Minhaz00/AWS-EKS-Labs/c40c2685db78b814e27c766b695ae358a5a97313/EKS%20Labs/Lab%2005/images/nlb.svg)

The Network Load Balancer (NLB) distributes TCP/UDP traffic across multiple targets, such as Apache servers in an EKS cluster, ensuring high availability and low latency. It operates at Layer 4, providing static IP addresses, automatic scaling, and health checks to route traffic only to healthy instances. Ideal for high-performance applications needing fixed IPs and secure private connectivity, the NLB helps maintain consistent traffic distribution and scalability.

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

## Step 01: Create an EKS Cluster Without a Node Group

1. **Create an EKS Cluster Without a Node Group:**

   Execute the following command to create an EKS cluster:

   ```bash
   eksctl create cluster \
   --name demo-cluster-1 \
   --version 1.27 \
   --region ap-southeast-1 \
   --zones ap-southeast-1a,ap-southeast-1b \
   --without-nodegroup
   ```

   - **Name**: Specifies the name of your EKS cluster (`demo-cluster-1`).
   - **Version**: Kubernetes version to use (`1.27`).
   - **Region**: AWS region (`ap-southeast-1`).
   - **Zones**: Availability zones to be used (`ap-southeast-1a`, `ap-southeast-1b`).
   - **Without Node Group**: Creates the cluster without any associated node groups.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-3.png)

2. **Monitor the Creation:**

   - The command will initiate the creation of the necessary VPC components, such as subnets, route tables, and NAT gateways, along with the EKS control plane. It may take a few minutes `(8-10 minutes)` to complete.
   - If the creation is successful, you will see messages indicating that the cluster has been successfully created.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-4.png)

   - Go to the AWS management console, check out the created resources

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-5.png)

   - Go to `EKS > Clusters` and check the created cluster

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-6.png)

## Step 02: Create a Node Group Using the AWS Console

1. **Navigate to the Amazon EKS Console:**

   - Open the Amazon EKS Console and select your cluster (`demo-cluster-1`).

2. **Add a Node Group:**

   - In the menu, click on **compute** and then **Add Node Group**.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-7.png)

3. **Configure the Node Group:**

   - **Name**: Give your node group a name (e.g., `my-nodegroup`).
   - **Node IAM role**: Create an IAM role with:

      - `AmazonEKSWorkerNodePolicy`
      - `AmazonEC2ContainerRegistryReadOnly`
      - `AmazonEKS_CNI_Policy`
      - `AmazonSSMManagedInstanceCore`
    
      attached.

    ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-18.png)

   - **Subnets**: Choose the subnets created by `eksctl`. Here, we will create the node group in the private subnet. Hence, select only the private subnets.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-19.png)

   - **AMI type:** `Amazon Linux 2(al2_x86_64)`

   - **Instance type**: Choose an instance type (e.g., `t3.medium`) according to your need.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-20.png)

   - **Scaling configuration:** Set the desired, minimum, and maximum number of nodes.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-21.png)

4. **Launch the Node Group:**
   - Click **Create** to launch the node group. This will start the creation of the EC2 instances that will act as worker nodes for your EKS cluster.

5. **Wait for Node Group Creation:**
   - Once created, the node group will automatically join the cluster. You can verify this by checking the Nodes section in the EKS Console

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-10.png)

## Step 03: Update kubeconfig to Connect to Your Cluster

Open a terminal on your local machine and do the following:

- Run the following command to update your kubeconfig file to connect to your cluster:

  ```sh
  aws eks --region ap-southeast-1 update-kubeconfig --name demo-cluster-1
  ```

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-16.png)

- Confirm the connection:

  ```sh
  kubectl get nodes
  ```

  ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-17.png)

  You should see the worker nodes in a "Ready" state.

## Step 04: Deploy an Apache HTTP Server on EKS

1. **Create a Dockerfile to Containerize the Apache HTTP Server:**

    ```Dockerfile
    # Use the official Apache HTTP server image from the Docker Hub
    FROM httpd:2.4

    # Copy a custom index.html file to the Apache server directory
    COPY ./index.html /usr/local/apache2/htdocs/
    ```

2. **Create a `index.html` file with some sample content:**

    ```html
    <!DOCTYPE html>
    <html>
    <head>
        <title>Apache HTTP Server</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
        <p>This is a simple Apache HTTP server running on EKS.</p>
    </body>
    </html>
    ```

3. Create a `Makefile` to build, tag and push the docker image

    ```Makefile
    # Variables
    DOCKER_USERNAME = <USERNAME>
    IMAGE_NAME = apache-server
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

    **NOTE:** Make sure to login into `Dockerhub`

4. Run the Makefile command

    ```sh
    make all
    ```

    ![](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2005/images/2.png?raw=true)

4. **Create a Kubernetes Deployment YAML File `apache-deployment.yaml`:**

    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: apache-deployment
    spec:
      replicas: 2
      selector:
        matchLabels:
          app: apache-server
      template:
        metadata:
          labels:
            app: apache-server
        spec:
          containers:
          - name: apache-container
            image: <image-name>:latest
            ports:
            - containerPort: 80
    ```

5. **Apply the Deployment:**

    ```sh
    kubectl apply -f apache-deployment.yaml
    ```

6. **Verify the Deployment:**

    ```sh
    kubectl get deployments
    kubectl get pods
    ```

## Step 05: Expose the Apache Server Using a Network Load Balancer

1. **Create a Kubernetes Service YAML File `apache-service-nlb.yaml`:**

    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: apache-service
      annotations:
        service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
    spec:
      selector:
        app: apache-server
      ports:
        - protocol: TCP
          port: 80
          targetPort: 80
      type: LoadBalancer
    ```

2. **Apply the Service Configuration:**

    ```sh
    kubectl apply -f apache-service-nlb.yaml
    ```

3. **Verify the Service:**

    ```sh
    kubectl get services
    ```

   ![](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2005/images/3.png?raw=true)

## Step 06: Test the Deployment

1. **Access the Apache HTTP Server:**

   Open a web browser and navigate to:

   ```
   http://<external-ip-or-dns-name>
   ```

   ![](https://github.com/Minhaz00/AWS-EKS-Labs/blob/main/EKS%20Labs/Lab%2005/images/4.png?raw=true)

2. **Clean Up**

   After completing the lab, clean up your resources:

   ```sh
   eksctl delete cluster --name demo-cluster-1 --region ap-southeast-1
   ```