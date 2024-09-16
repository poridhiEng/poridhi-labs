# Lab 2: VPC with Public and Private Subnets, Route Tables, IGW, and NAT Gateway

In this lab, we will expand our AWS VPC setup by adding both public and private subnets and configuring Internet access for the private subnet. Specifically, we will:

- Create a VPC: A dedicated virtual network for your AWS resources.
- Create a Public Subnet: A subnet with Internet access via an Internet Gateway (IGW).
- Create a Private Subnet: A subnet without direct Internet access.
- Set Up an Internet Gateway (IGW): Allow communication between the VPC and the Internet.
- Create Public and Private Route Tables: Manage routing for the subnets.
- Create a NAT Gateway: Enable instances in the private subnet to access the Internet securely.


By the end of this lab, you will have a VPC with public and private subnets. The public subnet will have direct Internet access, while the private subnet will have outbound Internet access through a NAT Gateway. This setup is essential for securing resources while maintaining necessary Internet connectivity.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20js/Lab-2/images/pulumi-diagram-new.png)

## Step 1: Configure AWS CLI

### 1.1 Configure AWS CLI

Open the terminal and run the following command to configure your AWS CLI with your credentials:

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
pulumi new aws-javascript
```

Follow the prompts to set up your project, including choosing a project name, description, and stack name.

## Step 3: Create the Pulumi Program

### 3.1 Open `index.js`

Open the `index.js` file in your project directory. This is where you will write the code to define your AWS infrastructure.

### 3.2 Create the VPC

Add the following code to create a VPC:

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

This code creates a VPC with the CIDR block `10.0.0.0/16` and exports its ID.

### 3.3 Create the Public Subnet

Add the following code to create a public subnet:

```javascript
// Create a public subnet
const publicSubnet = new aws.ec2.Subnet("public-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "ap-southeast-1a",
    mapPublicIpOnLaunch: true,
    tags: {
        Name: "my-public-subnet"
    }
});

exports.publicSubnetId = publicSubnet.id;
```

This code creates a public subnet in the specified availability zone with the CIDR block `10.0.1.0/24`. The `mapPublicIpOnLaunch: true` parameter ensures that instances launched in this subnet receive a public IP address.

### 3.4 Create the Private Subnet

Add the following code to create a private subnet:

```javascript
// Create a private subnet
const privateSubnet = new aws.ec2.Subnet("private-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.2.0/24",
    availabilityZone: "ap-southeast-1a",
    tags: {
        Name: "my-private-subnet"
    }
});

exports.privateSubnetId = privateSubnet.id;
```

This code creates a private subnet in the specified availability zone with the CIDR block `10.0.2.0/24`. This subnet does not have a public IP address.

### 3.5 Create the Internet Gateway

Add the following code to create an Internet Gateway (IGW):

```javascript
// Create an Internet Gateway
const igw = new aws.ec2.InternetGateway("internet-gateway", {
    vpcId: vpc.id,
    tags: {
        Name: "my-internet-gateway"
    }
});

exports.igwId = igw.id;
```

This code creates an IGW and attaches it to the VPC, allowing instances in the VPC to communicate with the Internet.

### 3.6 Create the Public Route Table and Associate with Public Subnet

Add the following code to create a route table, add a route to the IGW, and associate it with the public subnet:

```javascript
// Create a route table for the public subnet
const publicRouteTable = new aws.ec2.RouteTable("public-route-table", {
    vpcId: vpc.id,
    tags: {
        Name: "my-public-route-table"
    }
});

// Create a route in the route table for the Internet Gateway
const route = new aws.ec2.Route("igw-route", {
    routeTableId: publicRouteTable.id,
    destinationCidrBlock: "0.0.0.0/0",
    gatewayId: igw.id,
});

// Associate the route table with the public subnet
const routeTableAssociation = new aws.ec2.RouteTableAssociation("public-route-table-association", {
    subnetId: publicSubnet.id,
    routeTableId: publicRouteTable.id,
});

exports.publicRouteTableId = publicRouteTable.id;
```

This code creates a route table, adds a route that directs all traffic (`0.0.0.0/0`) to the IGW, and associates the route table with the public subnet.

### 3.7 Create the NAT Gateway

Add the following code to create a NAT Gateway:

```javascript
// Allocate an Elastic IP for the NAT Gateway
const eip = new aws.ec2.Eip("nat-eip", {
    vpc: true,
});

// Create the NAT Gateway
const natGateway = new aws.ec2.NatGateway("nat-gateway", {
    subnetId: publicSubnet.id,
    allocationId: eip.id,
    tags: {
        Name: "my-nat-gateway"
    }
});

exports.natGatewayId = natGateway.id;
```

This code allocates an Elastic IP and creates a NAT Gateway in the public subnet, enabling instances in the private subnet to access the Internet.

### 3.8 Create the Private Route Table and Associate with Private Subnet

Add the following code to create a route table for the private subnet and associate it with the private subnet:

```javascript
// Create a route table for the private subnet
const privateRouteTable = new aws.ec2.RouteTable("private-route-table", {
    vpcId: vpc.id,
    tags: {
        Name: "my-private-route-table"
    }
});

// Create a route in the route table for the NAT Gateway
const privateRoute = new aws.ec2.Route("nat-route", {
    routeTableId: privateRouteTable.id,
    destinationCidrBlock: "0.0.0.0/0",
    natGatewayId: natGateway.id,
});

// Associate the route table with the private subnet
const privateRouteTableAssociation = new aws.ec2.RouteTableAssociation("private-route-table-association", {
    subnetId: privateSubnet.id,
    routeTableId: privateRouteTable.id,
});

exports.privateRouteTableId = privateRouteTable.id;
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

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20js/Lab-2/images/pulumi-01.png)

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20js/Lab-2/images/pulumi-02.png)

You can see the resources in the pulumi stack as well in the graph view.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20js/Lab-2/images/pulumi-03.png)

### 5.2 Verify in AWS Management Console

Go to the AWS Management Console and navigate to the VPC, Subnet, Internet Gateway, and NAT Gateway sections to verify that the resources have been created as expected.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20js/Lab-2/images/pulumi-04.png)

You can see the resource map in the vpc to check the connection between the resources.

![alt text](https://raw.githubusercontent.com/AhnafNabil/poridhi.io.intern/main/PULUMI/PULUMI%20js/Lab-2/images/pulumi-05.png)

## Summary

By following these steps, you will have set up a VPC with one public subnet, one private subnet, a public route table, a private route table, an Internet Gateway, and a NAT Gateway using Pulumi and AWS CLI.