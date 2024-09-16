## Lab 3: Launch EC2 Instances in Public and Private Subnets Using JavaScript

### Introduction

In this lab, you will extend your VPC setup by launching EC2 instances in both the public and private subnets using JavaScript with Pulumi. Specifically, you will:

1. **Create a VPC**: A dedicated virtual network for your AWS resources.
2. **Create a Public Subnet**: A subnet with Internet access via an Internet Gateway (IGW).
3. **Create a Private Subnet**: A subnet without direct Internet access.
4. **Set Up an Internet Gateway (IGW)**: Allow communication between the VPC and the Internet.
5. **Create Public and Private Route Tables**: Manage routing for the subnets.
6. **Create a NAT Gateway**: Enable instances in the private subnet to access the Internet securely.
7. **Launch an EC2 Instance in the Public Subnet**: Accessible from the Internet.
8. **Launch an EC2 Instance in the Private Subnet**: Accessible only from within the VPC.

By the end of this lab, you will have a fully functional VPC with EC2 instances in both the public and private subnets. The public instance will have direct Internet access, while the private instance will be isolated from direct Internet access, providing a secure environment for sensitive operations.

![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20js/Lab-3/images/image.jpg?raw=true)

### Step 1: Configure AWS CLI

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

![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20js/Lab-3/images/5.png?raw=true)

You will find the `AWS Access key` and `AWS Seceret Access key` on Lab description page,where you generated the credentials

![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20js/Lab-3/images/6.png?raw=true)


### Step 2: Set Up a Pulumi Project

1. **Set Up a Pulumi Project**:
   - Create a new directory for your project and navigate into it:
     ```sh
     mkdir lab3-vpc-project
     cd lab3-vpc-project
     ```

2. **Initialize a New Pulumi Project**:
   - Run the following command to create a new Pulumi project:
     ```sh
     pulumi new aws-javascript
     ```
   - Follow the prompts to set up your project.

3. **Create a Key Pair**:
   - Run the following command to create a new key pair:
     ```sh
     aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem
     ```

4. **Set File Permissions**:
   - **For Windows**: Open PowerShell and navigate to the directory where `MyKeyPair.pem` is located. Then, use the following command to set the correct permissions:
     ```powershell
     icacls MyKeyPair.pem /inheritance:r
     icacls MyKeyPair.pem /grant:r "$($env:USERNAME):(R)"
     ```

   - **For Linux**:
     ```sh
     chmod 400 MyKeyPair.pem
     ```

     ![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20js/Lab-3/images/8.jpg?raw=true)

### Step 3: Create the Pulumi Program

1. **Open `index.js`**:
   - Open the `index.js` file in your project directory.

2. **Create the VPC**:
   - A Virtual Private Cloud (VPC) is a virtual network dedicated to your AWS account. You can configure your VPC with a range of IP addresses, subnets, route tables, and network gateways.
   ```javascript
   const pulumi = require("@pulumi/pulumi");
   const aws = require("@pulumi/aws");

   // Create a VPC
   const vpc = new aws.ec2.Vpc("my-vpc", {
       cidrBlock: "10.0.0.0/16",
       tags: {
        Name: "my-vpc"
       }
   });

   exports.vpcId = vpc.id;
   ```

3. **Create the Public Subnet**:
   - A public subnet is one that has a route to an Internet Gateway, enabling instances within it to communicate with the Internet.
   ```javascript
   // Create a public subnet
   const publicSubnet = new aws.ec2.Subnet("public-subnet", {
       vpcId: vpc.id,
       cidrBlock: "10.0.1.0/24",
       availabilityZone: "ap-southeast-1a",
       mapPublicIpOnLaunch: true,
       tags: {
        Name: "public-subnet"
       }
   });

   exports.publicSubnetId = publicSubnet.id;
   ```

4. **Create the Private Subnet**:
   - A private subnet does not have a route to an Internet Gateway, preventing instances within it from directly communicating with the Internet.
   ```javascript
   // Create a private subnet
   const privateSubnet = new aws.ec2.Subnet("private-subnet", {
       vpcId: vpc.id,
       cidrBlock: "10.0.2.0/24",
       availabilityZone: "ap-southeast-1a",
       tags: {
        Name: "private-subnet"
       }
   });

   exports.privateSubnetId = privateSubnet.id;
   ```

5. **Create the Internet Gateway**:
   - An Internet Gateway (IGW) allows communication between instances in your VPC and the Internet.
   ```javascript
   // Create an Internet Gateway
   const igw = new aws.ec2.InternetGateway("internet-gateway", {
       vpcId: vpc.id,
       tags: {
        Name: "igw"
       }
   });

   exports.igwId = igw.id;
   ```

6. **Create the Public Route Table and Associate with Public Subnet**:
   - A route table contains a set of rules, called routes, that are used to determine where network traffic is directed. Here, you will create a route table, add a route to the IGW, and associate it with the public subnet.
   ```javascript
   // Create a route table
   const publicRouteTable = new aws.ec2.RouteTable("public-route-table", {
       vpcId: vpc.id,
       tags: {
        Name: "rt-public"
       }
   });

   // Create a route in the route table for the Internet Gateway
   const route = new aws.ec2.Route("igw-route", {
       routeTableId: publicRouteTable.id,
       destinationCidrBlock: "0.0.0.0/0",
       gatewayId: igw.id
   });

   // Associate the route table with the public subnet
   const routeTableAssociation = new aws.ec2.RouteTableAssociation("public-route-table-association", {
       subnetId: publicSubnet.id,
       routeTableId: publicRouteTable.id
   });

   exports.publicRouteTableId = publicRouteTable.id;
   ```

7. **Create the NAT Gateway**:
   - A NAT Gateway allows instances in a private subnet to connect to the Internet or other AWS services, but prevents the Internet from initiating connections with the instances. This is necessary for updating instances in the private subnet.
   ```javascript
   // Allocate an Elastic IP for the NAT Gateway
   const eip = new aws.ec2.Eip("nat-eip", { vpc: true });

   // Create the NAT Gateway
   const natGateway = new aws.ec2.NatGateway("nat-gateway", {
       subnetId: publicSubnet.id,
       allocationId: eip.id,
       tags: {
        Name: "nat"
       }
   });

   exports.natGatewayId = natGateway.id;
   ```

8. **Create the Private Route Table and Associate with Private Subnet**:
   - The private route table directs traffic from the private subnet to the NAT Gateway for outbound Internet access.
   ```javascript
   // Create a route table for the private subnet
   const privateRouteTable = new aws.ec2.RouteTable("private-route-table", {
       vpcId: vpc.id,
       tags: {
        Name: "rt-private"
       }
   });

   // Create a route in the route table for the NAT Gateway
   const privateRoute = new aws.ec2.Route("nat-route", {
       routeTableId: privateRouteTable.id,
       destinationCidrBlock: "0.0.0.0/0",
       natGatewayId: natGateway.id
   });

   // Associate the route table with the private subnet
   const privateRouteTableAssociation = new aws.ec2.RouteTableAssociation("private-route-table-association", {
       subnetId: privateSubnet.id,
       routeTableId: privateRouteTable.id
   });

   exports.privateRouteTableId = privateRouteTable.id;
   ```

9. **Create the EC2 Instance in Public Subnet**:
   - An Amazon EC2 instance in the public subnet will have a public IP address and can directly communicate with the Internet.
   ```javascript
   // Create a security group for the public instance
   const publicSecurityGroup = new aws.ec2.SecurityGroup("public-secgrp", {
       vpcId: vpc.id,
       description: "Enable HTTP and SSH access for public instance",
       ingress: [
           { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] },
           { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] }
       ],
       egress: [
           { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }
       ]
   });

   // Use the specified Ubuntu 24.04 LTS AMI
   const amiId = "ami-060e277c0d4cce553";

   // Create an EC2 instance in the public subnet
   const publicInstance = new aws.ec2.Instance("public-instance", {
       instanceType: "t2.micro",
       vpcSecurityGroupIds: [publicSecurityGroup.id],
       ami: amiId,
       subnetId: publicSubnet.id,
       keyName: "MyKeyPair",
       associatePublicIpAddress: true,
       tags: {
        Name: "public-ec2"
       }
   });

   exports.publicInstanceId = publicInstance.id;
   exports.publicInstanceIp = publicInstance.publicIp;
   ```

10. **Create the EC2 Instance in Private Subnet**:
    - An Amazon EC2 instance in the private subnet will not have a public IP address and cannot directly communicate with the Internet. However, it can communicate with the Internet through the NAT Gateway.
    ```javascript
    // Create a security group for the private instance
    const privateSecurityGroup = new aws.ec2.SecurityGroup("private-secgrp", {
        vpcId: vpc.id,
        description: "Enable SSH access for private instance",
        ingress: [
            { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] }
        ],
        egress: [
            { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }
        ]
    });

    // Create an EC2 instance in the private subnet
    const privateInstance = new aws.ec2.Instance("private-instance", {
        instanceType: "t2.micro",
        vpcSecurityGroupIds: [privateSecurityGroup.id],
        ami: amiId,
        subnetId: privateSubnet.id,
        keyName: "MyKeyPair",
        tags: {
        Name: "private-ec2"
        }
    });

    exports.privateInstanceId = privateInstance.id;
    ```

### Step 4: Deploy the Pulumi Stack

1. **Run Pulumi Up**:
   - Deploy the stack using:
     ```sh
     pulumi up
     ```
   - Review the changes and confirm by typing "yes".

### Step 5: Verify the Deployment

1. **Check the Outputs**:
   - After the deployment completes, you should see the exported VPC ID, public subnet ID, private subnet ID, NAT Gateway ID, and instance IDs in the output.

   ![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20js/Lab-3/images/1.png?raw=true)

2. **Verify in AWS Management Console**:
   - Go to the [AWS Management Console](https://aws.amazon.com/console/) and navigate to the VPC, Subnet, Internet Gateway, NAT Gateway, and EC2 sections to verify that the resources have been created as expected.

   ![](https://github.com/Konami33/poridhi.io.intern/blob/main/PULUMI/PULUMI%20js/Lab-3/images/res.png?raw=true)

### Summary

By following these steps, you will have set up a VPC with one public subnet, one private subnet, a public route table, a private route table, an Internet Gateway, and a NAT Gateway, and configured EC2 instances in both subnets using Pulumi and AWS CLI on Windows.