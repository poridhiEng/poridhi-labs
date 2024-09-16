# SSH from Public Subnet Instance to Private Subnet Instance

In this lab, you will learn how to set up a Virtual Private Cloud (VPC) with both public and private subnets, launch EC2 instances in each subnet, and establish secure communication between these instances using JavaScript with Pulumi. Specifically, you will:

1. Configure AWS CLI and Pulumi.
2. Set up a VPC with a public and a private subnet.
3. Create an Internet Gateway (IGW) for the public subnet.
4. Create a NAT Gateway for the private subnet.
5. Launch an EC2 instance in the public subnet with a public IP address.
6. Launch an EC2 instance in the private subnet without a public IP address.
7. SSH into the public instance using a key pair.
8. Copy the key pair to the public instance and use it to SSH into the private instance from the public instance.

This lab will give you hands-on experience with AWS networking concepts and demonstrate how to securely access resources in a private subnet through a public subnet instance using JavaScript.

![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-1.png)

### Step 1: Configure AWS CLI

1. **Configure AWS CLI**:
   - Open Command Prompt or PowerShell and run:
     ```sh
     aws configure
     ```
   - Enter your AWS Access Key ID, Secret Access Key, default region (`us-east-1`), and default output format (`json`).

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-3.png)

### Step 2: Set Up a Pulumi Project

1. **Set Up a Pulumi Project**:
   - Create a new directory for your project and navigate into it:
     ```sh
     mkdir lab4
     cd lab4
     ```

2. **Initialize a New Pulumi Project**:
   - Run the following command to create a new Pulumi project:
     ```sh
     pulumi new aws-javascript
     ```
   - Follow the prompts to set up your project.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-4.png)

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

    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-5.png)

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
       allocationId: eip.id
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
    exports.privateInstanceIp = privateInstance.privateIp;
    ```

### Step 4: Deploy the Pulumi Stack

1. **Run Pulumi Up**:
   - Deploy the stack using:
     ```sh
     pulumi up
     ```
   - Review the changes and confirm by typing "yes".

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-2.png)

2. **Check the PULUMI outputs and resources**:
    - Goto your pulumi project dashboard and check for the outputs:
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-6.png)
    - You can also check the resources created:
    ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-7.png)


### Step 5: Access the Public Instance via SSH

1. **SSH into the Public Instance**:
   - Open a terminal and run:
     ```sh
     ssh -i MyKeyPair.pem ubuntu@<public_instance_ip>
     ```
   - Replace `<public_instance_ip>` with the public IP address of the public instance, which you can find in the Pulumi output or the AWS Management Console.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-8.png)

### Step 6: Copy the Key Pair to the Public Instance

1. **Copy the Key Pair to the Public Instance**:
   - On your local machine, run the following command to copy the key pair to the public instance:
     ```sh
     scp -i MyKeyPair.pem MyKeyPair.pem ubuntu@<public_instance_ip>:~
     ```
   - Replace `<public_instance_ip>` with the public IP address of the public instance.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-9.png)

### Step 7: SSH from the Public Instance to the Private Instance

1. **SSH into the Private Instance from the Public Instance**:
   - On the public instance, change the permissions of the copied key pair:
     ```sh
     chmod 400 MyKeyPair.pem
     ```
   - Then, SSH into the private instance:
     ```sh
     ssh -i MyKeyPair.pem ubuntu@<private_instance_ip>
     ```
   - Replace `<private_instance_ip>` with the private IP address of the private instance, which you can find in the Pulumi output or the AWS Management Console.

   ![alt text](https://github.com/Konami33/poridhi.io.intern/raw/main/PULUMI/PULUMI%20js/Lab-4/images/image-10.png)

### Summary

By following these steps, you will have set up a VPC with one public subnet and one private subnet, launched EC2 instances in both subnets, and used SSH to connect from the public subnet instance to the private subnet instance using Pulumi and AWS CLI on Windows with JavaScript.