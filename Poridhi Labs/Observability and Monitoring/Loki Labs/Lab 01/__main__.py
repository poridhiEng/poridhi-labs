# import pulumi
# import pulumi_aws as aws
# import os

# # Create a VPC
# vpc = aws.ec2.Vpc(
#     'kubernetes-vpc',
#     cidr_block='10.0.0.0/16',
#     enable_dns_support=True,
#     enable_dns_hostnames=True,
#     tags={'Name': 'kubernetes-the-hard-way'}
# )

# # Create a subnet
# subnet = aws.ec2.Subnet(
#     'kubernetes-subnet',
#     vpc_id=vpc.id,
#     cidr_block='10.0.1.0/24',
#     map_public_ip_on_launch=True,
#     tags={'Name': 'kubernetes'}
# )

# # Create an Internet Gateway
# internet_gateway = aws.ec2.InternetGateway(
#     'kubernetes-internet-gateway',
#     vpc_id=vpc.id,
#     tags={'Name': 'kubernetes'}
# )

# # Create a Route Table
# route_table = aws.ec2.RouteTable(
#     'kubernetes-route-table',
#     vpc_id=vpc.id,
#     routes=[
#         aws.ec2.RouteTableRouteArgs(
#             cidr_block='0.0.0.0/0',
#             gateway_id=internet_gateway.id,
#         )
#     ],
#     tags={'Name': 'kubernetes'}
# )

# # Associate the route table with the subnet
# route_table_association = aws.ec2.RouteTableAssociation(
#     'kubernetes-route-table-association',
#     subnet_id=subnet.id,
#     route_table_id=route_table.id
# )

# # Create a security group with egress and ingress rules
# security_group = aws.ec2.SecurityGroup(
#     'kubernetes-security-group',
#     vpc_id=vpc.id,
#     description="Kubernetes security group",
#     ingress=[
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol='-1',
#             from_port=0,
#             to_port=0,
#             cidr_blocks=['0.0.0.0/0'],
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol='tcp',
#             from_port=22,
#             to_port=22,
#             cidr_blocks=['0.0.0.0/0'],
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol='tcp',
#             from_port=6443,
#             to_port=6443,
#             cidr_blocks=['0.0.0.0/0'],
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol='tcp',
#             from_port=443,
#             to_port=443,
#             cidr_blocks=['0.0.0.0/0'],
#         ),
#         aws.ec2.SecurityGroupIngressArgs(
#             protocol='icmp',
#             from_port=-1,
#             to_port=-1,
#             cidr_blocks=['0.0.0.0/0'],
#         ),
#     ],
#     egress=[
#         aws.ec2.SecurityGroupEgressArgs(
#             protocol='-1',  # -1 allows all protocols
#             from_port=0,
#             to_port=0,
#             cidr_blocks=['0.0.0.0/0'],  # Allow all outbound traffic
#         )
#     ],
#     tags={'Name': 'kubernetes'}
# )

# # Create EC2 Instances for Controllers
# controller_instances = []
# for i in range(1):
#     controller = aws.ec2.Instance(
#         f'controller-{i}',
#         instance_type='t2.small',
#         ami='ami-01811d4912b4ccb26',  # Update with correct Ubuntu AMI ID
#         subnet_id=subnet.id,
#         key_name="kubernetes",
#         vpc_security_group_ids=[security_group.id],
#         associate_public_ip_address=True,
#         private_ip=f'10.0.1.1{i}',
#         tags={
#             'Name': f'controller-{i}'
#         }
#     )
#     controller_instances.append(controller)

# # Create EC2 Instances for Workers
# worker_instances = []
# for i in range(2):
#     worker = aws.ec2.Instance(
#         f'worker-{i}',
#         instance_type='t2.small',
#         ami='ami-01811d4912b4ccb26',  # Update with correct Ubuntu AMI ID
#         subnet_id=subnet.id,
#         key_name="kubernetes",
#         vpc_security_group_ids=[security_group.id],
#         associate_public_ip_address=True,
#         private_ip=f'10.0.1.2{i}',
#         tags={'Name': f'worker-{i}'}
#     )
#     worker_instances.append(worker)

# # Export Public and Private IPs of Controller and Worker Instances
# controller_public_ips = [controller.public_ip for controller in controller_instances]
# controller_private_ips = [controller.private_ip for controller in controller_instances]
# worker_public_ips = [worker.public_ip for worker in worker_instances]
# worker_private_ips = [worker.private_ip for worker in worker_instances]

# pulumi.export('controller_public_ips', controller_public_ips)
# pulumi.export('controller_private_ips', controller_private_ips)
# pulumi.export('worker_public_ips', worker_public_ips)
# pulumi.export('worker_private_ips', worker_private_ips)

# # Export the VPC ID and Subnet ID for reference
# pulumi.export('vpc_id', vpc.id)
# pulumi.export('subnet_id', subnet.id)

# # create config file
# def create_config_file(ip_list):
#     # Define the hostnames for each IP address
#     hostnames = ['controller-0', 'controller-1', 'worker-0', 'worker-1']
    
#     config_content = ""
    
#     # Iterate over IP addresses and corresponding hostnames
#     for hostname, ip in zip(hostnames, ip_list):
#         config_content += f"Host {hostname}\n"
#         config_content += f"    HostName {ip}\n"
#         config_content += f"    User ubuntu\n"
#         config_content += f"    IdentityFile ~/.ssh/loki.id_rsa\n\n"
    
#     # Write the content to the SSH config file
#     config_path = os.path.expanduser("~/.ssh/config")
#     with open(config_path, "w") as config_file:
#         config_file.write(config_content)

# # Collect the IPs for all nodes
# all_ips = [controller.public_ip for controller in controller_instances] + [worker.public_ip for worker in worker_instances]

# # Create the config file with the IPs once the instances are ready
# pulumi.Output.all(*all_ips).apply(create_config_file)
