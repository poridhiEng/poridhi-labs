# DEPLOY MONGODB IN EC2 USING SYSTEMD

In this lab, we will deploy MongoDB on an EC2 instance using systemd for process management. We will set up a VPC with public and private subnets, launch EC2 instances, and configure security groups. MongoDB will be installed on a private instance, managed using systemd, and accessed through SSH from a public instance.

![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/logo.png?raw=true)

### Lab Objectives

1. **Setup VPC and Subnets**
2. **Setup Internet Gateway and NAT Gateway**
3. **Launch EC2 Instances**
4. **Create Security Groups**
5. **SSH Access Configuration**
6. **Install and Configure MongoDB**
7. **Manage MongoDB with Systemd**



### 1. Create a VPC

A Virtual Private Cloud (VPC) provides an isolated network environment in AWS, enabling you to launch AWS resources in a virtual network that you define.

1. **Navigate to the VPC Console:**
   - Log into the AWS Management Console.
   - In the Services menu, select "VPC" or search for "VPC".

2. **Create the VPC:**
   - Click on "Create VPC".
   - Set the following values:
     - **VPC Name:** `my-vpc`
     - **IPv4 CIDR block:** `10.0.0.0/16`
     - **IPv6 CIDR block:** No IPv6 CIDR block
     - **Tenancy:** Default Tenancy
   - Click "Create VPC".

### 2. Create Subnets

Subnets allow you to partition your VPC's IP address range into smaller segments, enabling better management of resources within different availability zones.

1. **Navigate to Subnets:**
   - In the left-hand menu, click on "Subnets".
   - Click on "Create subnet".

2. **Create the Public Subnet:**
   - **VPC ID:** Select the VPC ID for `my-vpc`.
   - **Subnet Name:** `public-subnet`
   - **Availability Zone:** `ap-southeast-1a`
   - **IPv4 CIDR block:** `10.0.1.0/24`
   - Click "Create Subnet".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/2.png?raw=true)


3. **Create the Private Subnet:**
   - Click "Add new subnet".
   - **Subnet Name:** `private-subnet`
   - **Availability Zone:** `ap-southeast-1b`
   - **IPv4 CIDR block:** `10.0.2.0/24`
   - Click "Create Subnet".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/3.png?raw=true)

### 3. Create an Internet Gateway

An Internet Gateway allows instances in the VPC to communicate with the internet. It serves as a target for the VPC route tables for internet-routable traffic.

1. **Navigate to Internet Gateways:**
   - In the left-hand menu, select "Internet Gateways".
   - Click on "Create internet gateway".

2. **Create the Internet Gateway:**
   - **Name tag:** `my-IGW`
   - Click "Create internet gateway".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/4.png?raw=true)

3. **Attach the Internet Gateway to the VPC:**
   - Select the newly created internet gateway.
   - Click "Actions" > "Attach to VPC".
   - Select `my-vpc`.
   - Click "Attach internet gateway".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/5.png?raw=true)


### 4. Create a NAT Gateway

A NAT Gateway allows instances in the private subnet to access the internet for updates and other activities.

1. **Navigate to NAT Gateways:**
   - In the left-hand menu, select "NAT Gateways".
   - Click on "Create NAT Gateway".

2. **Create the NAT Gateway:**
   - **Name:** `my-nat-gateway`
   - **Subnet:** Select `public-subnet`.
   - **Elastic IP Allocation ID:** Click "Allocate Elastic IP" and then "Allocate".
   - Click "Create a NAT Gateway".

    ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/1.png?raw=true)


### 5. Create Route Tables

Route tables control the routing of network traffic within your VPC. Public route tables direct traffic to the Internet Gateway, while private route tables handle internal routing.

1. **Navigate to Route Tables:**
   - In the left-hand menu, select "Route Tables".
   - Click on "Create route table".

2. **Create the Public Route Table:**
   - **Name:** `public-route-table`
   - **VPC:** Select `my-vpc`.
   - Click "Create route table".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/6.png?raw=true)

3. **Add Route to the Internet Gateway:**
   - Select the `public-route-table`.
   - In the "Routes" tab, click "Edit routes".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/7.png?raw=true)

   - Click "Add route".
   - **Destination:** `0.0.0.0/0`
   - **Target:** Select the internet gateway `my-IGW`.
   - Click "Save changes".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/8.png?raw=true)


4. **Associate Public Route Table with Public Subnet:**
   - In the "Subnet associations" tab, click "Edit subnet associations".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/9.png?raw=true)

   - Select `public-subnet`.
   - Click "Save associations".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/10.png?raw=true)

5. **Create the Private Route Table:**
   - Click "Create route table".
   - **Name:** `private-route-table`
   - **VPC:** Select `my-vpc`.
   - Click "Create route table".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/11.png?raw=true)

6. **Add Route to the NAT Gateway:**
   - Click "Add route".
   - **Destination:** `0.0.0.0/0`
   - **Target:** Select the NAT Gateway `my-nat-gateway`.
   - Click "Save changes".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/2.png?raw=true)

   


7. **Associate Private Route Table with Private Subnet:**
   - Select the `private-route-table`.
   - In the "Subnet associations" tab, click "Edit subnet associations".
   - Select `private-subnet`.
   - Click "Save associations".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/12.png?raw=true)

### 6. Create Security Groups

#### Security Group 1: Allow SSH and All Outbound Traffic

1. **Navigate to Security Groups:**
   - In the left-hand menu, select "Security Groups".
   - Click on "Create security group".

2. **Create the Security Group:**
   - **Security group name:** `security-group-1`
   - **Description:** `Allow SSH and all outbound traffic`
   - **VPC:** Select `my-vpc`

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/13.png?raw=true)

3. **Configure Inbound Rules:**
   - In "Inbound rules" section click on `Add rule`:
     - **Type:** `SSH`
     - **Source:** `Anywhere` (0.0.0.0/0)

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/14.png?raw=true)

4. **Configure Outbound Rules:**
   - In "Outbound rules" section click on `Add rule`:
     - **Type:** `All traffic`
     - **Destination:** `Anywhere` (0.0.0.0/0)

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/15.png?raw=true)

#### Security Group 2: Allow SSH, MongoDB, and All Outbound Traffic

1. **Navigate to Security Groups:**
   - In the left-hand menu, select "Security Groups".
   - Click on "Create security group".

2. **Create the Security Group:**
   - **Security group name:** `security-group-2`
   - **Description:** `Allow SSH, MongoDB, and all outbound traffic`
   - **VPC:** Select `my-vpc`

3. **Configure Inbound Rules:**
   - In "Inbound rules" section click on `Add rule`:
     - **Type:** `SSH`
     - **Source:** `Anywhere` (0.0.0.0/0)

   - Click on `Add rule`:
     - **Type:** `Custom TCP`
     - **Port range:** `27017`
     - **Source:** `Anywhere` (0.0.0.0/0)

     ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/3.png?raw=true)

4. **Configure Outbound Rules:**
   - In "Outbound rules" section click on `Add rule`:
     - **Type:** `All traffic`
     - **Destination:** `Anywhere` (0.0.0.0/0)

### 7. Launch EC2 Instances

EC2 instances are virtual servers in the cloud, providing scalable computing capacity. Launching instances in public and private subnets allows you to control access and network traffic.

1. **Launch Public EC2 Instance:**
   - Navigate to "EC2" in the Services menu.
   - Click on "Instances" > "Launch instances".
   - **Name:** `ec2-instance-1`
   - **Application and OS Images (Amazon Machine Image):** Select "Ubuntu Server 24.04 LTS".
   - **Instance Type:** Select `t2.micro`.

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/17.png?raw=true)

   - **Key pair (login):** Click "Create new key pair". 
     - **Key pair name:** `public-key-pair`
     - **Key pair type:** RSA
     - **Private key file format:** `.pem` or `.ppk`
     - Click "Create key pair".

     ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/18.png?raw=true)
     
     *Note : Download and save the key in your desired directroy,we will need it later*


   - **Network settings:** Click "Edit".
     - **VPC:** Select `my-vpc`.
     - **Subnet:** Select `public-subnet`.
     - **Auto-assign Public IP:** Enable.
     - **Security group:** Select `security-group-1`.
   - Click "Launch instance".

    ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/19.png?raw=true)

2. **Launch Private EC2 Instance:**
   - Navigate back to "Instances" > "Launch instances".
   - **Name:** `ec2-instance-2`
   - **Application and OS Images (Amazon Machine Image):** Select "Ubuntu Server 24.04 LTS".
   - **Instance Type:** Select `t2.micro`.
   - **Key pair (login):** Click "Create new key pair".
     - **Key pair name:** `private-key-pair`
     - **Key pair type:** RSA
     - **Private key file format:** `.pem` or `.ppk`
     - Click "Create key pair".

     *Note : Download and save the key in your desired directroy,we will need it later*

   - **Network settings:** Click "Edit".
     - **VPC:** Select `my-vpc`.
     - **Subnet:** Select `private-subnet`.
     - **Auto-assign Public IP:** Disable.
     - **Security group:** Select `security-group-1`.
   - Click "Launch instance".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/20.png?raw=true)

### 8. SSH from Local Machine to Public EC2 Instance

1. **Set Permissions on the Key Pair:**
   - Open your terminal.
   - Navigate to the directory containing your `public-key-pair.pem` file.
   - Run the following command to set the correct permissions:

     ```sh
     chmod 400 "public-key-pair.pem"
     ```

2. **Connect to the Public EC2 Instance:**
   - Obtain the public IP address of `ec2-instance-1` from the EC2 console.
   - Run the following command to connect to the instance (replace `<ec2-instance-1-public-IP>` with your instance's public IP address):

     ```sh
     ssh -i "public-key-pair.pem" ubuntu@<ec2-instance-1-public-IP>
     ```

### 9. Transfer the Private Key to the Public EC2 Instance

1. **Navigate to the Directory Containing the Private Key on Your Local Machine:**
   - Open a new terminal window or tab.
   - Navigate to the directory containing your `private-key-pair.pem` file.

2. **Transfer the Private Key Using SCP:**
   - Run the following command to transfer the private key to the public EC2 instance (replace `<ec2-instance-1-public-IP>` with your instance's public IP address):

     ```sh
     scp -i "public-key-pair.pem" private-key-pair.pem ubuntu@<ec2-instance-1-public-IP>:/home/ubuntu/
     ```

     ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/4.png?raw=true)

### 10. SSH from the Public EC2 Instance to the Private EC2 Instance

1. **Set Permissions on the Private Key File:**
   - Once connected to `ec2-instance-1`, set the correct permissions:

     ```sh
     chmod 400 /home/ubuntu/private-key-pair.pem
     ```

2. **Connect to the Private EC2 Instance:**
   - Obtain the private IP address of `ec2-instance-2` from the EC2 console.
   - Run the following command to connect to the instance (replace `<ec2-instance-2-private-IP>` with your instance's private IP address):

     ```sh
     ssh -i "/home/ubuntu/private-key-pair.pem" ubuntu@<ec2-instance-2-private-IP>
     ```

     ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/5.png?raw=true)
### 11. Install and Run MongoDB Using systemd

1. **Import the Public Key for the MongoDB Packages:**
   ```sh
   wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
   ```

2. **Create a List File for MongoDB:**
   ```sh
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
   ```

3. **Update the Package Database:**
   ```sh
   sudo apt-get update
   ```

4. **Install MongoDB Packages:**
   ```sh
   sudo apt-get install -y mongodb-org
   ```

5. **Start MongoDB Using systemd:**
   ```sh
   sudo systemctl start mongod
   ```
   - **Explanation:** Initiates the MongoDB service (`mongod`) using `systemctl`, which is the command-line tool for controlling `systemd` services.

6. **Enable MongoDB to Start on Boot:**
   ```sh
   sudo systemctl enable mongod
   ```
   - **Explanation:** Configures MongoDB to launch automatically during system startup. This ensures MongoDB restarts after system reboots without manual intervention.

7. **Check the Status of MongoDB:**
   ```sh
   sudo systemctl status mongod
   ```
   - **Explanation:** Displays the current operational status of the MongoDB service (`mongod`). This command provides information about whether MongoDB is active, inactive, or facing any issues.

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2007/images/6.png?raw=true)