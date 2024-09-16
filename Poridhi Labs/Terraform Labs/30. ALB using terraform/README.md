

# **Application Load Balancer in AWS using Terraform**

In this lab, you will learn how to set up an Application Load Balancer (ALB) in AWS using Terraform. The ALB is a crucial component for distributing incoming application traffic across multiple targets, such as EC2 instances, in multiple availability zones. This ensures high availability, scalability, and fault tolerance for your applications.

## **What is an Application Load Balancer (ALB)?**

An Application Load Balancer (ALB) is a Layer 7 load balancer provided by AWS. It routes HTTP and HTTPS (Layer 7) traffic to targets such as EC2 instances, microservices, and containers within a VPC. ALB operates at the application layer, making routing decisions based on content. It is particularly useful for applications that require advanced routing, host-based or path-based routing, and WebSocket support.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-9.png?raw=true)


In this lab, we'll deploy an ALB to balance traffic across two web servers, ensuring that incoming requests are distributed evenly.

## **Task Description**
Set up an Application Load Balancer in AWS using Terraform to distribute traffic between two EC2 instances running a simple web server.
### **Components to be Created:**
  - VPC with public subnets.
  - Security Groups for ALB and EC2 instances.
  - EC2 instances running Apache web servers.
  - Application Load Balancer (ALB).
  - Target Group and Listener for ALB.

## **Prerequisites**

Before starting the lab, ensure the following:

1. **AWS CLI Configured:** AWS CLI should beconfigured with access credentials using the following command:

    ```bash
    `aws configure`
    ```
2. **SSH Key Pair:** Create an SSH key pair to access the EC2 instances using the following command:

    ```bash
    ssh-keygen -t rsa -b 2048 -f ~/.ssh/web_key -N ""
    ```

## **Step-by-Step Solution**

### **Step 01: Project Directory Structure**

```bash
alb-lab/
├── main.tf
├── variables.tf
├── outputs.tf
├── vpc.tf
├── ec2.tf
├── alb.tf
```

1. **Create the Project Directory**

   Create a directory for the project and navigate into it:

   ```bash
   mkdir alb-lab
   cd alb-lab
   ```

2. **Create and Edit Files**

   Create the files using the following command:
   ```bash
   touch main.tf variables.tf outputs.tf vpc.tf ec2.tf alb.tf
   ```

### **Step 02: Code and Detailed Explanation**

#### **1. `main.tf` - AWS Provider Configuration**

```hcl
provider "aws" {
  region = var.region
}
```
This file configures the AWS provider, specifying the AWS region where the resources will be deployed. The region is defined as a variable for flexibility.

#### **2. `variables.tf` - Variables Declaration**

```hcl
variable "region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}
```

This file defines variables that allow customization of the AWS region, VPC CIDR block, and public subnet CIDRs. By setting defaults, it simplifies configuration but allows flexibility for different environments.

#### **3. `vpc.tf` - VPC and Subnet Configuration**

```hcl
resource "aws_vpc" "my_vpc" {
  cidr_block = var.vpc_cidr
  
  tags = {
    Name = "MyVPC"
  }
}

resource "aws_subnet" "public_subnets" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "PublicSubnet-${count.index + 1}"
  }
}

resource "aws_internet_gateway" "my_igw" {
  vpc_id = aws_vpc.my_vpc.id
  
  tags = {
    Name = "MyIGW"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.my_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my_igw.id
  }

  tags = {
    Name = "PublicRouteTable"
  }
}

resource "aws_route_table_association" "public_subnet_routes" {
  count          = length(aws_subnet.public_subnets)
  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

data "aws_availability_zones" "available" {
  state = "available"
}
```


  - **VPC:** Creates a Virtual Private Cloud (VPC) with the specified CIDR block.
  - **Subnets:** Creates two public subnets, each in a different availability zone, defined by the `availability_zone` data source.
  - **Internet Gateway:** Attaches an Internet Gateway to the VPC, allowing communication with the internet.
  - **Route Table:** Creates a route table that directs traffic to the Internet Gateway and associates it with the public subnets.



#### **4. `ec2.tf` - EC2 Instances and Security Groups**

```hcl
resource "aws_security_group" "ec2_sg" {
  name        = "EC2SecurityGroup"
  description = "Security group for EC2 instances"
  vpc_id      = aws_vpc.my_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

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
}

resource "aws_key_pair" "web_key" {
  key_name   = "web_key"
  public_key = file("~/.ssh/web_key.pub")
}

resource "aws_instance" "web_server" {
  count                  = 2
  ami                    = "ami-060e277c0d4cce553"
  instance_type          = "t2.micro"
  subnet_id              = aws_subnet.public_subnets[count.index].id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = aws_key_pair.web_key.key_name
  associate_public_ip_address = true

  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install apache2 -y
              HOSTNAME=$(hostname)
              IP_ADDRESS=$(hostname -I | cut -d' ' -f1)
              echo "<html><head><title>Server Details</title></head><body><h1>Server Details</h1><p><strong>Hostname:</strong> $HOSTNAME</p><p><strong>IP Address:</strong> $IP_ADDRESS</p></body></html>" | tee /var/www/html/index.html
              systemctl restart apache2
              EOF

  tags = {
    Name = "WebServer-${count.index + 1}"
  }
}
```

- **Security Group:** Defines a security group for the EC2 instances, allowing SSH (port 22) and HTTP (port 80) traffic.
- **Key Pair:** Specifies the SSH key pair for accessing the EC2 instances.
- **EC2 Instances:** Launches two EC2 instances

with Apache installed, each serving a basic webpage displaying the server’s hostname and IP address. The user data script ensures Apache is installed and started on boot.

#### **5. `alb.tf` - Application Load Balancer Configuration**

```hcl
resource "aws_lb" "my_alb" {
  name               = "MyALB"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = aws_subnet.public_subnets[*].id

  tags = {
    Name = "MyALB"
  }
}

resource "aws_security_group" "alb_sg" {
  name        = "ALBSecurityGroup"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.my_vpc.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb_target_group" "web_tg" {
  name     = "WebTG"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.my_vpc.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 5
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.my_alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_tg.arn
  }
}

resource "aws_lb_target_group_attachment" "web_tg_attachment" {
  count            = length(aws_instance.web_server)
  target_group_arn = aws_lb_target_group.web_tg.arn
  target_id        = aws_instance.web_server[count.index].id
  port             = 80
}
```

- **ALB:** Creates an Application Load Balancer in the public subnets, allowing incoming HTTP traffic on port 80.
- **Security Group:** Defines a security group for the ALB, allowing incoming traffic on port 80.
- **Target Group:** Creates a target group for the EC2 instances, specifying health checks on the root path `/`.
- **Listener:** Configures the ALB to listen on port 80 and forward requests to the target group.
- **Target Group Attachment:** Attaches the EC2 instances to the ALB's target group.


#### **6. `outputs.tf` - Output Values**

```hcl
output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.my_alb.dns_name
}
```

Outputs the DNS name of the ALB, which can be used to access the load-balanced application.


## **Commands and Execution**

### 1. **Initialize Terraform**

   Run the following command to initialize Terraform, which downloads the necessary providers:

   ```bash
   terraform init
   ```

### 2. **Plan the Infrastructure**

   Execute the following command to create an execution plan. This shows you what will be created without actually deploying anything:

   ```bash
   terraform plan
   ```

### 3. **Apply the Plan**

Run the following command to deploy the infrastructure. Type `yes` when prompted:

```bash
terraform apply
```

Expected result:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image.png?raw=true)

We can see the created resources in the AWS console:

- **VPC with subnets:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-3.png?raw=true)

- **EC2 instances:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-4.png?raw=true)     

- **Target group:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-5.png?raw=true)

- **ALB:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-6.png?raw=true)

- **Public IP of EC2 instances:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-7.png?raw=true)

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-8.png?raw=true)

### 4. **Verify the ALB**

   After the deployment, Terraform will output the DNS name of the ALB. You can use this DNS name in your browser to verify that the load balancer is working and distributing traffic between the two EC2 instances.

   ```bash
   http://<ALB_DNS_NAME>
   ```

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-1.png?raw=true)

   If we reload we will get another instance:

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/30.%20ALB%20using%20terraform/images/image-2.png?raw=true)



## **Conclusion**

In this lab, we successfully set up an Application Load Balancer (ALB) in AWS using Terraform. The ALB is a powerful tool for distributing traffic across multiple EC2 instances, ensuring high availability and fault tolerance for your applications. This lab provided a basic understanding of setting up a VPC, subnets, security groups, EC2 instances, and an ALB, which forms the foundation for more complex architectures.
