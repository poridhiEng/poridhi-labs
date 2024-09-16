# Deploying an EC2 Instance on AWS using Terraform

In this lab, you will learn how to deploy an EC2 instance on AWS using Terraform. This process will guide you through setting up an SSH key pair, creating a security group for SSH access, and deploying an EC2 instance with a basic NGINX web server. This lab assumes you can manually create a VPC, public subnet, internet gateway, and routing table in AWS.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-7.png?raw=true)


## Introduction

Terraform is an open-source infrastructure-as-code software tool that provides a consistent CLI workflow to manage hundreds of cloud services. By using Terraform, you can define cloud resources in configuration files that describe your infrastructure, and then use these files to provision, update, and version your infrastructure with ease.

In this lab, you will:

1. Configure the AWS provider in Terraform.
2. Create an SSH key pair for secure access to your EC2 instance.
3. Define and deploy an EC2 instance running Ubuntu with NGINX installed.
4. Create a security group to allow SSH access to the instance.
5. Retrieve and use the public IP address of the instance to SSH into it.

## Step 1: Configure AWS CLI

Before starting with Terraform, ensure your AWS CLI is configured. This allows Terraform to interact with your AWS account.

```bash
aws configure
```

Provide your AWS Access Key, Secret Access Key, Default Region (e.g., `ap-southeast-1`), and output format (e.g., `json`). You can get the keys from lab creadentials.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image.png?raw=true)

## Step 2: Manually Create VPC and Public Subnet for the EC2

### 1. Create VPC
- Go to AWS Acount
- Search for VPC
- Click on `Create VPC`
- Name: `my-vpc`
- CIDR block: `10.0.0.0/16`
- Create the VPC

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-2.png?raw=true)

### 2. Create Subnet
- Go to `subnets` and click on `Create Subnet`
- Select the VPC
- Name: `my-subnet`
- CIDR block: `10.0.0.0/24`

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-3.png?raw=true)

### 3. Create Internet Gateway and Configure Route Table
- Create internet gateway named `my-IG` and attach it to `my-vpc`.
- Create route table named `my-RT`
- Edit route table as follows: 

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-4.png?raw=true)

- Edit subnet association and add it to the subnet `my-subnet`

Finally, here is the required vpc configuration resource map:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-5.png?raw=true)


## Step 2: Set Up Terraform Configuration

### 1. Create a Directory for the Project

Start by creating a directory where you will store your Terraform configuration files.
```
mkdir ec2-terraform-lab
cd ec2-terraform-lab
```
Then create `main.tf` and edit the file as follows.

### 2. **Configure the AWS Provider**

Start by defining the AWS provider in Terraform. This tells Terraform which region to operate in and which AWS credentials to use.

```hcl
provider "aws" {
  region = "ap-southeast-1"
}
```

### 2. **Create an SSH Key Pair**

If you don't have an SSH key pair, generate one using the following command:
```
ssh-keygen -t rsa -b 2048 -f ~/.ssh/web_key -N ""
```

This will create two files: `web_key` (private key) and `web_key.pub` (public key) in your `.ssh` directory.

To securely access your EC2 instance, you'll need an SSH key pair. Terraform will use this key pair during the creation of your EC2 instance.

```hcl
resource "aws_key_pair" "web_key" {
  key_name   = "web_key"
  public_key = file("~/.ssh/web_key.pub")
}
```

- `key_name`: The name of the key pair.
- `public_key`: The path to your public SSH key file.

### 3. **Deploy an EC2 Instance**

Next, define the EC2 instance that will be deployed within your pre-configured VPC and Subnet. The instance will use the SSH key pair you created earlier and will have an NGINX web server installed.

```hcl
resource "aws_instance" "web_server" {
  ami           = "ami-060e277c0d4cce553"  # Ubuntu 20.04 AMI ID
  instance_type = "t2.micro"

  key_name = aws_key_pair.web_key.key_name
  subnet_id = "subnet-003b060e207b1ba24"  # Replace with your subnet ID
  vpc_security_group_ids = [aws_security_group.ssh_access.id]
  associate_public_ip_address = true  

  tags = {
    Name        = "web_server"
    Description = "An NGINX web server on Ubuntu"
  }

  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y nginx
  EOF
}
```

- `ami`: The Amazon Machine Image (AMI) ID for Ubuntu.
- `instance_type`: The type of instance to launch (`t2.micro` for a free-tier eligible instance).
- `key_name`: The SSH key pair for secure access.
- `subnet_id`: The ID of the public subnet where the instance will be deployed.
- `vpc_security_group_ids`: A list of security group IDs for the instance.
- `associate_public_ip_address`: Ensures the instance gets a public IP for SSH access.

### 4. **Create a Security Group for SSH Access**

To allow SSH access to the EC2 instance, you need to create a security group that permits incoming connections on port 22.

```hcl
resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH access from anywhere"
  vpc_id      = "vpc-04e2eb2213d6f72b5"  # Replace with your VPC ID

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

- `vpc_id`: The ID of the VPC where the security group will be created.
- `ingress`: Defines incoming rules; here, it allows SSH access from any IP address.
- `egress`: Defines outgoing rules; allows all traffic to exit.

### 5. **Output the Public IP of the EC2 Instance**

After creating the instance, you can output its public IP address, which will be used for SSH access.

```hcl
output "web_server_public_ip" {
  value = aws_instance.web_server.public_ip
}
```


Here is the final `main.tf`:

```hcl
provider "aws" {
  region = "ap-southeast-1"
}

resource "aws_key_pair" "web_key" {
  key_name   = "web_key"
  public_key = file("~/.ssh/web_key.pub")
}

resource "aws_instance" "web_server" {
  ami           = "ami-060e277c0d4cce553"
  instance_type = "t2.micro"

  key_name = aws_key_pair.web_key.key_name

  subnet_id                   = "subnet-003b060e207b1ba24"
  vpc_security_group_ids      = [aws_security_group.ssh_access.id]
  associate_public_ip_address = true  

  tags = {
    Name        = "web_server"
    Description = "An NGINX web server on Ubuntu"
  }

  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y nginx
  EOF
}

resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH access from anywhere"
  vpc_id      = "vpc-04e2eb2213d6f72b5"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

output "web_server_public_ip" {
  value = aws_instance.web_server.public_ip
}
```


## Step 3: Deploy the Infrastructure

With your Terraform configuration ready, proceed to initialize, plan, and apply it.

```bash
terraform init
terraform plan
terraform apply
```

- `terraform init`: Initializes Terraform, downloading necessary plugins.
- `terraform plan`: Previews the actions that Terraform will take.
- `terraform apply`: Executes the plan and deploys your infrastructure.

After the deployment, Terraform will output the public IP address of your EC2 instance.

We can verify that created EC2 instance from the console:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-6.png?raw=true)

## Step 4: Connect to Your EC2 Instance

Now that your EC2 instance is up and running, you can SSH into it using the provided public IP address:

```bash
ssh -i ~/.ssh/web_key ubuntu@<public-ip>
```

Replace `<public-ip>` with the actual public IP output by Terraform.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/17.%20Deploying%20an%20EC2%20Instance%20on%20AWS%20using%20Terraform/images/image-1.png?raw=true)

## Conclusion

You've successfully deployed an EC2 instance on AWS using Terraform. This lab covered configuring the AWS provider, creating an SSH key pair, defining a security group, deploying an EC2 instance, and connecting to it. This foundational setup is essential for any cloud-based infrastructure, and with Terraform, you can easily manage, update, and scale your infrastructure as needed.