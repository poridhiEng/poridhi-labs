# SSH Key-Based Authentication to access Multiple EC2 instances via a Bastion Server

## Overview
SSH (Secure Shell) is a protocol for securely connecting to remote systems over a network. Using public/private key pairs for authentication is a more secure method than password-based authentication.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-1.png)

We will work on a scenario like this, suppose we have four EC2 instances: one public-facing **bastion server** and **three private server**. We want to SSH into each private servers.

## Before starting, why Use SSH Keys?

- **Enhanced Security:** Passwords can be vulnerable, especially if they are weak or reused. SSH keys provide stronger authentication.

- **Convenience:** Once set up, SSH keys allow you to log in to a server without needing to type a password.

## Create Infrastructure

For this setup, we will need a Publicly accessible **Bastion server**, and **three private servers**. We can create these servers in AWS. We can manually create the servers by login in to the AWS management console or we can create the servers and other necessary resouces using PULUMI or Terraform. In this lab, we will use `PULUMI Python` as Infrastructure as code. 

Here is our overall architecture:

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-15.png)

### Steps to create the resources and servers in aws using PULUMI.

1. **Configure AWS CLI**

- Configure AWS CLI in your local machine with necessary infromation.

  ```sh
  aws configure
  ```

  ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-2.png)

  Choose the Default region: `ap-southeast-1`

2. **Setup PULUMI for your project**

- Login into pulumi with your access token

    ```sh
    pulumi login
    ```

- Create an empty directory ( e.g., `Infra-for-ssh`)

    ```sh
    mkdir Infra-for-ssh
    cd Infra-for-ssh
    ```

- Install python (venv)

    ```sh
    sudo apt update
    sudo apt install python3.8-venv
    ```

- Run the following command to create to initialize a new Pulumi project:

    ```sh
    pulumi new aws-python
    ```
    Follow the prompts to set up your project.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-16.png)

3. **Create a Key Pair for your SERVER's**:

    We will use specific keys for SSHing into servers. So, we have to create 4 key pairs as we have 4 servers. This is for more secure connection. You can also create a single key pair as well.

- Bastion-server key generation

    ```sh
    aws ec2 create-key-pair --key-name BastionServer --query 'KeyMaterial' --output text > BastionServer.pem
    chmod 400 BastionServer.pem
    ```
- Private-server1 key generation

    ```sh
    aws ec2 create-key-pair --key-name PrivateServer1 --query 'KeyMaterial' --output text > PrivateServer1.pem
    chmod 400 PrivateServer1.pem
    ```

- Private-server1 key generation

    ```sh
    aws ec2 create-key-pair --key-name PrivateServer2 --query 'KeyMaterial' --output text > PrivateServer2.pem
    chmod 400 PrivateServer2.pem
    ```
- Private-server1 key generation

    ```sh
    aws ec2 create-key-pair --key-name PrivateServer3 --query 'KeyMaterial' --output text > PrivateServer3.pem
    chmod 400 PrivateServer3.pem
    ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-17.png)

    **NOTE:** Make sure to set the correct permission for the keys

4. **Open `__main__.py` file in the project directory**

    ```python
    import pulumi
    import pulumi_aws as aws

    # Create a VPC
    vpc = aws.ec2.Vpc("my-vpc",
        cidr_block="10.0.0.0/16",
        tags={"Name": "my-vpc"}
    )

    # Export the VPC ID
    pulumi.export("vpcId", vpc.id)

    # Create a public subnet
    public_subnet = aws.ec2.Subnet("public-subnet",
        vpc_id=vpc.id,
        cidr_block="10.0.1.0/24",
        availability_zone="ap-southeast-1a",
        map_public_ip_on_launch=True,
        tags={"Name": "public-subnet"}
    )

    # Export the public subnet ID
    pulumi.export("publicSubnetId", public_subnet.id)

    # Create a private subnet
    private_subnet = aws.ec2.Subnet("private-subnet",
        vpc_id=vpc.id,
        cidr_block="10.0.2.0/24",
        availability_zone="ap-southeast-1a",
        tags={"Name": "private-subnet"}
    )

    # Export the private subnet ID
    pulumi.export("privateSubnetId", private_subnet.id)

    # Create an Internet Gateway
    igw = aws.ec2.InternetGateway("internet-gateway",
        vpc_id=vpc.id,
        tags={"Name": "IGW"}
    )

    # Export the Internet Gateway ID
    pulumi.export("igwId", igw.id)

    # Create a route table for the public subnet
    public_route_table = aws.ec2.RouteTable("public-route-table",
        vpc_id=vpc.id,
        tags={"Name": "rt-public"}
    )

    # Create a route in the route table for the Internet Gateway
    route = aws.ec2.Route("igw-route",
        route_table_id=public_route_table.id,
        destination_cidr_block="0.0.0.0/0",
        gateway_id=igw.id
    )

    # Associate the route table with the public subnet
    route_table_association = aws.ec2.RouteTableAssociation("public-route-table-association",
        subnet_id=public_subnet.id,
        route_table_id=public_route_table.id
    )

    # Export the public route table ID
    pulumi.export("publicRouteTableId", public_route_table.id)

    # Allocate an Elastic IP for the NAT Gateway
    eip = aws.ec2.Eip("nat-eip", vpc=True)

    # Create the NAT Gateway
    nat_gateway = aws.ec2.NatGateway("nat-gateway",
        subnet_id=public_subnet.id,
        allocation_id=eip.id,
        tags={"Name": "NGW"}
    )

    # Export the NAT Gateway ID
    pulumi.export("natGatewayId", nat_gateway.id)

    # Create a route table for the private subnet
    private_route_table = aws.ec2.RouteTable("private-route-table",
        vpc_id=vpc.id,
        tags={"Name": "rt-private"}
    )

    # Create a route in the route table for the NAT Gateway
    private_route = aws.ec2.Route("nat-route",
        route_table_id=private_route_table.id,
        destination_cidr_block="0.0.0.0/0",
        nat_gateway_id=nat_gateway.id
    )

    # Associate the route table with the private subnet
    private_route_table_association = aws.ec2.RouteTableAssociation("private-route-table-association",
        subnet_id=private_subnet.id,
        route_table_id=private_route_table.id
    )

    # Export the private route table ID
    pulumi.export("privateRouteTableId", private_route_table.id)

    # Create a security group for the public instance (Bastion Server)
    public_security_group = aws.ec2.SecurityGroup("public-secgrp",
        vpc_id=vpc.id,
        description="Enable HTTP and SSH access for public instance",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=80,
                to_port=80,
                cidr_blocks=["0.0.0.0/0"]
            ),
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_blocks=["0.0.0.0/0"]
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"]
            )
        ]
    )

    # Use the specified Ubuntu 24.04 LTS AMI
    ami_id = "ami-060e277c0d4cce553"

    # Create an EC2 instance in the public subnet (Bastion Server)
    public_instance = aws.ec2.Instance("bastion-instance",
        instance_type="t2.micro",
        vpc_security_group_ids=[public_security_group.id],
        ami=ami_id,
        subnet_id=public_subnet.id,
        key_name="BastionServer",
        associate_public_ip_address=True,
        tags={"Name": "Bastion-Server"}
    )

    # Export the public instance ID and IP
    pulumi.export("publicInstanceId", public_instance.id)
    pulumi.export("publicInstanceIp", public_instance.public_ip)

    # Create a security group for the private instances allowing SSH only from the bastion server
    private_security_group = aws.ec2.SecurityGroup("private-secgrp",
        vpc_id=vpc.id,
        description="Allow SSH access from Bastion server",
        ingress=[
            aws.ec2.SecurityGroupIngressArgs(
                protocol="tcp",
                from_port=22,
                to_port=22,
                cidr_blocks=[pulumi.Output.concat(public_instance.private_ip, "/32")]
            )
        ],
        egress=[
            aws.ec2.SecurityGroupEgressArgs(
                protocol="-1",
                from_port=0,
                to_port=0,
                cidr_blocks=["0.0.0.0/0"]
            )
        ]
    )

    # Create EC2 instances in the private subnet
    private_instance1 = aws.ec2.Instance("private-instance1",
        instance_type="t2.micro",
        vpc_security_group_ids=[private_security_group.id],
        ami=ami_id,
        subnet_id=private_subnet.id,
        key_name="PrivateServer1",
        tags={"Name": "Private-server1"}
    )

    # Export the private instance 1 ID and private IP
    pulumi.export("privateInstance1Id", private_instance1.id)
    pulumi.export("privateInstance1PrivateIp", private_instance1.private_ip)

    private_instance2 = aws.ec2.Instance("private-instance2",
        instance_type="t2.micro",
        vpc_security_group_ids=[private_security_group.id],
        ami=ami_id,
        subnet_id=private_subnet.id,
        key_name="PrivateServer2",
        tags={"Name": "Private-server2"}
    )

    # Export the private instance 2 ID and private IP
    pulumi.export("privateInstance2Id", private_instance2.id)
    pulumi.export("privateInstance2PrivateIp", private_instance2.private_ip)

    private_instance3 = aws.ec2.Instance("private-instance3",
        instance_type="t2.micro",
        vpc_security_group_ids=[private_security_group.id],
        ami=ami_id,
        subnet_id=private_subnet.id,
        key_name="PrivateServer3",
        tags={"Name": "Private-server3"}
    )

    # Export the private instance 3 ID and private IP
    pulumi.export("privateInstance3Id", private_instance3.id)
    pulumi.export("privateInstance3PrivateIp", private_instance3.private_ip)
    ```

6. **Deploy the Pulumi Stack:**

    ```sh
    pulumi up
    ```
  - Review the changes and confirm by typing "yes".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-5.png)

7. Check the Pulumi output for successfull creation of the Infrastructure


## Traditional way: SSH into the private instances via Bastion server

When using the direct SSH command, you have to typically do something like this

1. **Copy the Key files from your local directory to Bastion Server:**

    ```sh
    scp -i BastionServer.pem PrivateServer1.pem PrivateServer2.pem PrivateServer3.pem privateubuntu@<bastion-public-ip>:~/.ssh/
    ```

2. **SSH into the Bastion Server to check the files:**

   ```bash
   ssh -i BastionServer.pem ubuntu@<bastion-public-ip>
   ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-6.png)

    This command will securely copy the key files into Bastion server using the bastion server key file. After copying the file make sure to set the correct file permission.

3. **Change the file permission of the key files in the bastion server:**

    ```bash
    chmod 400 PrivateServer1.pem
    chmod 400 PrivateServer2.pem
    chmod 400 PrivateServer3.pem
    ```

4. **Then, SSH from the Bastion Server to a Private Instances:**

- private-server1

   ```bash
   ssh -i ~/.ssh/PrivateServer1.pem ubuntu@<private-instance1-ip>
   ```
- private-server2

   ```bash
   ssh -i ~/.ssh/PrivateServer2.pem ubuntu@<private-instance2-ip>
   ```
- private-server3

   ```bash
   ssh -i ~/.ssh/PrivateServer3.pem ubuntu@<private-instance3-ip>
   ```
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-7.png)

### Set the hostname of the servers(Optional)

You can set the hostname of the servers by these commands:

- Bastion Server

    ```sh
    sudo hostnamectl set-hostname bastion-server
    ```
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-12.png)

- Private Server 1

    ```sh
    sudo hostnamectl set-hostname private-server1
    ```
- Private Server 2

    ```sh
    sudo hostnamectl set-hostname private-server2
    ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-13.png)


- Private Server 3

    ```sh
    sudo hostnamectl set-hostname private-server3
    ```

    You can again ssh into the servers to check if hostname is correctly setup or not.


### Issues with This Approach:

- **Repetitive Commands:** Every time you want to SSH into a private instance, you have to manually SSH into the bastion server first, then SSH into the private instance. This involves typing long commands repeatedly.
  
- **Private Key Management:** You must specify the private key with the `-i` option every time, which can be **cumbersome** if you manage multiple keys for different instances.
  
- **Multi-Hop SSH:** SSHing into private instances requires a multi-hop process, where you first connect to the bastion server and then hop to the private instances. This is not only tedious but also error-prone.

## Simplifying with an SSH Config File

You can solve these issues by configuring the `~/.ssh/config` file. This file allows you to define shortcuts and advanced SSH options, making the SSH process smoother and more efficient.

### Step 1: Set Up the SSH Config File

Create a `config` file in the `~/.ssh/` directory. Here’s an example `config` file that simplifies the SSH process for this scenario:

```sh
Host bastion
    HostName <bastion-server-ip>
    User ubuntu
    IdentityFile <path-to-your-key-file>/BastionServer.pem

Host private-server1
    HostName <private-server1-ip>
    User ubuntu
    IdentityFile <path-to-your-key-file>/PrivateServer1.pem
    ProxyJump bastion

Host private-server2
    HostName <private-server2-ip>
    User ubuntu
    IdentityFile <path-to-your-key-file>/PrivateServer2.pem
    ProxyJump bastion

Host private-server3
    HostName <private-server3-ip>
    User ubuntu
    IdentityFile <path-to-your-key-file>/PrivateServer2.pem
    ProxyJump bastion
```
![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-8.png)

**NOTE:**
- Configure the `HostName` with correct IP or DNS name.
- User is `ubuntu` by default if your have launched an ubuntu instance. Change accordingly to your requirement.
- Make sure to change the location of your key files accordingly.

#### Explanation of the Config File:

- **Host bastion:** This section defines the connection to your bastion server. The `HostName` is the public IP of the bastion server, and `IdentityFile` specifies the private key used for authentication.

- **Host private-instance-X:** These sections define the connection to each private instance. The `ProxyJump bastion` directive tells SSH to first connect to the **bastion** server before connecting to the private instance.

### Step 2: Simplified SSH Access

With the above configuration, you can now SSH into any of your instances with simple commands from your **local machine**:

- **SSH into the Bastion Server:**

  ```bash
  ssh bastion
  ```

  ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-9.png)

- **SSH into Private Server 1:**

  ```bash
  ssh private-server1
  ```

  ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-10.png)

- **SSH into Private Server 2:**

  ```bash
  ssh private-server2
  ```

- **SSH into Private Server 3:**

  ```bash
  ssh private-server3
  ```

### So, we have successfully done our SSH using ssh config file.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/SSH-Basic/images/image-11.png)

### Benefits of Using an SSH Config File

- **Streamlined Workflow:** No need to remember and type long SSH commands. Just use the server name you defined in the config file.
  
- **Multi-Hop SSH Made Easy:** The `ProxyJump` option allows for seamless SSH connections through the bastion server, making multi-hop SSH effortless.

- **Centralized Key Management:** You don’t need to specify the private key file with each command; it’s all handled by the config file.

### Security Note

- Ensure that your `~/.ssh/config` file is secure by setting appropriate permissions:

    ```bash
    chmod 600 ~/.ssh/config
    ```
    This will prevent unauthorized users from viewing or modifying your SSH configuration.

- If you want to push your project into github, make sure to write the keyfiles name in the `.gitignore` file.

### Conclusion

By using the SSH config file, you can significantly simplify and secure your SSH access to multiple instances, especially when dealing with bastion servers and private instances. This approach not only saves time but also reduces the potential for errors in your SSH workflow.