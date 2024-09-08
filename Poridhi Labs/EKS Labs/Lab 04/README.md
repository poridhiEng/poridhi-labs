# EKS with AWS Load Balancers: Classic Load Balancer

In this lab we will set up an Amazon EKS cluster with AWS Load Balancers (Classic & Network Load Balancers), deploy a Flask application, and test the deployment.

## **Table of Contents**
1. **Create an EKS Cluster**
2. **Create a Node Group Using the AWS Console**
3. **Deploy a Flask Application on EKS**
4. **Expose the Flask Application Using AWS Load Balancers**
5. **Test the Deployment**

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

   - In the menu, click on the **compute** and then **Add Node Group**.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-7.png)

3. **Configure the Node Group:**

   - **Name**: Give your node group a name (e.g., `my-nodegroup`).
   - **Node IAM role**: Create an IAM role with these policies:

      - `AmazonEKSWorkerNodePolicy`
      - `AmazonEC2ContainerRegistryReadOnly`
      - `AmazonEKS_CNI_Policy`
      - `AmazonSSMManagedInstanceCore`

    ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-18.png)

   - **Subnets**: Choose the subnets created by `eksctl`. Here, we will create the nodegroup in the private subnet. Thats why we have to select only the private subnets.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-19.png)

   - **AMI type:** `Amazon Linux 2(al2_x86_64)`

   - **Instance type**: Choose an instance type (e.g., `t3.medium`). according to your need.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-20.png)

   - **Scaling configuration:** Set the desired, minimum, and maximum number of nodes.

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-21.png)

4. **Launch the Node Group:**
   - Click **Create** to launch the node group. This will start the creation of the EC2 instances that will act as worker nodes for your EKS cluster.

5. **Wait for Node Group Creation:**
   - Once created, the node group will automatically join the cluster. You can verify this by checking the Nodes section in the EKS Console

   ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-10.png)


## Step 04: Update kubeconfig to connect to your cluster

Open terminal on your local machine and do the following:

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
  

## Step 03: Deploy a Flask Application on EKS

1. Create a simple Flask application and save it as `app.py`:

    ```python
    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def hello():
        return "Hello, World! This is a Flask application running on EKS."

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5001)
    ```

2. Create a `Dockerfile` to containerize the Flask app:

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

3. Create a `Makefile` to build, tag and push the docker image

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

    **NOTE:** Make sure to login into `Dockerhub`

4. Run the Makefile command

    ```sh
    make all
    ```

    ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-12.png) 

5. Create a kubernetes deployment YAML file (`flask-deployment.yaml`):
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

    **NOTE:** Update the *image* according to your docker image that you created earlier. You can also use this image as well.

6. Deploy the application:

    ```bash
    kubectl apply -f flask-deployment.yaml
    ```
    ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-14.png)

## Step 04: Expose the Flask Application Using AWS Load Balancers (Classic Load Balancer)

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

## Step 05: Test the Deployment

1. **Access the Flask Application:**
    - Run the following command to get the external IP of the load balancer:

      ```sh
      kubectl get svc
      ```
      ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-13.png)

    - The EXTERNAL-IP field will show the DNS name of the Classic Load Balancer.

   - Copy and Paste the URL into your web browser to access the Flask application.

      ```sh
      http://a535c28b241a042849b91065c6a53545-64277239.ap-southeast-1.elb.amazonaws.com/
      ```
   - You should see the flask application.

      ![](https://github.com/Konami33/AWS-EKS-Labs/raw/main/EKS%20Labs/Lab%2004/images/image-9.png)

2. **Verify Load Balancer Functionality:**
   - Test the load balancing by refreshing the page multiple times. The request should be distributed across the Flask application replicas.

---

So, We have successfully created the EKS cluster and node group and deployed a Flask application on the EKS cluster and exposing it using Classic Load Balancer.