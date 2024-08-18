# Deploy a simple Flask app in EC2 using systemd

## Overview
This guide provides a comprehensive step-by-step process to deploy a simple `Flask application` on an EC2 instance using `systemd` for service management. The process involves setting up the necessary AWS infrastructure, launching an EC2 instance, installing Flask, and configuring it to run as a `systemd` service. By the end of this tutorial, you will have a fully functional Flask web server running on an EC2 instance within a properly configured VPC.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-4.png)

## Prerequisites

1. Log in to the live AWS environment using the lab account.
2. Ensure you are in the `Singapore (ap-southeast-1)` region.

## *Steps*

## Step 1: Setup and configure AWS(vpc, subnet, route-table, Internet-Gateway)

1. Create a vpc named, e.g., `my-vpc` with IPv4 CIDR block `10.0.0.0/16`
2. Create a public subnet named `public-subnet` with IPv4 CIDR block `10.0.1.0/24`
3. Create a route table named `rt-public` and associate it with the `public-subnet`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-1.png)

4. Create an internet gateway named `igw` and attach it to the vpc `(my-vpc)`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-2.png)

5. Edit routes of the router:
   - Public Route Table`(rt-public)`:
      - Add a route with destination `0.0.0.0/0` and target `igw`

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-3.png)

Here is the resource map:

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image.png)


## Step 1: Set Up Your EC2 Instance

1. **Launch an EC2 instance:**
   - Choose an appropriate Amazon Machine Image (AMI), such as `Ubuntu`.
   - Choose the vpc `my-vpc` that we have created earlier.
   - Ensure that the instance is in the `public-subnet`.
   - Choose an appropriate instance type, such as `t2.micro`
   - Choose or create an appropriate key pair.
   - Choose or create an appropriate security group.

2. **Connect to your EC2 instance:**
   - Use SSH to connect to your EC2 instance:
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@your-public-ip
   ```
   - You can simply connect using AWS ec2 connect option. 

## Step 2: Install Flask and Create Your Flask Application

1. **Update and upgrade your system packages:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Install Python and pip:**
   ```bash
   sudo apt install python3 python3-pip -y
   ```

3. **Create a virtual environment (optional but recommended):**
   ```bash
   sudo apt install python3-venv -y
   python3 -m venv myenv
   source myenv/bin/activate
   ```

4. **Install Flask in your virtual environment:**
   ```bash
   pip install Flask
   ```
   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-6.png)

5. **Create your Flask application:**
   - Create a directory for your Flask app, e.g., `myflaskapp`.
   - Inside `myflaskapp`, create a file named `app.py` with the following content:
   ```python
   from flask import Flask

   app = Flask(__name__)

   @app.route('/')
   def hello():
      return "Hello, World!"

   if __name__ == '__main__':
      app.run(host='0.0.0.0')
   ```

### Step 3: Create a `systemd` Service File

1. **Create a new service file:**
   - Create a file named `flaskapp.service` in `/etc/systemd/system/`:
   ```bash
   sudo nano /etc/systemd/system/flaskapp.service
   ```

2. **Add the following content to the service file:**
   ```ini
   [Unit]
   Description=A simple Flask web application
   After=network.target

   [Service]
   User=ubuntu
   Group=ubuntu
   WorkingDirectory=/home/ubuntu/myflaskapp
   Environment="PATH=/home/ubuntu/myenv/bin"
   ExecStart=/home/ubuntu/myenv/bin/python /home/ubuntu/myflaskapp/app.py

   [Install]
   WantedBy=multi-user.target
   ```
   - Replace `/home/ubuntu/myflaskapp` with the absolute path to your Flask application directory.
   - Replace `/home/ubuntu/myenv` with the absolute path to your virtual environment.

### Step 4: Start and Enable the Flask Service

1. **Reload the `systemd` daemon to recognize the new service file:**
   ```bash
   sudo systemctl daemon-reload
   ```

2. **Start the Flask service:**
   ```bash
   sudo systemctl start flaskapp
   ```

3. **Enable the Flask service to start on boot:**
   ```bash
   sudo systemctl enable flaskapp
   ```

4. **Check the status of your service to ensure it's running correctly:**
   ```bash
   sudo systemctl status flaskapp
   ```

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-7.png)

### Step 5: Configure the Security Group

1. **Allow inbound traffic to port 5000:**
   - In the AWS Management Console, navigate to the EC2 dashboard.
   - Select "Security Groups" from the left-hand menu.
   - Find the security group associated with your EC2 instance.
   - Edit the inbound rules to allow traffic on port 5000 from your desired IP ranges (e.g., 0.0.0.0/0 for all IPs, though this is not recommended for `production`. But for now it is ok).

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-8.png)

### Step 6: Access Your Flask Application

1. **Open your web browser and navigate to:**
   ```http
   http://your-public-ip:5000
   ```

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2009/images/image-9.png)

You should see "Hello, World!" displayed, confirming that your Flask application is running and accessible via the public IP of your EC2 instance. So, we have successfully deployed a flask application in aws ec2 using systemd