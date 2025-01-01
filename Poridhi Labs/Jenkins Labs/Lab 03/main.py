import pulumi
import pulumi_aws as aws
import os
import base64


# Configuration setup
t3_small = 't3.small' # Change this to your desired instance type
t3_medium = 't3.medium'
ami = "ami-06650ca7ed78ff6fa" # Change this to your desired AMI


# Read installation scripts
with open('jenkins_install.sh', 'r') as file:
    jenkins_script = file.read()

# Create a VPC
vpc = aws.ec2.Vpc(
    'jenkins-cluster',
    cidr_block='10.0.0.0/16',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        'Name': 'Jenkins-cluster-vpc',
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

# Internet Gateway
igw = aws.ec2.InternetGateway(
    'internet-gateway',
    vpc_id=vpc.id,
    tags={
        'Name': 'jenkins-cluster-igw'
    }
)

# Route Table
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

# Route Table Association
public_route_table_association = aws.ec2.RouteTableAssociation(
    'public-route-table-association',
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)

# Security Group for Jenkins Master
jenkins_master_sg = aws.ec2.SecurityGroup("jenkins-master-sg",
    description='Jenkins Master Security Group',
    vpc_id=vpc.id,
    ingress=[
        # SSH access
        {
            "protocol": "tcp",
            "from_port": 22,
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "SSH access"
        },
        # Jenkins web interface
        {
            "protocol": "tcp",
            "from_port": 8080,
            "to_port": 8080,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "Jenkins web interface"
        },
        # Jenkins JNLP port for agent connection
        {
            "protocol": "tcp",
            "from_port": 50000,
            "to_port": 50000,
            "cidr_blocks": ["10.0.0.0/16"],
            "description": "Jenkins agent connection"
        },
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
        "description": "Allow all outbound traffic"
    }],
    tags={
        'Name': 'jenkins-master-sg',
    }
)

# Security Group for Jenkins Agent
jenkins_agent_sg = aws.ec2.SecurityGroup(
    'jenkins-agent-sg',
    description='Allow SSH and communication with Jenkins Master',
    vpc_id=vpc.id,
    ingress=[
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"], "description": "SSH access"},
        {"protocol": "tcp", "from_port": 50000, "to_port": 50000, "cidr_blocks": ["10.0.0.0/16"], "description": "JNLP communication with Master"}
    ],
    egress=[{"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"], "description": "Allow all outbound"}],
    tags={'Name': 'Jenkins Agent SG'}
)



# Create user data script for Jenkins master
jenkins_user_data = f'''#!/bin/bash
# Write installation scripts
cat > /tmp/jenkins_install.sh << 'EOL'
{jenkins_script}
EOL

# Make scripts executable
chmod +x /tmp/jenkins_install.sh

# Run installation scripts
/tmp/jenkins_install.sh
'''

# EC2 Jenkins Master
jenkins_master = aws.ec2.Instance(
    'jenkins-master-instance',
    instance_type=t3_medium,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[jenkins_master_sg.id],
    key_name='jenkins_cluster',
    user_data=jenkins_user_data,
    tags={
        'Name': 'Jenkins Master Node',
    }
)

jenkins_agent = aws.ec2.Instance(
    'jenkins-agent-instance',
    instance_type=t3_medium,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[jenkins_agent_sg.id],
    key_name='jenkins_cluster',
    tags={
        'Name': 'Jenkins Agent Node',
    }
)

# Outputs
pulumi.export('Jenkins_Master_PublicIP', jenkins_master.public_ip)
pulumi.export('Jenkins_Agent_PublicIP', jenkins_agent.public_ip)
pulumi.export('Jenkins_Master_privateIP', jenkins_master.private_ip)
pulumi.export('Jenkins_Agent_privateIP', jenkins_agent.private_ip)

def create_config_file(ip_addresses):
    jenkins_master_ip, jenkins_agent_ip = ip_addresses
    
    config_content = f"""Host jenkins-master
    HostName {jenkins_master_ip}
    User ubuntu
    IdentityFile ~/.ssh/jenkins_cluster.id_rsa

    Host agent-1
    HostName {jenkins_agent_ip}
    User ubuntu
    IdentityFile ~/.ssh/jenkins_cluster.id_rsa
    
""" 
    config_path = os.path.expanduser("~/.ssh/config")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

pulumi.Output.all(
    jenkins_master.public_ip,
    jenkins_agent.public_ip,
).apply(create_config_file)