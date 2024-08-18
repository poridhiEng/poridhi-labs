# Deploy a FastAPI application on an EC2 instance using `systemd`

## Overview
This guide provides a comprehensive step-by-step process to deploy a simple `FastAPI` on an EC2 instance using `systemd` for service management. The process involves setting up the necessary `AWS infrastructure`, launching an EC2 instance, installing `fastapi, uvicorn` and configuring it to run as a `systemd` service. By the end of this tutorial, you will have a fully functional fastapi web server running on an EC2 instance within a properly configured VPC.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-7.png)

## Prerequisites

1. Log in to the live AWS environment using the lab account.
2. Ensure you are in the `Singapore (ap-southeast-1)` region.

## *Steps*

## Step 1: Setup and configure AWS(vpc, subnet, route-table, Internet-Gateway)

1. Create a vpc named, e.g., `my-vpc` with IPv4 CIDR block `10.0.0.0/16`
2. Create a public subnet named `public-subnet` with IPv4 CIDR block `10.0.1.0/24`
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image.png)
3. Create a route table named `rt-public` and associate it with the `public-subnet`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-1.png)

4. Create an internet gateway named `igw` and attach it to the vpc `(my-vpc)`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-2.png)

5. Edit routes of the router:
   - Public Route Table`(rt-public)`:
      - Add a route with destination `0.0.0.0/0` and target `igw`

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-3.png)

Here is the resource map:

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image.png)


## Step 2: Set Up Your EC2 Instance

1. **Launch an EC2 instance:**
   - Choose an appropriate Amazon Machine Image (AMI), such as `Ubuntu`.
   - Choose the vpc `my-vpc` that we have created earlier.
   - Ensure that the instance is in the `public-subnet`.
   - Choose an appropriate instance type, such as `t2.micro`
   - Choose or create an appropriate key pair.
   - Choose an appropriate security group, such as `fast-api-sg`

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-4.png)

2. **Connect to your EC2 instance:**
   - Use SSH to connect to your EC2 instance:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@your-public-ip
   ```
   - Or You can simply connect using AWS ec2 connect option.

## Step 3: Install necessary depenedencies and libraries for fastapi setup.
1. Update the system and install necessary dependencies and libraries.

   ```sh
   sudo apt update
   sudo apt install python3.12-venv
   ```
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-5.png)

3. **Create FastAPI Application**:
   - Create a directory for your FastAPI application:
   ```sh
   mkdir ~/myfastapi
   cd ~/myfastapi
   ```
   - Create virtual environment and activate it:
    
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install FastAPI and Uvicorn**:
   - Install `FastAPI` and `Uvicorn` using pip:
   ```sh
   pip3 install fastapi uvicorn
   ```
    
5. **Create a simple FastAPI application in a file named `main.py`**:
   ```python
   from fastapi import FastAPI

   app = FastAPI()

   @app.get("/")
   def read_root():
      return {"Hello": "World"}
   ```

6. **Create a Uvicorn Service File**:
   - Create a `systemd` service file to manage your FastAPI application. Open the file with `nano` or your preferred editor:
   ```sh
   sudo nano /etc/systemd/system/myfastapi.service
   ```
   - Add the following content to the file:
   ```ini
    [Unit]
    Description=Gunicorn instance for a simple Fast Api App
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/myfastapi
    ExecStart=/home/ubuntu/myfastapi/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
    Environment="PATH=/home/ubuntu/myfastapi/venv/bin"

    [Install]
    WantedBy=multi-user.target
    ```
    Adjust the `User` and `WorkingDirectory` paths according to your environment.

6. **Start and Enable the Service**:
   - Reload `systemd` to recognize the new service:
     ```sh
     sudo systemctl daemon-reload
     ```
   - Start the FastAPI service:
     ```sh
     sudo systemctl start myfastapi.service
     ```
   - Enable the service to start on boot:
     ```sh
     sudo systemctl enable myfastapi.service
     ```
   - Check status
      ```sh
      sudo systemctl status myfastapi.service
      ```
   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-9.png)

1. **Allow inbound traffic to port 5000:**
   - In the AWS Management Console, navigate to the EC2 dashboard.
   - Select "Security Groups" from the left-hand menu.
   - Find the security group associated with your EC2 instance.
   - Edit the inbound rules to allow traffic on port 5000 from your desired IP ranges (e.g., 0.0.0.0/0 for all IPs, though this is not recommended for `production`. But for now it is ok).

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-8.png)

### Step 6: Access Your Flask Application

   - Open your web browser and navigate to `http://<EC2_INSTANCE_PUBLIC_IP>:8000`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2010/images/image-6.png)

Your FastAPI application should now be running and accessible through the specified port.
So, we have deployed a simple FastAPI application on a AWS ec2 instance using systemd.