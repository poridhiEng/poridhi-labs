import pulumi
import pulumi_aws as aws
import os

# Configuration setup
t3_small = 't3.small' # Change this to your desired instance type
t3_medium = 't3.medium'
ami = "ami-06650ca7ed78ff6fa" # Change this to your desired AMI

# Create a VPC
vpc = aws.ec2.Vpc(
    'jenkins-k3s',
    cidr_block='10.0.0.0/16',
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={
        'Name': 'Jenkins-k3s-vpc',
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
        'Name': 'jenkins-k3s-igw'
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
        }
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

# Security Group for k3s Master
k3s_master_sg = aws.ec2.SecurityGroup("k3s-master-sg",
    description='k3s Master Security Group',
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
        # Kubernetes API server
        {
            "protocol": "tcp",
            "from_port": 6443,
            "to_port": 6443,
            "cidr_blocks": ["10.0.0.0/16"],
            "description": "Kubernetes API server"
        },
        # etcd client port
        {
            "protocol": "tcp",
            "from_port": 2379,
            "to_port": 2380,
            "cidr_blocks": ["10.0.0.0/16"],
            "description": "etcd client and peer communication"
        },
        # Kubelet API
        {
            "protocol": "tcp",
            "from_port": 10250,
            "to_port": 10250,
            "cidr_blocks": ["10.0.0.0/16"],
            "description": "Kubelet API"
        },
        # NodePort Services
        {
            "protocol": "tcp",
            "from_port": 30000,
            "to_port": 32767,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "NodePort Services"
        }
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
        "description": "Allow all outbound traffic"
    }],
    tags={
        'Name': 'k3s-master-sg',
    }
)

# Security Group for k3s Worker
k3s_worker_sg = aws.ec2.SecurityGroup("k3s-worker-sg",
    description='k3s Worker Security Group',
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
        # Kubelet API
        {
            "protocol": "tcp",
            "from_port": 10250,
            "to_port": 10250,
            "cidr_blocks": ["10.0.0.0/16"],
            "description": "Kubelet API"
        },
        # NodePort Services
        {
            "protocol": "tcp",
            "from_port": 30000,
            "to_port": 32767,
            "cidr_blocks": ["0.0.0.0/0"],
            "description": "NodePort Services"
        },
        # Allow all traffic from k3s master
        {
            "protocol": "-1",
            "from_port": 0,
            "to_port": 0,
            "security_groups": [k3s_master_sg.id],
            "description": "Allow all traffic from k3s master"
        }
    ],
    egress=[{
        "protocol": "-1",
        "from_port": 0,
        "to_port": 0,
        "cidr_blocks": ["0.0.0.0/0"],
        "description": "Allow all outbound traffic"
    }],
    tags={
        'Name': 'k3s-worker-sg',
    }
)

# EC2 Jenkins Master
jenkins_master = aws.ec2.Instance(
    'jenkins-master-instance',
    instance_type=t3_medium,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[jenkins_master_sg.id],
    key_name='jenkins_k3s',
    tags={
        'Name': 'Jenkins Master Node',
    }
)

k3s_master = aws.ec2.Instance(
    'k3s-master-instance',
    instance_type=t3_medium,
    ami=ami,
    subnet_id=public_subnet.id,
    vpc_security_group_ids=[k3s_master_sg.id],
    key_name='jenkins_k3s',
    tags={
        'Name': 'k3s Master Node',
    }
)

# EC2 k3s workers
worker_instances = []
for i in range(2):
    worker = aws.ec2.Instance(
        f'worker-{i+1}',
        instance_type=t3_small,
        ami=ami,
        subnet_id=public_subnet.id,
        vpc_security_group_ids=[k3s_worker_sg.id],
        tags={'Name': f'k3s-worker-{i+1}'},
        key_name='jenkins_k3s'
    )
    worker_instances.append(worker)

# Outputs
pulumi.export('Jenkins_Master_PublicIP', jenkins_master.public_ip)
pulumi.export('k3s_Master_PublicIP', k3s_master.public_ip)
pulumi.export('Workers_Public_IP', [worker.public_ip for worker in worker_instances])
pulumi.export('Jenkins_Master_privateIP', jenkins_master.private_ip)
pulumi.export('k3s_Master_privateIP', k3s_master.private_ip)
pulumi.export('Workers_Private_IP', [worker.private_ip for worker in worker_instances])

def create_config_file(ip_addresses):
    jenkins_master_ip, k3s_master_ip, *worker_ips = ip_addresses
    
    config_content = f"""Host jenkins-master
    HostName {jenkins_master_ip}
    User ubuntu
    IdentityFile ~/.ssh/jenkins_k3s.id_rsa

    Host master
    HostName {k3s_master_ip}
    User ubuntu
    IdentityFile ~/.ssh/jenkins_k3s.id_rsa
    
"""
    
    for i, worker_ip in enumerate(worker_ips, 1):
        config_content += f"""Host k3s-worker-{i}
    HostName {worker_ip}
    User ubuntu
    IdentityFile ~/.ssh/jenkins_k3s.id_rsa

"""
    
    config_path = os.path.expanduser("~/.ssh/config")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

pulumi.Output.all(
    jenkins_master.public_ip,
    k3s_master.public_ip,
    *[worker.public_ip for worker in worker_instances]
).apply(create_config_file)