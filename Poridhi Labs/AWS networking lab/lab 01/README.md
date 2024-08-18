# Launch An Ec2 Instance In A Virtual Private Cloud (vpc)

## Overview

This guide will teach you how to set up a Virtual Private Cloud (VPC) from scratch and launch an EC2 instance within it. By the end of this guide, you will have created a VPC, set up a public subnet, configured routing with an Internet Gateway, and launched an EC2 instance.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/lab-01-diagram.png)

## Learning Objectives
1. Create a VPC with CIDR 10.0.0.0/16
2. Create a Public Subnet within the VPC
3. Create and Attach an Internet Gateway to the VPC
4. Configure Route Tables for Internet Access
5. Launch an EC2 Instance in the Subnet
6. Access the EC2 Instance

## Step-by-Step Guide

### Step 1: Create Your VPC
1. **Open the AWS Management Console** and search for "VPC" in the search bar.
2. On the left-hand side, click on "Your VPCs".
3. Click on "Create VPC" at the top right corner.
4. Name your VPC using a tag.
5. Set the IPv4 CIDR block to `10.0.0.0/16`.
6. Click "Create VPC" to create your VPC.
   
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-01.png)

   Congratulations on creating your first VPC!

### Step 2: Create a Public Subnet
1. After creating your VPC, click on "Subnets" on the left-hand side.
2. Click on "Create Subnet".
3. Designate the VPC you just created.
4. Assign a CIDR block within your VPC’s range (e.g., `10.0.0.0/24`).
5. Click "Create Subnet" to create your subnet.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-02.png)

5. Click on the created subnet and then "Edit subnet settings".
6. Enable "Auto-assign public IPv4 address" and save.

   <!-- ![Enable Auto-assign IPv4](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-03.png)

### Step 3: Create and Attach an Internet Gateway
1. Click on "Internet Gateways" on the left-hand side.
2. Click "Create internet gateway".

   <!-- ![Create Internet Gateway](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-04.png)

3. Once created, click "Actions" and then "Attach to VPC".
4. Select your VPC and attach the Internet Gateway.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-05.png)

### Step 4: Create Route Tables
1. Click on "Route Tables" on the left-hand side.
2. Click "Create route table".
3. Associate the new route table with your VPC.

   <!-- ![Create Route Table](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-06.png)

4. Add a route to allow internet traffic by specifying the destination `0.0.0.0/0` and target as your Internet Gateway.

   <!-- ![Add Route](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-07.png)

5. Click on the "Subnet Associations" tab, then "Edit Subnet Associations".
6. Select your public subnet and save.

   <!-- ![Associate Subnet](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-08.png)


### Network Diagram
Below is a visual representation of the VPC setup with subnets in `ap-southeast-1a` Availability Zone (AZ).

   <!-- ![VPC Network Diagram](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-09.png)


### Step 5: Launch an EC2 Instance
1. In the AWS console, search for "EC2" and click on "Launch Instance".
2. Give a name to your ec2 instance
3. Select the Amazon Machine Image (AMI) for Ubuntu image.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-10.png)

3. Choose the instance type, e.g., `t2.micro`.
4. Configure instance details, selecting the VPC and public subnet you created.
5. Create a key pair (.pem file) and save it securely.

   <!-- ![Create Key Pair](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-11.png)

6. Configure the security group to allow SSH (port 22) and HTTP (port 80) access.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-12.png)

7. Launch the instance and wait for it to start up.

### Step 6: Access the EC2 Instance
1. Select your running instance in the EC2 console.
2. Click "Connect".

   <!-- ![Connect to Instance](image) -->
   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-13.png)

3. SSH into the Public Instance:
   - Open a terminal where you saved the key pair and run:
     
     ```sh
     ssh -i MyKeyPair.pem ubuntu@<public_instance_ip>
     ```
     
   - Replace <public_instance_ip> with the public IP address of the public instance.

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-14.png)

   We can see that we have connected to our ec2 instance.

### Step 7: Verify that your EC2 instance has internet access

1. Ping a domain name, such as google.com, to test DNS resolution.

   ```sh
   ping google.com
   ```

   ![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/AWS%20networking%20lab/lab%2001/images/vpc-15.png)

Congratulations on successfully creating your first VPC and launching an EC2 instance!
