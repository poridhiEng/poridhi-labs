# AWS 3-Tier Architecture Using Terraform: A Standardized VPC Configuration


In this lab, we'll build a 3-tier architecture on AWS using Terraform by leveraging the standardized VPC configuration. This architecture is a best practice for organizing your infrastructure into three layers: public, private, and database subnets. We'll use Terraform modules to create and manage the VPC, ensuring that our infrastructure is reusable, scalable, and maintainable. This guide will provide a detailed explanation of each step and the underlying code to help you understand the entire process.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/27.%20AWS%203-tier%20architecture/images/image-4.png?raw=true)

## **Prerequisites**

- Basic understanding of AWS services (VPC, Subnets, NAT Gateway).
- Terraform installed on your local machine.
- AWS CLI configured with appropriate credentials using `aws configure` command.
- Familiarity with Terraform basics, including modules, variables, and outputs.

## **Folder and File Structure**

Before we start, let's organize our working directory to maintain clarity and order.

```plaintext
aws-3-tier-vpc/
├── generic-variables.tf
├── local-values.tf
├── vpc-variables.tf
├── vpc-module.tf
├── vpc-outputs.tf
└── terraform.tfvars

```

Use the following command to create a new directory and the required files as above:
```bash
mkdir aws-3-tier-vpc
cd aws-3-tier-vpc
touch generic-variables.tf local-values.tf vpc-variables.tf vpc-module.tf vpc-outputs.tf terraform.tfvars
```


## **Step 01: Define Generic Variables**

The first step in our standardized VPC configuration is to define the generic variables that will be used across the Terraform files.

**File: `generic-variables.tf`**

```hcl
# Input Variables

# AWS Region
variable "aws_region" {
  description = "Region where AWS Resources will be created"
  type        = string
  default     = "ap-southeast-1"
}

# Environment Variable
variable "environment" {
  description = "Environment Variable used as a prefix (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

# Business Division
variable "organization" {
  description = "Organization for organizational purposes"
  type        = string
  default     = "poridhi"
}
```

### **Explanation:**

- **aws_region:** Specifies the AWS region where the resources will be deployed. Here, we set it to `ap-southeast-1`.
- **environment:** A prefix to identify the environment (development, production, etc.). Default is `dev`.
- **business_division:** Helps to categorize resources based on the division within an organization.



## **Step 02: Define Local Values**

Local values are used to simplify and reuse expressions within the Terraform configuration.

**File: `local-values.tf`**

```hcl
# Define Local Values

# Define Local Values

locals {
  owners      = var.organization
  environment = var.environment
  name        = "${var.organization}-${var.environment}"
  common_tags = {
    Owner       = local.owners
    Environment = local.environment     
  }
}
```

### **Explanation:**

- **owners:** Derived from the `organization` variable.
- **environment:** Directly references the `environment` variable.
- **name:** Combines business division and environment to create a unique identifier.
- **common_tags:** Standardized tags that will be applied to all resources for easy management and tracking.



## **Step 03: Define VPC Input Variables**

Next, we define the input variables specifically for the VPC configuration.

**File: `vpc-variables.tf`**

```hcl
# VPC Input Variables

# VPC Name
variable "vpc_name" {
  description = "Name of the VPC"
  type        = string 
  default     = "myvpc"
}

# VPC CIDR Block
variable "vpc_cidr_block" {
  description = "CIDR Block for the VPC"
  type        = string 
  default     = "10.0.0.0/16"
}

# VPC Availability Zones
variable "vpc_availability_zones" {
  description = "List of Availability Zones"
  type        = list(string)
  default     = ["ap-southeast-1a", "ap-southeast-1b"]
}

# VPC Public Subnets
variable "vpc_public_subnets" {
  description = "CIDR Blocks for Public Subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}

# VPC Private Subnets
variable "vpc_private_subnets" {
  description = "CIDR Blocks for Private Subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24"]
}


# VPC Enable NAT Gateway (True or False) 
variable "vpc_enable_nat_gateway" {
  description = "Enable NAT Gateways for Private Subnets"
  type        = bool
  default     = true  
}

# VPC Single NAT Gateway (True or False)
variable "vpc_single_nat_gateway" {
  description = "Use a single NAT Gateway to reduce costs"
  type        = bool
  default     = true
}
```

### **Explanation:**

- **vpc_name:** The name of the VPC.
- **vpc_cidr_block:** The IP address range for the VPC.
- **vpc_availability_zones:** List of availability zones where the subnets will be created.
- **vpc_public_subnets, vpc_private_subnets:** CIDR blocks for public, private respectively.
- **vpc_enable_nat_gateway, vpc_single_nat_gateway:** Configurations for NAT Gateway to enable internet access for private subnets.



## **Step 04: Create VPC Module**

Now, we will use the Terraform AWS VPC module to create our VPC and all associated subnets and gateways.

**File: `vpc-module.tf`**

```hcl
# Create VPC Terraform Module

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.2.0"  

  # VPC Basic Details
  name             = "${local.name}-${var.vpc_name}"
  cidr             = var.vpc_cidr_block
  azs              = var.vpc_availability_zones
  public_subnets   = var.vpc_public_subnets
  private_subnets  = var.vpc_private_subnets  

  # NAT Gateways - Outbound Communication
  enable_nat_gateway = var.vpc_enable_nat_gateway 
  single_nat_gateway = var.vpc_single_nat_gateway

  # VPC DNS Parameters
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Tags
  tags     = local.common_tags
  vpc_tags = local.common_tags

  # Additional Tags for Subnets
  public_subnet_tags = {
    Type = "Public Subnets"
  }
  private_subnet_tags = {
    Type = "Private Subnets"
  }  
}
```

### **Explanation:**

- **source, version:** Specifies the module source from the Terraform Registry and locks the version to ensure stability.
- **name, cidr, azs, public_subnets, private_subnets:** These values define the VPC and its associated subnets.
- **enable_nat_gateway, single_nat_gateway:** Configures NAT Gateway settings to allow outbound internet access from private subnets.
- **enable_dns_hostnames, enable_dns_support:** Ensures that DNS resolution is enabled within the VPC.
- **tags, vpc_tags, public_subnet_tags, private_subnet_tags:** Tags to categorize and manage resources easily.



## **Step 05: Define VPC Output Values**

The final step in our Terraform configuration is to define the outputs, which will provide the essential information about the resources we created.

Certainly! Continuing from where we left off:



**File: `vpc-outputs.tf`**

```hcl
# VPC Output Values

# VPC ID
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

# Public Subnets
output "public_subnet_ids" {
  description = "List of IDs for the public subnets"
  value       = module.vpc.public_subnets
}

# Private Subnets
output "private_subnet_ids" {
  description = "List of IDs for the private subnets"
  value       = module.vpc.private_subnets
}

# NAT Gateway Public IPs
output "nat_gateway_public_ips" {
  description = "List of public Elastic IPs created for AWS NAT Gateway"
  value       = module.vpc.nat_public_ips
}

# VPC CIDR Block
output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}
```

### **Explanation:**

- **vpc_id:** Outputs the VPC ID, which is essential for referencing the VPC in other parts of the infrastructure.
- **public_subnet_ids, private_subnet_ids:** These outputs provide the IDs of the public, private, which are useful for deploying resources within specific subnets.
- **nat_gateway_ids:** Outputs the IDs of the NAT Gateways, crucial for routing traffic from private subnets to the internet.
- **vpc_cidr_block:** Outputs the CIDR block of the VPC, providing a quick reference to the IP range assigned to the VPC.



## **Step 06: Define Variable Values in `terraform.tfvars`**

The `terraform.tfvars` file allows you to set values for the variables defined earlier. This file is where you customize the configuration to fit your specific environment.

**File: `terraform.tfvars`**

```hcl
# terraform.tfvars

# AWS Region
aws_region = "ap-southeast-1"

# Environment
environment = "dev"

# Business Division
organization = "poridhi"

# VPC Specifics
vpc_name                = "myvpc"
vpc_cidr_block          = "10.0.0.0/16"
vpc_availability_zones  = ["ap-southeast-1a", "ap-southeast-1b"]
vpc_public_subnets      = ["10.0.101.0/24", "10.0.102.0/24"]
vpc_private_subnets     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24", "10.0.4.0/24"]
vpc_enable_nat_gateway  = true
vpc_single_nat_gateway  = true
```

### **Explanation:**

- **aws_region, environment, business_division:** These values are set to match your specific environment and organizational structure.
- **vpc_name, vpc_cidr_block, vpc_availability_zones:** Customizes the VPC with a specific name, CIDR block, and availability zones.
- **vpc_public_subnets, vpc_private_subnets:** Specifies the IP ranges for the subnets.
- **vpc_enable_nat_gateway, vpc_single_nat_gateway:** Enables and configures NAT Gateway settings.
- **vpc_create_database_subnet_group, vpc_create_database_subnet_route_table:** Controls whether to create database-specific resources.




## Step 07: Initialize Terraform

Once the folder structure and files are set up with the necessary code, the next step is to initialize Terraform in your project directory.

```bash
terraform init
```

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/27.%20AWS%203-tier%20architecture/images/image.png?raw=true)

This command downloads the required provider plugins and sets up the backend configuration.



## Step 08: Validate the Configuration

Before proceeding, it’s crucial to validate the configuration files to ensure there are no syntax errors or issues.

```bash
terraform validate
```

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/27.%20AWS%203-tier%20architecture/images/image-1.png?raw=true)

This command checks if the configuration is syntactically valid and internally consistent.



## Step 09: Create an Execution Plan

Now, generate an execution plan to review the resources Terraform will create or modify.

```bash
terraform plan
```

This command shows the planned actions that Terraform will take to reach the desired state as described in the configuration files.



## Step 10: Apply the Configuration

To create the VPC and related resources as described in the configuration, run the apply command:

```bash
terraform apply
```

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/27.%20AWS%203-tier%20architecture/images/image-2.png?raw=true)


This command will prompt for confirmation. You need to type `yes` for confirmation. After confirmation, Terraform will create the resources in AWS.



## Step 11: Review and Manage the Terraform State

Once the infrastructure is deployed, you can review the current state using the following command:

```bash
terraform show
```

This command displays the current state of the infrastructure as known to Terraform.

To view all resources managed by Terraform, use:

```bash
terraform state list
```

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/27.%20AWS%203-tier%20architecture/images/image-3.png?raw=true)

This command lists all the resources that are currently managed by Terraform in your state file.



## Step 12: Destroy the Infrastructure

If you need to tear down the infrastructure, use the following command:

```bash
terraform destroy
```

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/27.%20AWS%203-tier%20architecture/images/image-5.png?raw=true)

This command will destroy all the resources defined in your Terraform configuration.



This concludes the lab on setting up a standardized VPC using Terraform with detailed explanations of each step.



## **Conclusion**

By following this lab, you have successfully created a 3-tier architecture on AWS using Terraform with a standardized VPC configuration. The structure and modularity of the configuration make it easy to scale, maintain, and replicate across different environments.


