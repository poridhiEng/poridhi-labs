# Deploying MySQL on EC2 Using Systemd

## Overview

This guide outlines the process of deploying MySQL on an Amazon EC2 instance using systemd for service management. The deployment process will be structured to ensure that the MySQL server is efficiently managed and automatically starts on system boot. The steps include setting up the VPC, subnet, security group, and configuring MySQL.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-diagram.png)

## Prerequisites
- AWS account with appropriate permissions
- SSH key pair (e.g., `my-key.pem`) for connecting to the EC2 instance

### Step 1: VPC and Subnet Configuration

1. **Create a VPC**
   - **CIDR:** `10.0.0.0/16`

2. **Create a Private Subnet**
   - **CIDR:** `10.0.1.0/24`
   - **Availability Zone:** `ap-southeast-1a`
   - **Do not enable Auto-assign Public IPv4 Address**

3. **Create a Public Subnet**
   - **CIDR:** `10.0.2.0/24`
   - **Availability Zone:** `ap-southeast-1a`
   - **Enable Auto-assign Public IPv4 Address**

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/dc-01.png)

4. **Create an Internet Gateway (IGW)**
   - Attach the IGW to the VPC.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/dc-02.png) 

5. **Create a NAT Gateway**
   - Go to the VPC Dashboard in the AWS Management Console.
   - In the left-hand menu, click on "NAT Gateways".
   - Click "Create NAT Gateway".
   - Select the public subnet (`10.0.2.0/24`).
   - Allocate an Elastic IP for the NAT Gateway.
   - Click "Create a NAT Gateway".

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/dc-03.png)

6. **Create and Configure Route Tables**
   - **Public Route Table:**
     - Add a route with `Destination: 0.0.0.0/0` and `Target: IGW`.
     - Associate the route table with the public subnet.

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/dc-04.png)

   - **Private Route Table:**
     - Add a route with `Destination: 0.0.0.0/0` and `Target: NAT Gateway ID (select the NAT Gateway created above)`.
     - Associate the route table with the private subnet.

     ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/dc-06.png)

7. **Create a Security Group for MySQL**
   - **Inbound Rules:**
     - Type: MySQL/Aurora
     - Protocol: TCP
     - Port: 3306
   - **Outbound Rules:**
     - Allow all outbound traffic

    ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-02.png)

## Network Diagram

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-01.png)

### Step 2: Launch and Connect to EC2 Instance

1. **Launch a Bastion Host in the Public Subnet**
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance Type:** t2.micro (or as needed)
   - **Network:** Select the VPC and public subnet created earlier
   - **Security Group:** Create or use a security group that allows SSH access (port 22) from your IP.
   - **Key-pair:** Create a key pair named `my-key.pem` and save it securely.

2. **Launch MySQL EC2 Instance in the Private Subnet**
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance Type:** t2.micro (or as needed)
   - **Network:** Select the VPC and private subnet created earlier
   - **Security Group:** Select the MySQL security group 
   - **Key-pair:** Select the key pair created earlier

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/dc-11.png)

3. **Connect to the Bastion Host**

   Open a terminal where you saved the key pair and run:

   ```bash
   chmod 400 "my-key.pem"
   ssh -i "my-key.pem" ubuntu@<Public_IP_of_Bastion_Host>
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-03.png)

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-04.png)

4. **Copy the Key Pair to the Public Instance:**
    - On your local machine, run the following command to copy the key pair to the public instance:

      ```sh
      scp -i <My-key.pem> <My-key.pem> ubuntu@<public_instance_ip>:~
      ```

    Replace <public_instance_ip> with the public IP address of the public instance and the <My-key.pem> with the keypair.

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-05.png)

5. **Connect to the MySQL Instance from the Bastion Host**

    - After coping the keypair into the public instance, ssh into public instance

      ```sh
      ssh -i "my-key.pem" ubuntu@<Public_IP_of_Bastion_Host>
      ```
    - change the file permissions of the copied key pair:
   
      ```sh
      chmod 400 "my-key.pem"
      ```
    - ssh into the private instance from the public instance:
   
      ```sh
      ssh -i "my-key.pem" ubuntu@<Private_IP_of_MySQL_Instance>
      ```

    - Remember to Replace the <private_instance_ip> with the private IP address of the Mysql instance.

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-06.png)

      ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-07.png)

Now, We are currently within the private MySQL instance. Here we will deploy MySQL using systemd.

### Step 3: Update Packages and Install MySQL

1. **Update Package List and Install MySQL**
   ```bash
   sudo apt update
   sudo apt-get install mysql-server -y
   ```

2. **Verify MySQL Installation**
   ```bash
   mysql --version
   ```

### Step 4: Secure MySQL Installation

1. **Run the MySQL Secure Installation Script**
   ```bash
   sudo mysql_secure_installation
   ```

   Follow the prompts to secure your MySQL installation (e.g., set root password, remove anonymous users, disallow root login remotely, remove test database, and reload privilege tables).

### Step 5: Configure MySQL with Systemd

1. **Create Systemd Service File for MySQL**
   ```bash
   sudo nano /etc/systemd/system/mysql.service
   ```

2. **Paste the Following Content and Save**
   ```ini
   [Unit]
   Description=MySQL Server
   After=syslog.target
   After=network.target

   [Service]
   Type=simple
   PermissionsStartOnly=true
   ExecStartPre=/bin/mkdir -p /var/run/mysqld
   ExecStartPre=/bin/chown mysql:mysql -R /var/run/mysqld
   ExecStart=/usr/sbin/mysqld --basedir=/usr --datadir=/var/lib/mysql --plugin-dir=/usr/lib/mysql/plugin --log-error=/var/log/mysql/error.log --pid-file=/var/run/mysqld/mysqld.pid --socket=/var/run/mysqld/mysqld.sock --port=3306
   TimeoutSec=300
   PrivateTmp=true
   User=mysql
   Group=mysql
   WorkingDirectory=/usr

   [Install]
   WantedBy=multi-user.target
   ```

### Step 6: Manage MySQL Service with Systemd

1. **Reload Systemd and Start MySQL Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start mysql
   ```

2. **Enable MySQL Service on Boot**
   ```bash
   sudo systemctl enable mysql
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-08.png)

3. **Verify MySQL Service Status**
   ```bash
   sudo systemctl status mysql
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2006/images/systemd-new-09.png)

## Conclusion

We have successfully deployed MySQL on an EC2 instance using systemd for service management. This setup ensures that MySQL starts automatically with the system and can be easily managed using systemd commands.
