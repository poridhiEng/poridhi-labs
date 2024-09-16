import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    tags= {
     "Name": "my-vpc"
    }
)

pulumi.export("vpc_id", vpc.id)

# Create a public subnet
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="ap-southeast-1a",
    map_public_ip_on_launch=True,
    tags= {
     "Name": "public-subnet"
    }
)

pulumi.export("public_subnet_id", public_subnet.id)

# Create a private subnet
private_subnet = aws.ec2.Subnet("private-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="ap-southeast-1a",
    tags= {
     "Name": "private-subnet"
    }
)

pulumi.export("private_subnet_id", private_subnet.id)

# Create an Internet Gateway
igw = aws.ec2.InternetGateway("internet-gateway",
    vpc_id=vpc.id,
    tags= {
     "Name": "igw"
    }
)

pulumi.export("igw_id", igw.id)

# Create a route table
public_route_table = aws.ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    tags= {
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

# Allocate an Elastic IP for the NAT Gateway
eip = aws.ec2.Eip("nat-eip", vpc=True)

# Create the NAT Gateway
nat_gateway = aws.ec2.NatGateway("nat-gateway",
    subnet_id=public_subnet.id,
    allocation_id=eip.id,
    tags= {
     "Name": "nat"
    }
)

pulumi.export("nat_gateway_id", nat_gateway.id)

# Create a route table for the private subnet
private_route_table = aws.ec2.RouteTable("private-route-table",
    vpc_id=vpc.id,
    tags= {
     "Name": "rt-private"
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

# Create a security group for the public instance
public_security_group = aws.ec2.SecurityGroup("public-secgrp",
    vpc_id=vpc.id,
    description='Enable HTTP and SSH access for public instance',
    ingress=[
        {'protocol': 'tcp', 'from_port': 80, 'to_port': 80, 'cidr_blocks': ['0.0.0.0/0']},
        {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0']}
    ],
    egress=[
        {'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0']}
    ]
)

# Use the specified Ubuntu 24.04 LTS AMI
ami_id = 'ami-060e277c0d4cce553'

# Create an EC2 instance in the public subnet
public_instance = aws.ec2.Instance("public-instance",
    instance_type="t2.micro",
    vpc_security_group_ids=[public_security_group.id],
    ami=ami_id,
    subnet_id=public_subnet.id,
    key_name="MyKeyPair",
    associate_public_ip_address=True,
    tags= {
     "Name": "public-ec2"
    }
)

pulumi.export("public_instance_id", public_instance.id)
pulumi.export("public_instance_ip", public_instance.public_ip)

# Create a security group for the private instance
private_security_group = aws.ec2.SecurityGroup("private-secgrp",
    vpc_id=vpc.id,
    description='Enable SSH access for private instance',
    ingress=[
        {'protocol': 'tcp', 'from_port': 22, 'to_port': 22, 'cidr_blocks': ['0.0.0.0/0']}
    ],
    egress=[
        {'protocol': '-1', 'from_port': 0, 'to_port': 0, 'cidr_blocks': ['0.0.0.0/0']}
    ]
)

# Create an EC2 instance in the private subnet
private_instance = aws.ec2.Instance("private-instance",
    instance_type="t2.micro",
    vpc_security_group_ids=[private_security_group.id],
    ami=ami_id,
    subnet_id=private_subnet.id,
    key_name="MyKeyPair",
    tags= {
    "Name": "private-ec2"
    }
)

pulumi.export("private_instance_id", private_instance.id)




