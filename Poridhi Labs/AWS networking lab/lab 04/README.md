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

1. Create a vpc named `my-vpc` with IPv4 CIDR block `10.0.0.0/16`

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image.png)

2. Create a public subnet named `public-subnet` with IPv4 CIDR block `10.0.1.0/24`
3. Create a private subnet named `private-subnet` with IPv4 CIDR block `10.0.2.0/24`

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-1.png)

4. Create a route table named `rt-public` and associate it with the `public-subnet`.
5. Create a route table named `rt-private` and associate it with the `private-subnet`.
6. Create an internet gateway named `igw` and attach it to the vpc.
7. Create a NAT gateway named `ngw`, allocate a elastic ip, and attach it to the public subnet.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-3.png)


8. Edit routes of the router:
    - Public Route Table(rt-public):
        - Add a route with destination `0.0.0.0/0` and target `igw`
    - Private Route Table(rt-private):
        - Add a route with destination `0.0.0.0/0` and target `ngw`

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-2.png)

Here, is the resource map:

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-4.png)

### Step 2: Launce EC2 instances

#### Bastion Server

1. Launch an EC2 instance named `Bastion server` in the `public-subnet`.
2. Select `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type` as the AMI.
3. Create a key pair named `bastion.pem` download it locally.
4. Add a security group named `bastion-scg` with inbound rules:
    - SSH from anywhere or from your IP.

#### Private Instance

1. Launch an EC2 instance named `Private Instance` in the `private-subnet`.
2. Select `Ubuntu Server 24.04 LTS (HVM), SSD Volume Type` as the AMI.
3. Select key pair named `bastion.pem`.
4. Add a security group named `Private-Instance` with inbound rules:
    - Allow inbound SSH (port 22) from the bastion server's security group.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-6.png)

### Step 3: Configure the Bastion Server

1. **Connect to the Bastion Server**:
   - Use SSH to connect to the bastion server using the public IP:
     ```bash
     ssh -i /path/to/key.pem ubuntu@<bastion-public-ip>
     ```
     ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/AWS%20networking%20lab/lab%2004/images/image-7.png)
2. **Copy the pem file into the Bastion Server**:
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