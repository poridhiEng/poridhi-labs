# Multi-Environment Infrastructure with Shared Network in Terraform

In this lab, you will learn how to use Terraform modules to manage infrastructure across multiple environments, such as development and production, while sharing a common network setup. The network resources, including VPC, subnet, route table, and internet gateway (IGW), will be created once and shared across environments. You will also create separate EC2 instances for dev and prod environments using the shared network.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/23.%20Multi-Environment%20Infrastructure%20with%20Terraform%20Modules/images/logo.png?raw=true)


## Scenario Description

Your organization requires setting up a shared network that both development and production environments will use. Each environment will have its own EC2 instances, but they will all share the same VPC, subnet, route table, and IGW. This ensures consistency and efficient resource management.

## Objectives

1. Create a shared network that is used by both development and production environments.
2. Use Terraform modules to manage network and EC2 instance resources separately.
3. Deploy EC2 instances in both development and production environments using the shared network.
4. Understand how to pass shared resources to different environments using Terraform.


## Step 1: Set Up the Project Structure

### Install AWS CLI

Before proceeding, ensure that the AWS CLI is installed on your local machine. Follow the instructions below based on your operating system:

- **Windows**:
  1. Download the AWS CLI MSI installer from the [official AWS website](https://aws.amazon.com/cli/).
  2. Run the downloaded MSI installer and follow the instructions.

- **Linux**:
  ```sh
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
  ```

#### Configure AWS CLI

After installing the AWS CLI, configure it with the necessary credentials. Run the following command and follow the prompts to configure it:

```sh
aws configure
```

- **Explanation**: This command sets up your AWS CLI with the necessary credentials, region, and output format.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/23.%20Multi-Environment%20Infrastructure%20with%20Terraform%20Modules/images/5.png?raw=true)

You will find the `AWS Access key` and `AWS Seceret Access key` on Lab description page,where you generated the credentials

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/23.%20Multi-Environment%20Infrastructure%20with%20Terraform%20Modules/images/6.png?raw=true)

### Directory Structure

Organize your Terraform project with the following directory structure:

```
terraform-projects/
├── modules/
│   ├── aws-instance/
│   └── aws-network/
├── environments/
│   ├── dev/
│   └── prod/
└── shared-network/
```

- **`modules/aws-network/`**: Contains the module for creating the network infrastructure (VPC, subnet, route table, IGW).
- **`modules/aws-instance/`**: Contains the module for creating EC2 instances.
- **`environments/dev/`** and **`environments/prod/`**: Contains the environment-specific configurations for dev and prod.
- **`shared-network/`**: Contains the configuration for creating shared network resources.

## Step 2: Create the Shared Network Module

### Define the Network Module

Navigate to the `modules/aws-network/` directory and create the Terraform configurations to manage the network resources:

**`modules/aws-network/main.tf`:**

```py
resource "aws_vpc" "main_vpc" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "${var.network_name}-vpc"
  }
}

resource "aws_subnet" "public_subnet" {
  vpc_id                   = aws_vpc.main_vpc.id
  cidr_block               = var.public_subnet_cidr
  availability_zone        = var.availability_zone
  map_public_ip_on_launch  = true
  tags = {
    Name = "${var.network_name}-subnet"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "${var.network_name}-igw"
  }
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.main_vpc.id
  tags = {
    Name = "${var.network_name}-public-rt"
  }
}

resource "aws_route_table_association" "public_rt_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

resource "aws_route" "default_route" {
  route_table_id         = aws_route_table.public_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}
```

**Explanation :**
1. **VPC Creation**: The `aws_vpc` resource creates the main VPC with a specified CIDR block.
2. **Subnet Setup**: The `aws_subnet` resource creates a public subnet within the VPC, mapped to an availability zone.
3. **Internet Gateway**: The `aws_internet_gateway` resource sets up an Internet Gateway attached to the VPC.
4. **Route Table and Association**: The `aws_route_table` and `aws_route_table_association` resources create a public route table and associate it with the subnet, allowing internet access through the gateway.

**`modules/aws-network/variables.tf`:**

```py
variable "network_name" {
  description = "The name of the network resources"
  type        = string
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "The CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "availability_zone" {
  description = "The availability zone to deploy the subnet in"
  type        = string
}
```

**`modules/aws-network/outputs.tf`:**

```py
output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main_vpc.id
}

output "subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public_subnet.id
}
```

## Step 3: Create the Shared Network Configuration

Create the shared network configuration that will be used by both dev and prod environments:

**`shared-network/main.tf`:**

```py
provider "aws" {
  region = "ap-southeast-1"
}

module "network" {
  source            = "../modules/aws-network"
  network_name      = "shared-network"
  availability_zone = "ap-southeast-1"
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "subnet_id" {
  value = module.network.subnet_id
}
```

**Explanation :**
1. **AWS Region**: Sets AWS region to `ap-southeast-1`.
2. **Network Module**: Creates shared network resources (VPC, subnet) using the `aws-network` module.

## Step 4: Modify the EC2 Instance Module

The EC2 instance module will take VPC and subnet IDs as inputs:

**`modules/aws-instance/variables.tf`:**

```py
variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "subnet_id" {
  description = "The ID of the public subnet"
  type        = string
}

variable "ami_id" {
  description = "The AMI ID for the instance"
  type        = string
}

variable "instance_type" {
  description = "The instance type"
  type        = string
}

variable "instance_name" {
  description = "The name of the instance"
  type        = string
}
```

**`modules/aws-instance/main.tf`:**

```py
resource "aws_instance" "web_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  tags = {
    Name = var.instance_name
  }

  vpc_security_group_ids = [aws_security_group.web_sg.id]
}

resource "aws_security_group" "web_sg" {
  vpc_id = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}
```

**Explanation :**
1. **EC2 Instance**: Launches an EC2 instance using the specified AMI and instance type within a given subnet.
2. **Security Group**: Creates a security group allowing SSH (port 22) access and all outbound traffic.
3. **Subnet Association**: Associates the instance with the specified subnet and security group.
4. **Instance Tagging**: Tags the instance with a specified name for identification.

## Step 5: Use the Network and Instance Modules in Environments

In the dev and prod environments, reference the shared network’s outputs and pass them to the `aws-instance` module:

**`environments/dev/main.tf`:**

```py
provider "aws" {
  region = "ap-southeast-1"
}

# Reference the shared network
data "terraform_remote_state" "network" {
  backend = "local"
  config = {
    path = "../../shared-network/terraform.tfstate"
  }
}

# Deploy the EC2 instance in the shared network
module "web_server" {
  source        = "../../modules/aws-instance"
  ami_id        = "ami-060e277c0d4cce553"
  instance_type = "t2.micro"
  instance_name = "dev-web-server"
  vpc_id        = data.terraform_remote_state.network.outputs.vpc_id
  subnet_id     = data.terraform_remote_state.network.outputs.subnet_id
}
```

**Explanation :**
Here’s a concise summary of what this Terraform code does:

1. **AWS Provider**: Configures AWS provider for the `ap-southeast-1` region.
2. **Shared Network Reference**: Fetches VPC and subnet details from a remote state file of a shared network.
3. **EC2 Instance Module**: Deploys a `t2.micro` EC2 instance named "dev-web-server" in the shared VPC and subnet using the provided AMI ID.

**`environments/prod/main.tf`:**

```py
provider "aws" {
  region = "ap-southeast-1"
}

# Reference the shared network
data "terraform_remote_state" "network" {
  backend = "local"
  config = {
    path = "../../shared-network/terraform.tfstate"
  }
}

# Deploy the EC2 instance in the shared network
module "web_server" {
  source        = "../../modules/aws-instance"
  ami_id        = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.small"
  instance_name = "prod-web-server"
  vpc_id        = data.terraform_remote_state.network.outputs.vpc_id
  subnet_id     = data.terraform_remote_state.network.outputs.subnet_id
}
```

## Step 6: Apply the Configuration

1. **First**, create the shared network:

   ```bash
   cd shared-network
   terraform init
   terraform apply
   ```


2. **Then**, deploy the EC2 instances in the dev and prod environments using the shared network:

   **For dev:**

   ```bash
   cd ../environments/dev
   terraform init
   terraform apply
   ```

   **For prod:**

   ```bash
   cd ../prod
   terraform init
   terraform apply
   ```

## Step 7: Verify the Resources

After applying the configurations, verify that the resources have been correctly created and associated with the appropriate environments.

1. **Verify the Resource Map:**
   - Confirm that the EC2 instances are using the shared VPC, subnet, route table, and IGW.

   ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/23.%20Multi-Environment%20Infrastructure%20with%20Terraform%20Modules/images/res.png?raw=true)

2. **Verify the Dev EC2 Instance:**
   - Log in to the AWS Management Console.
   - Navigate to the EC2 dashboard and verify that the "dev-web-server" instance is running.
   - Ensure it is correctly associated with the shared subnet and security group.

   ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/23.%20Multi-Environment%20Infrastructure%20with%20Terraform%20Modules/images/dev-ec2.png?raw=true)

3. **Verify the Prod EC2 Instance:**
   - In the same AWS Management Console, check the "prod-web-server" instance.
   - Confirm that it is also running and associated with the shared network resources.

   ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/23.%20Multi-Environment%20Infrastructure%20with%20Terraform%20Modules/images/prod-ec2.png?raw=true)

## Conclusion

By using this structure, the network is created once and shared between environments, avoiding duplication of network resources while allowing separate management of environment-specific EC2 instances.

