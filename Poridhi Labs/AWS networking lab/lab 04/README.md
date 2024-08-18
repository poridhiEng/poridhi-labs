# Create a Secure SSH connection between a Bastion Server and a Private Instance

## Overview

In a *cloud environment*, a common security practice is to place *sensitive* resources like EC2 instances in private subnets to **minimize exposure** to the internet. To access these private instances securely, you can use a `bastion server` (or jump box) situated in a `public subnet`. The bastion server acts as an intermediary for establishing SSH connections to instances in private subnets.

This documentation provides a step-by-step guide on how to set up and establish a secure SSH connection between a bastion server and a private instance.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/archi.png)

## Prerequisites

1. Log in to the live AWS environment using the lab account.
2. Ensure you are in the `Singapore (ap-southeast-1)` region.

## Steps

### Step 1: Configure and setup AWS(vpc, subnet, route-table, Internet gateway, NAT gateway)

1. **Create a VPC**
   - **CIDR:** `10.0.0.0/16`

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image.png)

2. **Create a Public Subnet**
   - **CIDR:** `10.0.1.0/24`
   - **Availability Zone:** `ap-southeast-1a`
   - **Enable Auto-assign Public IPv4 Address**

3. **Create a Private Subnet**
   - **CIDR:** `10.0.2.0/24`
   - **Availability Zone:** `ap-southeast-1a`
   - **Do not enable Auto-assign Public IPv4 Address**

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-1.png)

4. Create a **Public Route Table** named `rt-public`
    - **Associate** it with the `public-subnet`.

5. Create a **Private Route Table** named `rt-private`
    - **Associate** it with the `private-subnet`.

6. **Create an Internet Gateway (IGW)**
   - Attach the IGW to the VPC.

7. **Create a NAT Gateway**
   - Go to the VPC Dashboard in the AWS Management Console.
   - In the left-hand menu, click on `NAT Gateways`.
   - Click "Create NAT Gateway".
   - Select the public subnet (`10.0.1.0/24`).
   - Allocate an Elastic IP for the NAT Gateway.
   - Click "Create a NAT Gateway".

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-3.png)


8. Edit routes of the router:
    - Public Route Table(rt-public):
        - Add a route with destination `0.0.0.0/0` and target `igw` (Internet Gateway)
    - Private Route Table(rt-private):
        - Add a route with destination `0.0.0.0/0` and target `ngw` (NAT Gateway)

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-2.png)

**Here, is the resource map:**

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-4.png)

### Step 2: Launce EC2 instances

1. **Launch a Bastion Host in the Public Subnet**
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance Type:** t2.micro (or as needed)
   - **Network:** Select the VPC and public subnet created earlier
   - **Security Group:** Create a security group (e.g., *Bastion-scg*).
   - **Key-pair:** Create a key pair and save it securely.


2. **Launch a private EC2 Instance in the Private Subnet**
   - **AMI:** Ubuntu Server 24.04 LTS
   - **Instance Type:** t2.micro (or as needed)
   - **Network:** Select the VPC and private subnet created earlier
   - **Security Group:** Add a security group named `Private-Instance`.
   - **Key-pair:** Select the key pair created earlier.


### Step 3: Configure the security group

1. Configure the public instance security group `Bastion-scg` that allows SSH access (port 22) from your IP.

2. Configure the private instance security group `Private-Instance` to allow SSH access from the `Bastion-scg` security group. Means you can access it from only the bastion server.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-6.png)

### Step 3: Configure the Bastion Server

1. **Connect to the Bastion Server**:
   - Use SSH to connect to the **bastion server** using the public IP:

     ```bash
     ssh -i /path/to/key.pem ubuntu@<bastion-public-ip>
     ```
     ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-7.png)

2. **Copy the pem file from your local machine into the Bastion Server**:

    - Use SCP to copy the private key file to the bastion server:

    ```bash
    scp -i /path/to/key.pem /path/to/key.pem ubuntu@<bastion-public-ip>
    ```
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-8.png)
    

### Step 3: Establish the SSH Connection to the Private Instances

1. **SSH from the Bastion Server to a Private Instance**:
   - From the bastion server, use SSH to connect to a private instance:

     ```bash
     ssh -i ~/.ssh/key.pem ubuntu@<private-instance-private-ip>
     ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/ssh.png)
    
    So, we have successfully created a SSH connection, and ssh into the private instance.

## Conclusion

Setting up a secure SSH connection between a bastion server and private instances enhances the security of your cloud infrastructure. By following these steps, you can ensure that your private instances remain protected from direct internet exposure while still being accessible for administration through the bastion server.