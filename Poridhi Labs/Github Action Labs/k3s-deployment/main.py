import pulumi
import pulumi_aws as aws
import os


# Configuration setup
instance_type = 't2.micro'
ami = "ami-060e277c0d4cce553"


# Create a VPC
vpc = aws.ec2.Vpc(
    'k3s-cluster',
    cidr_block='10.0.0.0/16',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        'Name': 'k3s-cluster-vpc',
    }
)

# Create subnets
public_subnet = aws.ec2.Subnet('public-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.1.0/24',
    map_public_ip_on_launch=True,
    availability_zone='ap-southeast-1a',
    tags={
        'Name': 'public-subnet',
    }
)

private_subnet = aws.ec2.Subnet('private-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.2.0/24',
    map_public_ip_on_launch=False,
    availability_zone='ap-southeast-1a',
    tags={
        'Name': 'private-subnet',
    }
)

# Internet Gateway
igw = aws.ec2.InternetGateway(
    'internet-gateway',
    vpc_id=vpc.id,
    tags={
        'Name': 'k3s-cluster-igw'
    }
)

# Route Table for Public Subnet
public_route_table = aws.ec2.RouteTable(
    'public-route-table', 
    vpc_id=vpc.id,
    routes=[{
        'cidr_block': '0.0.0.0/0',
        'gateway_id': igw.id,
    }],
    tags={
        'Name': 'public-route-table',
    }
)

# Associate the public route table with the public subnet
public_route_table_association = aws.ec2.RouteTableAssociation(
    'public-route-table-association',
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)

# Elastic IP for NAT Gateway
eip = aws.ec2.Eip('nat-eip', vpc=True)

# NAT Gateway
nat_gateway = aws.ec2.NatGateway(
    'nat-gateway',
    subnet_id=public_subnet.id,
    allocation_id=eip.id,
    tags={
        'Name': 'nat-gateway',
    }
)

# Route Table for Private Subnet 
private_route_table = aws.ec2.RouteTable(
    'private-route-table', 
    vpc_id=vpc.id,
    routes=[{
        'cidr_block': '0.0.0.0/0',
        'nat_gateway_id': nat_gateway.id,
    }],
    tags={
        'Name': 'private-route-table',
    }
)

# Associate the private route table with the private subnet
private_route_table_association = aws.ec2.RouteTableAssociation(
    'private-route-table-association',
    subnet_id=private_subnet.id,
    route_table_id=private_route_table.id
)

# Security Group for allowing SSH and k3s traffic
security_group = aws.ec2.SecurityGroup("web-secgrp",
    description='Enable SSH and K3s access',
    vpc_id=vpc.id,
    ingress=[
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "protocol": "tcp",
            "from_port": 10250,
            "to_port": 10250,
            "self": True,
        },
        {
            "protocol": "udp",
            "from_port": 8472,
            "to_port": 8472,
            "self": True,
        },
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
    }],
    tags={
        'Name': 'k3s-secgrp',
    }
)

# EC2 instances
master = aws.ec2.Instance(
    'master-instance',
    instance_type=instance_type,
    ami=ami,
    subnet_id=private_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name='kubernetes',
    tags={
        'Name': 'Master Node',
    }
)


worker_instances = []
for i in range(2):
    worker = aws.ec2.Instance(
        f'worker-{i+1}',
        instance_type=instance_type,
        ami=ami,
        subnet_id=private_subnet.id,
        vpc_security_group_ids=[security_group.id],
        tags={'Name': f'k3s-worker-{i+1}'},
        key_name='kubernetes'
    )
    worker_instances.append(worker)

git_runner = aws.ec2.Instance(
    'git-runner',
    instance_type=instance_type,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[security_group.id],
    key_name='kubernetes',
    tags={
        'Name': 'git-runner',
    }
)

# Output the instance IP addresses
pulumi.export('git_runner_public_ip', git_runner.public_ip)
pulumi.export('master_private_ip', master.private_ip)
pulumi.export('worker_private_ips', [worker.private_ip for worker in worker_instances])


def create_config_file(ip_addresses):
    git_runner_ip, master_ip, *worker_ips = ip_addresses
    
    config_content = f"""Host git-runner
    HostName {git_runner_ip}
    User ubuntu
    IdentityFile ~/.ssh/kubernetes.id_rsa

Host k3s-master
    HostName {master_ip}
    User ubuntu
    IdentityFile ~/.ssh/kubernetes.id_rsa
    ProxyJump git-runner

"""
    
    for i, worker_ip in enumerate(worker_ips, 1):
        config_content += f"""Host k3s-worker-{i}
    HostName {worker_ip}
    User ubuntu
    IdentityFile ~/.ssh/kubernetes.id_rsa
    ProxyJump git-runner

"""
    
    config_path = os.path.expanduser("~/.ssh/config")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

pulumi.Output.all(
    git_runner.public_ip,
    master.private_ip,
    *[worker.private_ip for worker in worker_instances]
).apply(create_config_file)