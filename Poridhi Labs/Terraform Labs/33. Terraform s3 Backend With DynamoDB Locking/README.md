
# Terraform Remote State & State Locking with S3 and DynamoDB

When managing infrastructure with Terraform, it's crucial to ensure your state file is secure and protected against concurrent modifications. Terraform's state file keeps track of all your infrastructure resources, allowing you to manage them safely across different environments. In multi-user or multi-environment projects, a remote state file and state locking are essential to prevent data corruption and race conditions.

This tutorial demonstrates how to:

- Set up **Terraform Remote State** storage in an S3 bucket.
- Enable **State Locking** using DynamoDB.
- Create an infrastructure with a VPC using Terraform modules.

![alt text](image.png)


## **Why Terraform Remote State & State Locking?**

- **Remote State** allows multiple users or systems to manage infrastructure by storing the Terraform state file in a centralized location such as an S3 bucket. This ensures that everyone has access to the latest infrastructure configuration and state, preventing issues arising from local state file conflicts. It also enables infrastructure automation across environments, providing a seamless workflow for team collaboration.
  
- **State Locking** is critical in avoiding simultaneous operations on the same infrastructure, which can lead to state file corruption and unpredictable results. By leveraging DynamoDB for state locking, Terraform ensures that only one process can modify the state file at a time, maintaining consistency and reliability during deployments and updates. This feature is especially important in CI/CD pipelines and large team environments where multiple processes might attempt to interact with the same infrastructure simultaneously.
  

## **Prerequisites**

Before you begin, ensure you have the following:

- **AWS CLI** configured with your credentials.
- **Terraform CLI** installed.
<!-- - An **SSH Key Pair** created locally for EC2 instance access.

To create an SSH key pair, run:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/web_key
```

 -->

## **Task Description**

1. **Create an S3 Bucket** to store the Terraform state file.
2. **Create a DynamoDB Table** to enable state locking.
3. **Set up Terraform Backend** configuration using S3 and DynamoDB.
4. **Create a VPC** using the Terraform module.
<!-- 5. **Launch an EC2 instance** in the VPC with SSH access. -->



## **Step-by-Step Solution**

### **Step 1: Set Up S3 for Remote State**

**File**: `s3.tf`

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "terraform-state-bucket-poridhi-lab"
}

resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}
```

This block defines the S3 bucket (`terraform_state`) that will store the Terraform state file. Versioning is enabled for safety, allowing you to roll back to previous state versions if needed.

### **Step 2: Set Up DynamoDB for State Locking**

**File**: `dynamodb.tf`

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_dynamodb_table" "state_lock_table" {
  name           = "terraform_state_lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  attribute {
    name = "LockID"
    type = "S"
  }
}
```
This block creates a DynamoDB table (`terraform_state_lock`) to manage state locking. The `LockID` attribute will act as a unique identifier for the state lock.


### **Step 3: Create and Verify S3 and DynamoDB**

1. **Initialize the Terraform project** to download the necessary modules and providers:
   ```bash
   terraform init
   ```

2. **Apply the configuration** to create the infrastructure:
   ```bash
   terraform apply
   ```

    Type `yes` to continue creating the resources.    

3. Va

### **Step 3: Configure Terraform Backend**

**File**: `backend.tf`

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "ap-southeast-1"
}

terraform {
  backend "s3" {
    bucket         = "terraform-state-bucket-poridhi-lab"
    region         = "ap-southeast-1"
    dynamodb_table = "terraform_state_lock"
    key            = "dev/ec2.tfstate"
    encrypt        = true
  }
}
```

**Explanation**:
- This block configures Terraform to use the S3 bucket for remote state storage and DynamoDB for state locking.
- The state file will be stored at `dev/ec2.tfstate` in the S3 bucket.
- The `encrypt` flag ensures the state file is encrypted at rest.

### **Step 4: Create a VPC with Terraform Module**

**File**: `vpc.tf`

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "4.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-southeast-1a"]
  public_subnets  = ["10.0.1.0/24"]

  enable_dns_hostnames    = true
  enable_dns_support      = true
  map_public_ip_on_launch = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

**Explanation**:
- This block uses the official AWS VPC module to create a VPC with a public subnet.
- DNS support and public IP mapping are enabled to allow internet access.

### **Step 5: Security Group and EC2 Instance Setup**

**File**: `ec2.tf`

```hcl
resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH traffic"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description = "SSH"
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
    Name = "ssh_access"
  }
}

resource "aws_key_pair" "web_key" {
  key_name   = "web_key"
  public_key = file("~/.ssh/web_key.pub")
}

resource "aws_instance" "terraform_state_test" {
  ami           = "ami-01811d4912b4ccb26" # Amazon Linux 2 AMI ID
  instance_type = "t2.micro"

  key_name               = aws_key_pair.web_key.key_name
  subnet_id              = module.vpc.public_subnets[0]  # Using the first public subnet from the VPC module
  vpc_security_group_ids = [aws_security_group.ssh_access.id]
  associate_public_ip_address = true

  tags = {
    Name = "terraform_state_test"
  }
}
```

**Explanation**:
- A security group (`ssh_access`) is created to allow SSH access on port 22.
- An EC2 instance is launched in the VPC using the SSH key and the public subnet created earlier.
  


## **Verification**

Once all files are created and saved in your project directory, follow these steps:

1. **Initialize the Terraform project** to download the necessary modules and providers:
   ```bash
   terraform init
   ```

2. **Apply the configuration** to create the infrastructure:
   ```bash
   terraform apply
   ```

3. **Verify the Remote State** by checking the S3 bucket. You should see a state file saved under the specified key (`dev/ec2.tfstate`).

4. **Verify State Locking** by running the `terraform apply` command in another terminal or from a different user. You should receive a message that the state is locked if one process is already running.



## **Conclusion**

In this lab, you successfully set up a remote state storage system and enabled state locking using Terraform, AWS S3, and DynamoDB. You also created an EC2 instance inside a VPC using a public subnet, allowing SSH access. By following these steps, you can now manage your Terraform state securely and collaborate in a multi-environment setup.

