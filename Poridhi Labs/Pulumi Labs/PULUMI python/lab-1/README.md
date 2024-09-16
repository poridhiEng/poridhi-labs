# Setting Up a VPC with a Public Subnet, Route Table, and Internet Gateway Using Pulumi and AWS CLI

## Introduction

In this lab, we will set up a basic network infrastructure on AWS using a Virtual Private Cloud (VPC). A VPC is a virtual network dedicated to your AWS account, where you can launch AWS resources in a logically isolated section of the AWS Cloud. This lab will guide you through the process of creating a VPC with a public subnet, configuring the necessary components using `PULUMI python`.

The tasks include:

1. **Configuring AWS CLI and Installing Pulumi**: Set up the necessary tools to manage your AWS resources programmatically. The AWS CLI allows you to interact with AWS services from the command line, and Pulumi is an Infrastructure as Code (IaC) tool that enables you to define and manage cloud resources using familiar programming languages.
2. **Creating a VPC**: Establish a virtual network dedicated to your AWS account, providing you with control over your networking environment.
3. **Creating a Public Subnet**: Configure a subnet that can route traffic to and from the Internet via an Internet Gateway (IGW). This subnet will host resources that need to be publicly accessible.
4. **Creating an Internet Gateway (IGW)**: Enable communication between instances in your VPC and the Internet. The IGW allows your VPC to connect to the Internet.
5. **Creating a Public Route Table**: Set up a route table that routes traffic destined for the Internet to the IGW and associate it with the public subnet.

![VPC Diagram](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-1/images/image-1.png)

By the end of this lab, you will have a VPC with a public subnet that can communicate with the Internet. This setup forms the foundation for more complex network architectures, essential for running public-facing applications on AWS.

## Prerequisites

- **AWS Account**: Ensure you have an AWS account with appropriate permissions to create VPCs, subnets, and other resources.
- **Basic Knowledge**: Familiarity with AWS networking concepts (VPCs, subnets, route tables, etc.) is beneficial.

> NOTE: This lab is intended to be done in `poridhi VS Code`. So you can skip the aws cli installation, pulumi installation, and python installation steps as we these are already installed in the VS code environment.

## Step 1: Install and Configure AWS CLI

The AWS Command Line Interface (CLI) is a unified tool to manage AWS services from the command line and automate them through scripts.

### 1.1 Configure AWS CLI

After installation, configure the AWS CLI with your credentials.

Open Command Prompt or PowerShell and run the following command:

```sh
aws configure
```

Provide the following details when prompted:

- **AWS Access Key ID**: Your AWS access key ID.
- **AWS Secret Access Key**: Your AWS secret access key.
- **Default region name**: The default region for your AWS resources (e.g., `ap-southeast-1`).
- **Default output format**: The output format for AWS CLI commands (`json`, `yaml`, `text`, `table`).

![AWS Configure](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-1/images/image-2.png)

You will find the `AWS Access key` and `AWS Seceret Access key` on Lab description page,where you generated the credentials

![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20python/lab-3/images/6.png?raw=true)


## Step 2: Install Pulumi

Pulumi is an open-source infrastructure as code tool that lets you create, deploy, and manage cloud resources using programming languages like Python.

### 2.1 Install Pulumi CLI

Download and install the Pulumi CLI by following the instructions from the [Pulumi Installation Guide](https://www.pulumi.com/docs/get-started/install/).

- **Linux**: Use the installation script:

  ```sh
  curl -fsSL https://get.pulumi.com | sh
  ```

- After installation, verify the installation by running:

    ```sh
    pulumi version
    ```

## Step 3: Set Up a Pulumi Project

### 3.1 Create a New Directory for Your Project

Open your terminal and create a directory for your project. Navigate into it:

```sh
mkdir pulumi-project
cd pulumi-project
```

### 3.2 Initialize a New Pulumi Project

1. Install Python venv

    ```sh
    sudo apt update
    sudo apt install python3.8-venv
    ```

2. Initialize a new Pulumi project:

   ```sh
   pulumi new aws-python
   ```

   Follow the prompts:

   - **Project name**: Accept the default or provide a new name.
   - **Project description**: Optional description.
   - **Stack name**: Use `dev` or another name to identify this deployment.

   ![Initializing Project](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-1/images/image-5.png)

> **Note**: A stack in Pulumi represents an instance of your cloud infrastructure, which you can use for different environments like development, staging, and production.

## Step 4: Create the Pulumi Program

### 4.1 Open `__main__.py` File

Open the `__main__.py` file in your project directory. This is where you'll define your AWS infrastructure using Python code.

### 4.2 Create the VPC

Add the following code to create a VPC:

```python
import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    tags={
        "Name": "my-vpc"
    }
)
pulumi.export("vpc_id", vpc.id)
```

**Explanation**:

- **CIDR Block**: `10.0.0.0/16` defines the IP address range for the VPC.
- **Tags**: Helps identify the resource in the AWS Console.
- **pulumi.export**: Exports the VPC ID, making it visible after deployment.

### 4.3 Create the Public Subnet

Add the following code to create a public subnet:

```python
# Create a public subnet
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="ap-southeast-1a",
    map_public_ip_on_launch=True,
    tags={
        "Name": "public-subnet"
    }
)

pulumi.export("public_subnet_id", public_subnet.id)
```

**Explanation**:

- **VPC ID**: Associates the subnet with the VPC you created.
- **CIDR Block**: `10.0.1.0/24` is a subset of the VPC's CIDR block.
- **Availability Zone**: Specifies where the subnet will reside.
- **map_public_ip_on_launch**: Ensures instances receive a public IP.
- **Tags**: Helps identify the subnet.

### 4.4 Create the Internet Gateway

Add the following code to create an Internet Gateway (IGW):

```python
# Create an Internet Gateway
igw = aws.ec2.InternetGateway("internet-gateway",
    vpc_id=vpc.id,
    tags={
        "Name": "igw"
    }
)

pulumi.export("igw_id", igw.id)
```

**Explanation**:

- **Internet Gateway**: Enables communication between your VPC and the Internet.
- **VPC ID**: Attaches the IGW to your VPC.
- **Tags**: Helps identify the IGW.

### 4.5 Create the Route Table and Associate it with the Public Subnet

Add the following code to create a route table, add a route to the IGW, and associate it with the public subnet:

```python
# Create a route table
public_route_table = aws.ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    tags={
        "Name": "rt-public"
    }
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

pulumi.export("public_route_table_id", public_route_table.id)
```

**Explanation**:

- **Route Table**: Contains routes that determine where network traffic is directed.
- **Route**: Directs all outbound traffic (`0.0.0.0/0`) to the IGW.
- **Route Table Association**: Associates the route table with the public subnet.
- **Tags**: Helps identify the route table.

## Step 5: Deploy the Pulumi Stack

### 5.1 Run Pulumi Up

Deploy the stack using the following command:

```sh
pulumi up
```

Review the proposed changes carefully. Pulumi will show a preview of the resources it will create.

- **Preview**: Displays the resources to be created.
- **Confirmation**: Type "yes" to proceed with the deployment.


## Step 6: Verify the Deployment

### 6.1 Check the Outputs

After deployment, Pulumi will display the exported outputs:

- **vpc_id**
- **public_subnet_id**
- **igw_id**
- **public_route_table_id**

![Pulumi Outputs](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-1/images/image-6.png)

### 6.2 Verify in AWS Management Console

Go to the AWS Management Console to verify the resources:

- **VPCs**: Check for "my-vpc".
- **Subnets**: Look for "public-subnet" in the correct availability zone.
- **Internet Gateways**: Ensure "igw" is attached to "my-vpc".
- **Route Tables**: Verify "rt-public" has a route to the IGW.
- **Route Table Associations**: Confirm the public subnet is associated with the public route table.

![AWS Console Verification](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-1/images/image-7.png)

## Step 7: Tear Down the Deployment

It's important to clean up resources to avoid unnecessary charges.

### 7.1 Destroy the Pulumi Stack

Navigate to your project directory:

```sh
cd pulumi-project
```

Run the destroy command:

```sh
pulumi destroy
```

Confirm the destruction by typing "yes" when prompted.

![Pulumi Destroy](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20python/lab-1/images/image-8.png)

### 7.2 Remove the Stack (Optional)

If you no longer need the stack:

```sh
pulumi stack rm dev
```

> **Note**: This removes the stack's state file. Only do this if you're sure you won't need it again.

## Summary

By following these steps, you have set up a VPC with one public subnet, a public route table, and an Internet Gateway using Pulumi and AWS CLI. This basic network forms the foundation for deploying applications that need Internet access.