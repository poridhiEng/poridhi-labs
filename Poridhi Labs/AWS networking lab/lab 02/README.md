# Deploying a Bastion Server in a Public Subnet

VPC allows users to create a private network within AWS, isolating and protecting resources. Within this VPC, a crucial security component is the bastion server. This server acts as a gateway, enabling secure access to resources in the private VPC environment from the internet. In this lab, we will deploy a bastion server in a public subnet.

![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2002/images/2.png?raw=true)

## What is a Bastion Server?

A bastion server is an EC2 instance that acts as a secure gateway for accessing private instances within an AWS VPC environment. Also known as a jump server, it provides a controlled access point from the internet into the private network. 

A bastion server runs on an Ubuntu EC2 instance hosted in a public subnet of an AWS VPC. This instance is configured with a security group that allows SSH access from anywhere over the internet. The bastion server facilitates secure connections to instances within private subnets, ensuring that these instances remain inaccessible directly from the internet, thereby enhancing the overall security of the VPC.


## Objectives

1. Create a VPC.
2. Create a Public Subnet.
3. Create Routes and an Internet Gateway.
4. Launch EC2 instances in the Public Subnets.
5. Add a Security Group.
6. SSH into the Public EC2 Instance. 

### 1. Create a VPC

A Virtual Private Cloud (VPC) provides an isolated network environment in AWS, enabling you to launch AWS resources in a virtual network that you define.

1. **Navigate to the VPC Console:**
   - Log into the AWS Management Console.
   - In the Services menu, select "VPC" or Search `VPC`.

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2002/images/1.png?raw=true)

2. **Create the VPC:**
   - In the left-hand menu, select "Your VPCs".
   - Click on "Create VPC".
   - Set the following values:
     - **VPC Name:** `my-vpc`
     - **IPv4 CIDR block:** `10.0.0.0/16`
     - **IPv6 CIDR block:** No IPv6 CIDR block
     - **Tenancy:** Default Tenancy
   - Click "Create VPC".

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/vpc.png?raw=true)

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

### 4. Create Route Tables

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

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2002/images/3.png?raw=true)

### 5. Create Security Group

Security groups act as a virtual firewall for your EC2 instances to control inbound and outbound traffic. They are essential for defining and enforcing network access rules.

1. **Navigate to Security Groups:**
   - In the left-hand menu, select "Security Groups".
   - Click on "Create security group".

2. **Create the Security Group:**
   - **Security group name:** `security-group-1`
   - **Description:** `Allow SSH and all outbound traffic`
   - **VPC:** Select `my-vpc`

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/13.png?raw=true)

3. **Configure Inbound Rules:**
   - In "Inbound rules" section click on `Add rule`>
   - **Type:** `SSH`
   - **Source:** `Anywhere` (0.0.0.0/0)

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/14.png?raw=true)

4. **Configure Outbound Rules:**
   - In "Outbound rules" section click on `Add rule`>
   - **Type:** `All traffic`
   - **Destination:** `Anywhere` (0.0.0.0/0)

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/15.png?raw=true)

5. **Verify Resources:**
   - In the left-hand menu, select "VPC".
   - View the resources map of our vpc (`my-vpc`)

   ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2002/images/4.png?raw=true)

### 6. Launch EC2 Instances

EC2 instances are virtual servers in the cloud, providing scalable computing capacity. Launching instances in public and private subnets allows you to control access and network traffics.

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

     *Note : Download and save the key in your desired directroy,we will need it later*

     ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/18.png?raw=true)

   - **Network settings:** Click "Edit".
     - **VPC:** Select `my-vpc`.
     - **Subnet:** Select `public-subnet`.
     - **Auto-assign Public IP:** Enable.
     - **Security group:** Select `security-group-1`.
   - Click "Launch instance".

    ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/19.png?raw=true)

### 7. SSH into the Public EC2 Instance

SSH (Secure Shell) allows you to securely access your EC2 instances. We'll first connect to the public instance from your local machine.

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

     ![](https://github.com/Galadon123/poridhi.io.intern/blob/main/AWS%20networking%20lab/lab%2003/images/32.png?raw=true)


By following these steps, we created a secure and efficient way to access private instances within an AWS VPC, improving the network's security. This project demonstrates how to use AWS VPC features to implement a bastion server, providing a strong solution for managing access to private resources in the cloud.