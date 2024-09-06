import pulumi
import pulumi_aws as aws
import os

# Create a VPC
vpc = aws.ec2.Vpc("micro-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway("micro-igw",
    vpc_id=vpc.id
)

# Create a Public Subnet
subnet = aws.ec2.Subnet("micro-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True
)

# Create a route table
route_table = aws.ec2.RouteTable("micro-route-table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=internet_gateway.id,
    )]
)

# Associate the subnet with the route table
route_table_association = aws.ec2.RouteTableAssociation("micro-route-table-association",
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Security Group allowing SSH and HTTP
security_group = aws.ec2.SecurityGroup("micro-sec-group",
    vpc_id=vpc.id,
    description="Allow SSH and HTTP",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=6379,
            to_port=6382,
            cidr_blocks=['0.0.0.0/0'],  # Allow from anywhere
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=1024,
            to_port=65535,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
)

# Read the head_node_user_data.txt file. Update your path accordingly
with open('/root/code/scripts/head_node_user_data.txt', 'r') as file:
    head_node_user_data = file.read()

# Create the head node
head_node = aws.ec2.Instance('head-node',
    instance_type='t3.medium',
    ami='ami-01811d4912b4ccb26',
    vpc_security_group_ids=[security_group.id],
    subnet_id=subnet.id,
    user_data=head_node_user_data, # pass the head-node-user-data
    key_name='key-pair-poridhi-poc',
    ebs_block_devices=[
        aws.ec2.InstanceEbsBlockDeviceArgs(
            device_name="/dev/sda1",
            volume_type="gp3",
            volume_size=20,
            delete_on_termination=True,
        ),
    ],
    tags={
        'Name': 'head-node',
    }
)

# Read the worker_node_common_data.txt user. Update your path accordingly
with open('/root/code/scripts/worker_node_common_data.txt', 'r') as file:
    worker_node_common_data = file.read()


# Create worker nodes
worker_nodes = []
for i in range(2):
    worker_node_user_data = head_node.private_ip.apply(lambda ip: worker_node_common_data  + f"""
ray start --address='{ip}:6379'
""") # The private IP of the head node is passed dynamically to the worker nodes, so they can connect to the head node via Ray (ray start command).
    worker_node = aws.ec2.Instance(f'worker-node-{i+1}',
        instance_type='t3.small',
        ami='ami-01811d4912b4ccb26',
        vpc_security_group_ids=[security_group.id],
        subnet_id=subnet.id,
        user_data=worker_node_user_data, # pass the worker node user data
        key_name='key-pair-poridhi-poc',
        ebs_block_devices=[
            aws.ec2.InstanceEbsBlockDeviceArgs(
            device_name="/dev/sda1",
            volume_type="gp3",
            volume_size=20,
            delete_on_termination=True,
            ),
        ],
        tags={
            'Name': f'worker-node-{i+1}',
        }
    )
    worker_nodes.append(worker_node)

# Output the public and private IP addresses
pulumi.export('head_node_private_ip', head_node.private_ip)
pulumi.export('head_node_public_ip', head_node.public_ip)

# Export the worker node public and private ip
for i, worker_node in enumerate(worker_nodes):
    pulumi.export(f'worker_node_{i+1}_private_ip', worker_node.private_ip)
    pulumi.export(f'worker_node_{i+1}_public_ip', worker_node.public_ip)


# Create a dynamic config file for SSH access
def create_config_file(ip_list):
    # Define the hostnames for each IP address
    hostnames = ['headnode', 'worker1', 'worker2']
    
    config_content = ""
    
    # Iterate over IP addresses and corresponding hostnames
    for hostname, ip in zip(hostnames, ip_list):
        config_content += f"Host {hostname}\n"
        config_content += f"    HostName {ip}\n"
        config_content += f"    User ubuntu\n"
        config_content += f"    IdentityFile ~/.ssh/key-pair-poridhi-poc.pem\n\n"
    
    # Write the content to the SSH config file
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

# Collect the IPs for all nodes
all_ips = [head_node.public_ip] + [worker_node.public_ip for worker_node in worker_nodes]

# Create the config file with the IPs once the instances are ready
pulumi.Output.all(*all_ips).apply(create_config_file)


# Create Staging S3 bucket with unique names
staging_data_store_bucket = aws.s3.Bucket("stagingdatastorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create Feature store bucket
feature_store_bucket = aws.s3.Bucket("featurestorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create Model store bucket
model_store_bucket = aws.s3.Bucket("modelstorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Create Results store bucket
results_store_bucket = aws.s3.Bucket("resultsstorebucket-unique-name-321",
    acl="private",  # Example ACL configuration
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True,
    ),
)

# Export the names of the created buckets
pulumi.export('staging_data_store_bucket_name', staging_data_store_bucket.id)
pulumi.export('feature_store_bucket_name', feature_store_bucket.id)
pulumi.export('model_store_bucket_name', model_store_bucket.id)
pulumi.export('results_store_bucket_name', results_store_bucket.id)