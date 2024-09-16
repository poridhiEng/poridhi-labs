# AWS Autoscaling EC2 instance using Terraform

In this lab, you will learn how to set up Auto Scaling in AWS using Terraform. Auto Scaling is a crucial feature in AWS that automatically adjusts the number of EC2 instances in a group according to the demand. This ensures that your application can handle varying amounts of traffic without manual intervention, optimizing performance and cost.

An Auto Scaling Group (ASG) manages a collection of EC2 instances that are treated as a logical grouping for automatic scaling and management. ASGs help ensure that the correct number of Amazon EC2 instances are running to handle the load for your application.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-8.png?raw=true)

## Task Description

In this lab, you will:
1. Create a VPC in the `ap-southeast-1` region with two public subnets.
2. Set up an Internet Gateway and associate it with a route table to enable internet access for the subnets.
3. Create a security group for the Load Balancer (ALB) and the instances.
4. Generate an SSH key pair for EC2 instances using the `ssh-keygen` command.
5. Create a launch template with user data to install Apache2 and serve a basic HTML page.
6. Set up a Target Group for the Load Balancer.
7. Create an Application Load Balancer (ALB) to distribute incoming traffic.
8. Set up an Auto Scaling Group (ASG) to automatically adjust the number of instances based on demand.
9. Deploy the infrastructure using Terraform and verify the setup with a load test script.


## Project Structure

```bash
autoscaling-aws-terraform/
├── main.tf
├── variables.tf
└── outputs.tf
```
Commands to Create Project Structure:

```bash
mkdir autoscaling-aws-terraform
cd autoscaling-aws-terraform
touch main.tf variables.tf outputs.tf
```

## Step-by-Step Solution

### 1. Define Variables
The `variables.tf` file defines all the variables that will be used in the configuration, such as region, VPC CIDR block, subnet CIDR blocks, availability zones, and AMI ID.

```hcl
variable "region" {
  default = "ap-southeast-1"
}

variable "vpc_cidr" {
  default = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  default = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "availability_zones" {
  default = ["ap-southeast-1a", "ap-southeast-1b"]
}

variable "key_name" {
  default = "mykey"
}

variable "instance_type" {
  default = "t2.micro"
}

variable "ami_id" {
  default = "ami-060e277c0d4cce553"  # Ubuntu AMI
}

variable "desired_capacity" {
  default = 1
}

variable "max_size" {
  default = 4
}

variable "min_size" {
  default = 1
}
```

### 2. Set Up AWS Provider
The `main.tf` file starts by configuring the AWS provider.

```hcl
provider "aws" {
  region = var.region
}
```

### 3. Create VPC and Subnets
In the `main.tf` file create a VPC with two public subnets across different availability zones.

```hcl
resource "aws_vpc" "main_vpc" {
  cidr_block = var.vpc_cidr
}

resource "aws_subnet" "public_subnet_1" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = var.public_subnet_cidrs[0]
  availability_zone = var.availability_zones[0]
  map_public_ip_on_launch = true
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id            = aws_vpc.main_vpc.id
  cidr_block        = var.public_subnet_cidrs[1]
  availability_zone = var.availability_zones[1]
  map_public_ip_on_launch = true
}
```

### 4. Configure Internet Gateway and Route Table
Attach an Internet Gateway to the VPC and configure a route table for the public subnets.

```hcl
resource "aws_internet_gateway" "main_igw" {
  vpc_id = aws_vpc.main_vpc.id
}

resource "aws_route_table" "main_rt" {
  vpc_id = aws_vpc.main_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main_igw.id
  }
}

resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_subnet_1.id
  route_table_id = aws_route_table.main_rt.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_subnet_2.id
  route_table_id = aws_route_table.main_rt.id
}
```

### 5. Create Security Groups
Create security groups for the ALB and the instances.

```hcl
resource "aws_security_group" "alb_sg" {
  vpc_id = aws_vpc.main_vpc.id

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

resource "aws_security_group" "instance_sg" {
  vpc_id = aws_vpc.main_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

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
```

### 6. Generate SSH Key Pair
Create an SSH key pair to access the instances using the command:

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/web_key
```

Add the public key to Terraform.

```hcl
resource "aws_key_pair" "web_key" {
  key_name   = "web_key"
  public_key = file("~/.ssh/web_key.pub")
}
```

### 7. Create Launch Template
Define a launch template with user data to install Apache2.

```hcl
resource "aws_launch_template" "main_lt" {
  name_prefix   = "autoscaling-lt-"
  image_id      = var.ami_id
  instance_type = var.instance_type
  key_name      = aws_key_pair.web_key.key_name

  network_interfaces {
    security_groups = [aws_security_group.instance_sg.id]
    associate_public_ip_address = true
  }

   user_data = base64encode(<<-EOF
    #!/bin/bash
    exec > >(tee /var/log/user-data.log | logger -t user-data -s 2>/dev/console) 2>&1
    apt-get update -y
    apt-get install git -y
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
    . /.nvm/nvm.sh
    nvm install --lts
    mkdir -p /demo-website
    cd /demo-website
    git clone https://github.com/imnulhaqueruman/simple-express-server.git .
    cd simple-express-server
    npm install
    iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 3000
    npm install pm2@latest -g
    pm2 start app.js
  EOF
  )
}
```

### 8. Set Up Load Balancer and Target Group
Create a target group and Application Load Balancer.

```hcl
resource "aws_lb_target_group" "main_tg" {
  name     = "autoscaling-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main_vpc.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb" "main_alb" {
  name               = "autoscaling-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb

_target_group.main_tg.arn
  }
}
```

### 9. Create Auto Scaling Group
Set up the Auto Scaling Group to manage instance scaling.

```hcl
resource "aws_autoscaling_group" "main_asg" {
  desired_capacity     = var.desired_capacity
  max_size             = var.max_size
  min_size             = var.min_size
  vpc_zone_identifier  = [aws_subnet.public_subnet_1.id, aws_subnet.public_subnet_2.id]
  target_group_arns    = [aws_lb_target_group.main_tg.arn]
  launch_template {
    id      = aws_launch_template.main_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "autoscaling-instance"
    propagate_at_launch = true
  }
}
```

### 10. Create output variable

In the `outputs.tf` file add the following to get the VPC Id as well as the DNS name of ALB.

```hcl
output "vpc_id" {
  value = aws_vpc.main_vpc.id
}

output "alb_dns_name" {
  value = aws_lb.main_alb.dns_name
}
```

### 11. Deploy the Infrastructure
Initialize Terraform, validate the configuration, plan the deployment, and apply it.

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Expected output after apply command:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image.png?raw=true)


### 12. Verification

#### 1. Verify Load Balancer
Visit the DNS name of the ALB in your web browser and check that it displays the message:

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-1.png?raw=true)

#### 2. Verify the cerated AWS resources

You can varify the resources created by terraform by using AWS console:

- VPC:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-2.png?raw=true)

- Instance:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-3.png?raw=true)

- Launch template:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-4.png?raw=true)

- Load balancer:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-5.png?raw=true)

- Target group:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-6.png?raw=true)

- Auto scaling group:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/31.%20Autoscaling%20using%20terraform/images/image-7.png?raw=true)
    

#### 2. Verify Auto Scaling
Use a load testing tool to simulate traffic and verify that the Auto Scaling Group launches additional instances to handle the load. You can use the following code too test automatically. 

```bash
const axios = require('axios');

// Change URL according to your IPv4 DNS 
const url = 'http://autoscaling-alb-975928261.ap-southeast-1.elb.amazonaws.com/';
const numberOfRequests = 1000; // Adjust this to the desired number of requests
const concurrency = 100; // Number of concurrent requests

async function sendRequest() {
  try {
    const response = await axios.get(url);
    console.log(Status: ${response.status});
  } catch (error) {
    console.error(Error: ${error.response ? error.response.status : error.message});
  }
}

async function startLoadTest() {
  const promises = [];
  for (let i = 0; i < numberOfRequests; i++) {
    if (i % concurrency === 0) {
      // Wait for all current concurrent requests to finish
      await Promise.all(promises);
      promises.length = 0; // Clear the promises array
    }
    promises.push(sendRequest());
  }
  // Wait for any remaining promises
  await Promise.all(promises);
  console.log('Load test finished.');
}

startLoadTest();
```

## Conclusion

By completing this lab, you have successfully set up an Auto Scaling Group in AWS using Terraform. The Auto Scaling Group allows your infrastructure to scale automatically based on demand, ensuring high availability and cost-efficiency.