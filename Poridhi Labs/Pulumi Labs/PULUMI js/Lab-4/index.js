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

// Create an Internet Gateway
const igw = new aws.ec2.InternetGateway("internet-gateway", {
    vpcId: vpc.id,
    tags: {
        Name: "igw"
    }
});

exports.igwId = igw.id;


// Create a route table
const publicRouteTable = new aws.ec2.RouteTable("public-route-table", {
    vpcId: vpc.id,
    tags: {
        Name: "rt-public"
    }
});

// Create a public route in the route table for the Internet Gateway
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


// Allocate an Elastic IP for the NAT Gateway
const eip = new aws.ec2.Eip("nat-eip", { vpc: true });

// Create the NAT Gateway
const natGateway = new aws.ec2.NatGateway("nat-gateway", {
    subnetId: publicSubnet.id,
    allocationId: eip.id
});

exports.natGatewayId = natGateway.id;


// Create a private route table for the private subnet
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