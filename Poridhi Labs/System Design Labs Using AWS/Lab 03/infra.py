import pulumi
import pulumi_aws as aws
import os

# Create a VPC
vpc = aws.ec2.Vpc(
    'db-cluster-vpc',
    cidr_block='10.0.0.0/16',
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={'Name': 'db-cluster-vpc'}
)

# Create two subnets in different AZs
subnet1 = aws.ec2.Subnet(
    'db-cluster-subnet-1',
    vpc_id=vpc.id,
    cidr_block='10.0.1.0/24',
    availability_zone='ap-southeast-1a',
    map_public_ip_on_launch=True,
    tags={
        'Name': 'db-cluster-subnet-1',
        'Environment': 'production'
    }
)

subnet2 = aws.ec2.Subnet(
    'db-cluster-subnet-2',
    vpc_id=vpc.id,
    cidr_block='10.0.2.0/24',
    availability_zone='ap-southeast-1b',
    map_public_ip_on_launch=True,
    tags={
        'Name': 'db-cluster-subnet-2',
        'Environment': 'production'
    }
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway(
    'db-cluster-internet-gateway',
    vpc_id=vpc.id,
    tags={'Name': 'db-cluster-internet-gateway'}
)

# Create a Route Table
route_table = aws.ec2.RouteTable(
    'db-cluster-route-table',
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            gateway_id=internet_gateway.id,
        )
    ],
    tags={'Name': 'db-cluster-route-table'}
)

# Associate the route table with both subnets
route_table_association1 = aws.ec2.RouteTableAssociation(
    'db-cluster-route-table-association-1',
    subnet_id=subnet1.id,
    route_table_id=route_table.id
)

route_table_association2 = aws.ec2.RouteTableAssociation(
    'db-cluster-route-table-association-2',
    subnet_id=subnet2.id,
    route_table_id=route_table.id
)


# Create security group for NLB
nlb_security_group = aws.ec2.SecurityGroup(
    'nlb-security-group',
    vpc_id=vpc.id,
    description="NLB security group",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=5432,
            to_port=5432,
            cidr_blocks=['10.0.0.0/16'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],
        )
    ],
    tags={
        'Name': 'nlb-security-group',
        'Environment': 'production'
    }
)

# Create a security group for the database cluster
db_security_group = aws.ec2.SecurityGroup(
    'db-cluster-security-group',
    vpc_id=vpc.id,
    description="Database cluster security group",
    ingress=[
        # PostgreSQL from vpc
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=5432,
            to_port=5432,
            cidr_blocks=['10.0.0.0/16'],
        ),
        # PostgreSQL from NLB security group
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=5432,
            to_port=5432,
            security_groups=[nlb_security_group.id],
        ),
        # SSH access
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],
        )
    ],
    tags={
        'Name': 'db-cluster-security-group',
        'Environment': 'production'
    }
)

# Create a security group for the application server
app_security_group = aws.ec2.SecurityGroup(
    'app-security-group',
    vpc_id=vpc.id,
    description="Application server security group",
    ingress=[
        # HTTP
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_blocks=['0.0.0.0/0'],
        ),
        # HTTPS
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=443,
            to_port=443,
            cidr_blocks=['0.0.0.0/0'],
        ),
        # Node.js application port
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=3000,
            to_port=3000,
            cidr_blocks=['0.0.0.0/0'],
        ),
        # SSH
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],
        )
    ],
    tags={
        'Name': 'app-security-group',
        'Environment': 'production'
    }
)

# User data script for application server
app_user_data = """#!/bin/bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL client
sudo apt-get install -y postgresql-client

# Create application directory
sudo mkdir -p /opt/db-cluster-app
sudo chown ubuntu:ubuntu /opt/db-cluster-app

# Install PM2 for process management
sudo npm install -g pm2
"""


db_user_data = """#!/bin/bash
# Update system packages
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
"""



# Create EC2 Instance for Application Server
app_server = aws.ec2.Instance(
    'app-server',
    instance_type='t2.small',
    ami='ami-01811d4912b4ccb26',
    subnet_id=subnet1.id,
    key_name="db-cluster",
    vpc_security_group_ids=[app_security_group.id],
    associate_public_ip_address=True,
    private_ip='10.0.1.30',
    user_data=app_user_data,
    tags={
        'Name': 'app-server',
        'Environment': 'production'
    }
)

# Create EC2 Instance for Master DB
master_instances = []
master = aws.ec2.Instance(
    'master-0',
    instance_type='t2.small',
    ami='ami-01811d4912b4ccb26',
    subnet_id=subnet1.id,
    key_name="db-cluster",
    vpc_security_group_ids=[db_security_group.id],
    associate_public_ip_address=True,
    private_ip='10.0.1.10',
    user_data=db_user_data,
    tags={
        'Name': 'master-0',
        'Environment': 'production',
        'AZ': 'ap-southeast-1a'
    }
)
master_instances.append(master)

# Create EC2 Instances for Replicas in the first AZ
replica_instances_1 = []
for i in range(1):
    replica = aws.ec2.Instance(
        f'replica-az-a-{i}',
        instance_type='t2.small',
        ami='ami-01811d4912b4ccb26',
        subnet_id=subnet1.id, # same subnet as master
        key_name="db-cluster",
        vpc_security_group_ids=[db_security_group.id],
        associate_public_ip_address=True,
        private_ip=f'10.0.1.2{i}',
        user_data=db_user_data,
        tags={
            'Name': f'replica-az-a-{i}',
            'Environment': 'production',
            'AZ': 'ap-southeast-1a'

        }
    )
    replica_instances_1.append(replica)

# Create EC2 Instances for Replicas in the second AZ
replica_instances_2 = []
for i in range(1):
    replica = aws.ec2.Instance(
        f'replica-az-b-{i}',
        instance_type='t2.small',
        ami='ami-01811d4912b4ccb26',
        subnet_id=subnet2.id, # different subnet as master
        key_name="db-cluster",
        vpc_security_group_ids=[db_security_group.id],
        associate_public_ip_address=True,
        private_ip=f'10.0.2.2{i}',
        user_data=db_user_data,
        tags={
            'Name': f'replica-az-b-{i}',
            'Environment': 'production',
            'AZ': 'ap-southeast-1b'
        }
    )
    replica_instances_2.append(replica)

# Create Network Load Balancer
nlb = aws.lb.LoadBalancer(
    'postgres-nlb',
    internal=True,
    load_balancer_type='network',
    subnets=[subnet1.id, subnet2.id],
    enable_cross_zone_load_balancing=True,
    name='postgres-nlb'  # Added explicit name
)

# Create target group for read replicas
read_target_group = aws.lb.TargetGroup(
    'postgres-target-group',
    port=5432,
    protocol='TCP',
    vpc_id=vpc.id,
    target_type='ip',
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        protocol='TCP',
        port=5432,
        healthy_threshold=2,
        unhealthy_threshold=2,
        interval=30,
        timeout=10
    ),
    tags={
        'Name': 'postgres-read-replicas',
        'Environment': 'production'
    }
)

# Function to create attachments
def create_attachment(name, target_id):
    return aws.lb.TargetGroupAttachment(
        name,
        target_group_arn=read_target_group.arn,
        target_id=target_id,
        port=5432
    )


# Attach master to target group using private IP
target_id = master.private_ip
attachment_name = master.tags["Name"].apply(
    lambda tag_name: f'master-tg-attachment'
)

# Create attachment using resolved values
attachment = pulumi.Output.all(target_id, attachment_name).apply(
    lambda vals: create_attachment(vals[1], vals[0])
)
# Debug output
attachment_name.apply(lambda name: pulumi.log.info(f'Creating TargetGroupAttachment with name: {name}'))


# Attach replicas to target group using private IPs
for i, replica in enumerate(replica_instances_1):
    # Use private IP instead of instance ID
    target_id = replica.private_ip
    attachment_name = replica.tags["Name"].apply(
        lambda tag_name: f'replica-{tag_name}-tg-attachment-{i}'
    )
    
    # Create attachment using resolved values
    attachment = pulumi.Output.all(target_id, attachment_name).apply(
        lambda vals: create_attachment(vals[1], vals[0])
    )
    # Debug output
    attachment_name.apply(lambda name: pulumi.log.info(f'Creating TargetGroupAttachment with name: {name}'))

# Attach replicas to target group using private IPs
for i, replica in enumerate(replica_instances_2):
    # Use private IP instead of instance ID
    target_id = replica.private_ip
    attachment_name = replica.tags["Name"].apply(
        lambda tag_name: f'replica-{tag_name}-tg-attachment-{i}'
    )
    
    # Create attachment using resolved values
    attachment = pulumi.Output.all(target_id, attachment_name).apply(
        lambda vals: create_attachment(vals[1], vals[0])
    )
    # Debug output
    attachment_name.apply(lambda name: pulumi.log.info(f'Creating TargetGroupAttachment with name: {name}'))

# Create listener for read requests
listener = aws.lb.Listener(
    'postgres-listener',
    load_balancer_arn=nlb.arn,
    port=5432,
    protocol='TCP',
    default_actions=[aws.lb.ListenerDefaultActionArgs(  # Using proper args structure
        type='forward',
        target_group_arn=read_target_group.arn,
    )]
)

# Export Public and Private IPs
master_public_ips = [master.public_ip for master in master_instances]
master_private_ips = [master.private_ip for master in master_instances]
replica_public_ips = [replica.public_ip for replica in replica_instances_1] + [replica.public_ip for replica in replica_instances_2]
replica_private_ips = [replica.private_ip for replica in replica_instances_1] + [replica.private_ip for replica in replica_instances_2]
app_server_public_ip = app_server.public_ip
app_server_private_ip = app_server.private_ip
load_balancer_dns = nlb.dns_name

# Export all the necessary information
pulumi.export('vpc_id', vpc.id)
pulumi.export('subnet1_id', subnet1.id)
pulumi.export('subnet2_id', subnet2.id)
pulumi.export('master_public_ips', master_public_ips)
pulumi.export('master_private_ips', master_private_ips)
pulumi.export('replica_public_ips', replica_public_ips)
pulumi.export('replica_private_ips', replica_private_ips)
pulumi.export('app_server_public_ip', app_server_public_ip)
pulumi.export('app_server_private_ip', app_server_private_ip)
pulumi.export('load_balancer_dns', load_balancer_dns)
pulumi.export('nlb_security_group_id', nlb_security_group.id)
pulumi.export('db_security_group_id', db_security_group.id)

# Updated create_config_file function
def create_config_file(args):
    # Split the flattened list into IPs and hostnames
    ip_list = args[:len(args)//2]
    hostname_list = args[len(args)//2:]
    
    config_content = "# PostgreSQL Cluster SSH Configuration\n\n"
    
    for hostname, ip in zip(hostname_list, ip_list):
        config_content += f"Host {hostname}\n"
        config_content += f"    HostName {ip}\n"
        config_content += f"    User ubuntu\n"
        config_content += f"    IdentityFile ~/.ssh/db-cluster.id_rsa\n"
        config_content += f"    StrictHostKeyChecking no\n\n"
    
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

# Collect all IPs and hostnames including app server
all_ips = [master.public_ip for master in master_instances] + \
          [replica.public_ip for replica in replica_instances_1] + \
          [replica.public_ip for replica in replica_instances_2] + \
          [app_server.public_ip]

all_hostnames = [master.tags["Name"] for master in master_instances] + \
                [replica.tags["Name"] for replica in replica_instances_1] + \
                [replica.tags["Name"] for replica in replica_instances_2] + \
                [app_server.tags["Name"]]

# Combine all_ips and all_hostnames into a single list of Outputs
combined_outputs = all_ips + all_hostnames

# Create the config file with the IPs
pulumi.Output.all(*combined_outputs).apply(create_config_file)