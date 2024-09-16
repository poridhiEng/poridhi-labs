# VPC Peering Using Terraform

In this lab, we will explore how to set up a VPC peering connection between two VPCs using Terraform. VPC peering allows resources in one VPC to communicate with resources in another, which is useful for extending your network across different VPCs in the same AWS region. By the end of this lab, you will have a thorough understanding of VPC peering, including setup, configuration, and verification of the connection.

## Task Description

You are required to create two VPCs in the same AWS region and set up a VPC peering connection between them using Terraform. The lab will cover creating VPCs, subnets, Internet Gateways, route tables, security groups, EC2 instances, and establishing the VPC peering connection. Finally, you will verify the peering connection by testing connectivity between instances in the two VPCs.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-5.png?raw=true)



### Prerequisites
- AWS CLI configured
- Terraform installed
- Basic knowledge of Terraform and AWS VPCs

## Lab Workflows

- Create the First Custom VPC (App-VPC)
- Create the Second Custom VPC (DB-VPC)
- Launch EC2 Instances in both VPCs 
- Test communication between instances
- Create a VPC Peering Connection
- Verify the Peering Connection



## Step 1: Set Up the Project Directory

```bash
mkdir vpc-peering-lab
cd vpc-peering-lab
touch main.tf
```



## Step 2: Create Initial Infrastructure

In the `main.tf` file create the initial infrastructure as follows:


### Part 1: AWS Provider
```hcl
provider "aws" {
  region = "ap-southeast-1"
}
```
This sets up the AWS provider with desired region.

### Part 2: VPC 1 and its components (Subnet, Internet Gateway, Route Table, and Association)
```hcl
# Create the First Custom VPC App-VPC
resource "aws_vpc" "app_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "App-VPC"
  }
}

# Create a Public Subnet for App-VPC
resource "aws_subnet" "app_public_subnet" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "ap-southeast-1a"
  tags = {
    Name = "App_Public_Subnet"
  }
}

# Internet Gateway for App-VPC
resource "aws_internet_gateway" "app_igw" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "App-VPC_IGW"
  }
}

# Route Table for App-VPC
resource "aws_route_table" "app_route_table" {
  vpc_id = aws_vpc.app_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.app_igw.id
  }

  tags = {
    Name = "App-VPC_RouteTable"
  }
}

# Route Table Association for App-VPC
resource "aws_route_table_association" "app_route_table_assoc" {
  subnet_id      = aws_subnet.app_public_subnet.id
  route_table_id = aws_route_table.app_route_table.id
}
```

1. **VPC (`App-VPC`) Creation**: Defines a VPC with a broad IP range for hosting resources.
2. **Public Subnet**: Creates a subnet within the VPC that has internet access.
3. **Internet Gateway**: Connects the VPC to the internet.
4. **Route Table**: Directs traffic from the public subnet to the internet via the IGW.
5. **Route Table Association**: Links the public subnet to the route table for internet access.

### Part 3: VPC 2 and its components (Subnet, Route Table, and Association)
```hcl
# Create the Second Custom VPC DB-VPC
resource "aws_vpc" "db_vpc" {
  cidr_block = "10.1.0.0/16"
  tags = {
    Name = "DB-VPC"
  }
}

# Create a Private Subnet for DB-VPC
resource "aws_subnet" "db_private_subnet" {
  vpc_id            = aws_vpc.db_vpc.id
  cidr_block        = "10.1.1.0/24"
  availability_zone = "ap-southeast-1a"
  tags = {
    Name = "DB_Private_Subnet"
  }
}

# Route Table for DB-VPC
resource "aws_route_table" "db_route_table" {
  vpc_id = aws_vpc.db_vpc.id

  tags = {
    Name = "DB-VPC_RouteTable"
  }
}

# Route Table Association for DB-VPC
resource "aws_route_table_association" "db_route_table_assoc" {
  subnet_id      = aws_subnet.db_private_subnet.id
  route_table_id = aws_route_table.db_route_table.id
}
```

1. **VPC (`DB-VPC`)**: Creates a separate network (`10.1.0.0/16`) for database resources.
2. **Private Subnet**: Adds a private subnet (`10.1.1.0/24`) in `DB-VPC` for resources without internet access.
3. **Route Table**: Sets up a route table for `DB-VPC`.
4. **Route Table Association**: Associates the private subnet with the route table.

### Part 4: Security Groups for both VPC1 and VPC2
```hcl
# Security Group for allowing all traffic in App-VPC
resource "aws_security_group" "allow_all_app_vpc" {
  vpc_id      = aws_vpc.app_vpc.id
  name        = "allow_all_app_vpc"
  description = "Allow all traffic for App-VPC"

  # Allow all inbound traffic
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allows all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allows all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound SSH traffic
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group for allowing all traffic in DB-VPC
resource "aws_security_group" "allow_all_db_vpc" {
  vpc_id      = aws_vpc.db_vpc.id
  name        = "allow_all_db_vpc"
  description = "Allow all traffic for DB-VPC"

  # Allow all inbound traffic
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allows all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Allows all protocols
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow inbound SSH traffic
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```
This creates security groups for both VPCs. Here's a concise explanation for the security groups:

1. **Security Group for `App-VPC`**:
   - **Purpose**: Allows all inbound and outbound traffic within `App-VPC`, including SSH (port 22).
   - **Inbound Rules**: Allows all traffic from any IP address (`0.0.0.0/0`) and SSH traffic on port 22.
   - **Outbound Rules**: Allows all traffic to any IP address (`0.0.0.0/0`).

2. **Security Group for `DB-VPC`**:
   - **Purpose**: Allows all inbound and outbound traffic within `DB-VPC`, including SSH (port 22).
   - **Inbound Rules**: Allows all traffic from any IP address (`0.0.0.0/0`) and SSH traffic on port 22.
   - **Outbound Rules**: Allows all traffic to any IP address (`0.0.0.0/0`).

### Part 5: SSH Key Pair and EC2 Instances

```hcl
# Key Pair for EC2 Instances
resource "aws_key_pair" "deployer_key" {
  key_name   = "deployer-key"
  public_key = file("~/.ssh/deployer-key.pub")
}

# Launch an EC2 Instance in APP-VPC
resource "aws_instance" "instance_app_vpc" {
  ami                    = "ami-060e277c0d4cce553" # Example AMI ID, update to a valid one
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.app_public_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_all_app_vpc.id]  # Use App-VPC security group
  associate_public_ip_address = true  

  key_name = aws_key_pair.deployer_key.key_name  # Use the created key

  tags = {
    Name = "Instance_App_VPC"
  }
}

# Launch an EC2 Instance in DB-VPC
resource "aws_instance" "instance_db_vpc" {
  ami                    = "ami-060e277c0d4cce553" # Example AMI ID, update to a valid one
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.db_private_subnet.id
  vpc_security_group_ids = [aws_security_group.allow_all_db_vpc.id]  # Use DB-VPC security group
  associate_public_ip_address = false  # No public IP for private subnet

  key_name = aws_key_pair.deployer_key.key_name  # Use the created key

  tags = {
    Name = "Instance_DB_VPC"
  }
}
```
Here's a concise explanation for the EC2 instance setup:

1. **Key Pair**:
   - Creates an SSH key pair named `deployer-key` using a public key from `~/.ssh/deployer-key.pub`. This key is used for securely accessing EC2 instances.

2. **EC2 Instance in `App-VPC`**:
   - **AMI**: Specifies the Amazon Machine Image (AMI) to use. Update with a valid AMI ID for your region.
   - **Instance Type**: Uses `t2.micro`, which is a basic, low-cost instance type.
   - **Public IP**: Associates a public IP address for internet access.
   - **Security Group**: Applies the `allow_all_app_vpc` security group, allowing all traffic.

3. **EC2 Instance in `DB-VPC`**:
   - **AMI**: Uses the same AMI ID as the `App-VPC` instance. Update as needed.
   - **Instance Type**: Uses `t2.micro`.
   - **Public IP**: Does not associate a public IP, as it's in a private subnet.
   - **Security Group**: Applies the `allow_all_db_vpc` security group, allowing all traffic.

## Step 3: Generate SSH Key

```bash
ssh-keygen -t rsa -b 2048 -f ~/.ssh/deployer-key -N ""
```


The command `ssh-keygen -t rsa -b 2048 -f ~/.ssh/deployer-key` is used to generate a new RSA SSH key pair. In this case, it will create `deployer-key` in the `.ssh` directory in your home folder.



## Step 4: Apply Initial Configuration

```bash
terraform init
terraform apply
```

- **`terraform init`**: Prepares your Terraform environment by installing plugins and configuring the backend.
- **`terraform apply`**: Applies your configuration to create or update infrastructure resources.

Expected output:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-1.png?raw=true)

We can varify the created resources using aws console:

- **VPCs:**

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-6.png?raw=true)

- **EC2 Instances:**

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-7.png?raw=true)

## Step 5: Test Connectivity (Will Fail)

SSH into the EC2 instance in VPC1 and try to ping the instance in VPC2:

```bash
ssh -i ~/.ssh/deployer-key ubuntu@<VPC1_INSTANCE_PUBLIC_IP>
ping <VPC2_INSTANCE_PUBLIC_IP>
```

Successfully ssh into instace in APP-VPC:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image.png?raw=true)




Let's ping the DB-instance in other vpc using private IP. This will fail because there's no VPC peering connection yet:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-2.png?raw=true)

## Step 6: Add VPC Peering Configuration

Add the following to `main.tf`:

1. **VPC Peering**: Establishes a peering connection between the two VPCs.
2. **Peering Routes**: Added to each VPC's route table to enable cross-VPC communication.

```hcl
# Create a VPC Peering Connection
resource "aws_vpc_peering_connection" "vpc_peering" {
  vpc_id        = aws_vpc.app_vpc.id
  peer_vpc_id   = aws_vpc.db_vpc.id
  auto_accept   = true

  tags = {
    Name = "AppVPC-DBVPC-Peering"
  }
}

# Update Route Table in App-VPC for VPC Peering
resource "aws_route" "app_vpc_peering_route" {
  route_table_id         = aws_route_table.app_route_table.id
  destination_cidr_block = aws_vpc.db_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.vpc_peering.id
  
}
# VPC Peering Route for DB-VPC
resource "aws_route" "db_vpc_peering_route" {
  route_table_id            = aws_route_table.db_route_table.id
  destination_cidr_block    = aws_vpc.app_vpc.cidr_block
  vpc_peering_connection_id = aws_vpc_peering_connection.vpc_peering.id
}
```
We can varify the created vpc peering connection using AWS console:

- **VPC peering Connection:**

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-8.png?raw=true)


## Step 7: Apply VPC Peering Configuration

```bash
terraform apply
```
![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-3.png?raw=true)

## Step 8: Test Connectivity Again (Should Succeed)

SSH into the EC2 instance in VPC1 and try to ping the instance in VPC2 again:

```bash
ssh -i ~/.ssh/deployer-key ec2-user@<VPC1_INSTANCE_PUBLIC_IP>
ping <VPC2_INSTANCE_PUBLIC_IP>
```

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/28.%20VPC%20peering/images/image-4.png?raw=true)

This time, the ping should succeed, indicating that the VPC peering connection is working.


## Conclusion

In this lab, you learned how to set up a VPC peering connection between two VPCs using Terraform. You configured the necessary VPC components, established the peering connection, and updated the route tables to enable communication between the VPCs. Finally, you verified the connection by testing connectivity between instances in the two VPCs. This lab provides a strong foundation for understanding and implementing VPC peering in a cloud environment.







