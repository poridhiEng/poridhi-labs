# Lab 2: VPC with Public and Private Subnets, Route Tables, IGW, and NAT Gateway

## Introduction

In this lab, you will expand your AWS VPC setup by adding both public and private subnets and configuring Internet access for the private subnet. Specifically, you will:

1. **Create a VPC**: A dedicated virtual network for your AWS resources.
2. **Create a Public Subnet**: A subnet with Internet access via an Internet Gateway (IGW).
3. **Create a Private Subnet**: A subnet without direct Internet access.
4. **Set Up an Internet Gateway (IGW)**: Allow communication between the VPC and the Internet.
5. **Create Public and Private Route Tables**: Manage routing for the subnets.
6. **Create a NAT Gateway**: Enable instances in the private subnet to access the Internet securely.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20python/lab-2/images/pulumi-diagram-new.png)

By the end of this lab, you will have a VPC with public and private subnets. The public subnet will have direct Internet access, while the private subnet will have outbound Internet access through a NAT Gateway. This setup is essential for securing resources while maintaining necessary Internet connectivity.

## Step 1: Configure AWS CLI

### 1.1 Configure AWS CLI

Open Command Prompt or PowerShell and run the following command to configure your AWS CLI with your credentials:

```sh
aws configure
```

Provide the following details when prompted:
- **AWS Access Key ID**: Your AWS access key.
- **AWS Secret Access Key**: Your AWS secret key.
- **Default region name**: The default region (e.g., `ap-southeast-1`).
- **Default output format**: The default output format (`json`).

## Step 2: Set Up a Pulumi Project

### 2.1 Create a New Directory for Your Project

Create a directory for your project and navigate into it:

```sh
mkdir lab2-vpc-project
cd lab2-vpc-project
```

### 2.2 Initialize a New Pulumi Project

Run the following command to initialize a new Pulumi project:

```sh
pulumi new aws-python
```

Follow the prompts to set up your project, including choosing a project name, description, and stack name.

## Step 3: Create the Pulumi Program

### 3.1 Open `__main__.py`

Open the `__main__.py` file in your project directory. This is where you will write the code to define your AWS infrastructure.

### 3.2 Create the VPC

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

This code creates a VPC with the CIDR block `10.0.0.0/16` and exports its ID.

### 3.3 Create the Public Subnet

Add the following code to create a public subnet:

```python
# Create a public subnet
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="ap-southeast-1a",
    map_public_ip_on_launch=True,
    tags={
        "Name": "my-public-subnet"
    }
)

pulumi.export("public_subnet_id", public_subnet.id)
```

This code creates a public subnet in the specified availability zone with the CIDR block `10.0.1.0/24`. The `map_public_ip_on_launch=True` parameter ensures that instances launched in this subnet receive a public IP address.

### 3.4 Create the Private Subnet

Add the following code to create a private subnet:

```python
# Create a private subnet
private_subnet = aws.ec2.Subnet("private-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="ap-southeast-1a",
    tags={
        "Name": "my-private-subnet"
    }
)

pulumi.export("private_subnet_id", private_subnet.id)
```

This code creates a private subnet in the specified availability zone with the CIDR block `10.0.2.0/24`. This subnet does not have a public IP address.

### 3.5 Create the Internet Gateway

Add the following code to create an Internet Gateway (IGW):

```python
# Create an Internet Gateway
igw = aws.ec2.InternetGateway("internet-gateway",
    vpc_id=vpc.id,
    tags={
        "Name": "my-internet-gateway"
    }
)

pulumi.export("igw_id", igw.id)
```

This code creates an IGW and attaches it to the VPC, allowing instances in the VPC to communicate with the Internet.

### 3.6 Create the Public Route Table and Associate with Public Subnet

Add the following code to create a route table, add a route to the IGW, and associate it with the public subnet:

```python
# Create a route table for the public subnet
public_route_table = aws.ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    tags={
        "Name": "my-public-route-table"
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

This code creates a route table, adds a route that directs all traffic (`0.0.0.0/0`) to the IGW, and associates the route table with the public subnet.

### 3.7 Create the NAT Gateway

Add the following code to create a NAT Gateway:

```python
# Allocate an Elastic IP for the NAT Gateway
eip = aws.ec2.Eip("nat-eip", vpc=True)

# Create the NAT Gateway
nat_gateway = aws.ec2.NatGateway("nat-gateway",
    subnet_id=public_subnet.id,
    allocation_id=eip.id,
    tags={
        "Name": "my-nat-gateway"
    }
)

pulumi.export("nat_gateway_id", nat_gateway.id)
```

This code allocates an Elastic IP and creates a NAT Gateway in the public subnet, enabling instances in the private subnet to access the Internet.

### 3.8 Create the Private Route Table and Associate with Private Subnet

Add the following code to create a route table for the private subnet and associate it with the private subnet:

```python
# Create a route table for the private subnet
private_route_table = aws.ec2.RouteTable("private-route-table",
    vpc_id=vpc.id,
    tags={
        "Name": "my-private-route-table"
    }
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

pulumi.export("private_route_table_id", private_route_table.id)
```

This code creates a route table, adds a route that directs all traffic (`0.0.0.0/0`) to the NAT Gateway, and associates the route table with the private subnet.

## Step 4: Deploy the Pulumi Stack

### 4.1 Run Pulumi Up

Deploy the stack using the following command:

```sh
pulumi up
```

Review the changes that Pulumi will make and confirm by typing "yes".

## Step 5: Verify the Deployment

### 5.1 Check the Outputs

After the deployment completes, you should see the exported VPC ID, public subnet ID, private subnet ID, NAT Gateway ID, and route table IDs in the output.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20python/lab-2/images/pulumi-python-01.png)

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20python/lab-2/images/pulumi-python-02.png)

You can see the resources in the pulumi stack as well in the graph view.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20python/lab-2/images/pulumi-python-03.png)

### 5.2 Verify in AWS Management Console

Go to the AWS Management Console and navigate to the VPC, Subnet, Internet Gateway, and NAT Gateway sections to verify that the resources have been created as expected.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20python/lab-2/images/pulumi-python-04.png)

You can see the resource map in the vpc to check the connection between the resources.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20python/lab-2/images/pulumi-python-05.png)

## Summary

By following these steps, you will have set up a VPC with one public subnet, one private subnet, a public route table, a private route table, an Internet Gateway, and a NAT Gateway using Pulumi and AWS CLI.