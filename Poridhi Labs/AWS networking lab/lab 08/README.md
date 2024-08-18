# Deploy Nginx in EC2 using systemd

This guide provides detailed steps to deploy `NGINX` on an EC2 instance using `systemd`. The process includes setting up and configuring AWS infrastructure, launching and configuring an EC2 instance, and deploying and managing NGINX.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-10.png)

## What is systemd by the way?

`Systemd` is a **system and service manager** for Linux operating systems. It is responsible for starting, stopping and managing system services and daemons. It provides a unified interface for managing system services and simplifies the process of configuring and managing system services. It also provides a number of features such as on-demand service activation, dependency-based service activation, and service unit files that describe the service and its configuration.

## Prerequisites

1. Log in to the live AWS environment using the lab account.
2. Ensure you are in the `Singapore (ap-southeast-1)` region.

## Steps

## Step 1: Setup and configure AWS(vpc, subnet, route-table, Internet-Gateway)

1. Create a vpc named `my-vpc` with IPv4 CIDR block `10.0.0.0/16`
2. Create a public subnet named `public-subnet` with IPv4 CIDR block `10.0.1.0/24`
3. Create a route table named `rt-public` and associate it with the `public-subnet`.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-6.png)

4. Create an internet gateway named `igw` and attach it to the vpc.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-7.png)

5. Edit routes of the router:
   - Public Route Table(rt-public):
      - Add a route with destination `0.0.0.0/0` and target `igw`

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-8.png)

Here is the resource map:

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-1.png)


## Step 1: Set Up Your EC2 Instance

1. **Launch an EC2 instance:**
   - Choose an appropriate Amazon Machine Image (AMI), such as `Ubuntu`.
   - Ensure that the instance is in the `public-subnet` that we have created.
   - Configure the security group to allow traffic on the port your Flask app will be running on (usually port `5000`).

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-9.png)

2. **Connect to your EC2 instance:**
   - Use SSH to connect to your EC2 instance:
     ```bash
     ssh -i /path/to/your-key.pem ubuntu@your-public-ip
     ```
   - You can simply connect using AWS ec2 connect option.

## Step 2: Install NGINX and configure Service
1. **Update the package index and install NGINX.**

    ```sh
    sudo apt-get update
    sudo apt-get install nginx -y
    ```
   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image.png)

2. **Create a systemd Service File:**
   - Create a custom systemd service file for NGINX if you want to customize the service management.

    ```sh
    sudo nano /etc/systemd/system/nginx.service
    ```

    - Add the following content to the file:

    ```ini
    [Unit]
    Description=A high performance web server and a reverse proxy server
    After=network.target

    [Service]
    Type=forking
    ExecStart=/usr/sbin/nginx -c /etc/nginx/nginx.conf
    ExecReload=/usr/sbin/nginx -s reload
    ExecStop=/bin/kill -s QUIT $MAINPID
    PIDFile=/run/nginx.pid
    Restart=always

    [Install]
    WantedBy=multi-user.target
    ```

3. **Reload systemd and Start NGINX:**
   - Reload the systemd manager configuration to read the new service file, start the NGINX service, and enable it to start on boot.

    ```sh
    sudo systemctl daemon-reload
    sudo systemctl start nginx
    sudo systemctl enable nginx
    ```

## Step 3: Verify NGINX Deployment:
1. **Check the status of the NGINX service to ensure it is running correctly:**

    ```sh
    sudo systemctl status nginx
    ```
   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-2.png)

2. **Access NGINX:**
   - Open a web browser and navigate to the `public IP address` of your EC2 instance. You should see the default NGINX welcome page.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2008/images/image-3.png)

---

By following this guide, we have successfully set up and configured an EC2 instance within a VPC, installed NGINX, and managed it using systemd. This setup allows you to deploy a high-performance web server capable of serving static and dynamic content. 