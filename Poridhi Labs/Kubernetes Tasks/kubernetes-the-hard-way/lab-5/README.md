# Bootstrapping the Kubernetes Control Plane

In this lab we will bootstrap the `Kubernetes control plane` across `two compute instances` and configure it for high availability. We will configure the control plane for high availability by setting up an external `load balancer` to expose the Kubernetes API servers to remote clients. The following components will be installed on each control plane node: Kubernetes API Server, Scheduler, and Controller Manager.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/controll-1.drawio.svg)


## Pretask: Initialize AWS Infrastructure

In this setup, we will design and deploy AWS Infrastructure to support Kubernetes Cluster. The cluster will 

- Consist of `four` public instances, divided into `two` categories: **Controller nodes** and **Worker nodes**. 
- To enable connectivity and internet access to the nodes, we will create a **public route table** and attach an **internet gateway** to it. This will allow the nodes to communicate with each other and access external resources and services. 
- Finally, we will utilize Pulumi python to create and manage this AWS infrastructure.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/infra.drawio.svg)

### 1. Configure AWS CLI

```sh
aws configure
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-7.png)

### 2. Create a script to install the necessary tools:

```bash
#!/bin/bash

# Script to install jq, cfssl, cfssljson, kubectl, and python3.8-venv

# Function to check if a command exists
command_exists() {
  command -v "$1" &> /dev/null
}

echo "Updating package list..."
sudo apt-get update -y

# Install jq if not already installed
if command_exists jq; then
  echo "jq is already installed."
else
  echo "Installing jq..."
  sudo apt-get install jq -y
fi

# Download and install cfssl and cfssljson if not already installed
if command_exists cfssl && command_exists cfssljson; then
  echo "cfssl and cfssljson are already installed."
else
  echo "Installing cfssl and cfssljson..."
  wget -q --show-progress --https-only --timestamping \
    https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 \
    https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64

  chmod +x cfssl_linux-amd64 cfssljson_linux-amd64

  sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
  sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
  echo "cfssl and cfssljson installed successfully."
fi

# Download and install kubectl if not already installed
if command_exists kubectl; then
  echo "kubectl is already installed."
else
  echo "Installing kubectl..."
  curl -LO "https://dl.k8s.io/release/v1.21.0/bin/linux/amd64/kubectl"
  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
  echo "kubectl installed successfully."
fi

echo "All tools installed successfully!"
```
This script will install **jq, cfssl, cfssljson, kubectl**, and **python3.8-venv**.

**1. Now, Save the script as `install_k8s_tools.sh`**

**2. Make the script executable.**

```sh
chmod +x install_k8s_tools.sh
```
**3. Run the script:**

```sh
./install_k8s_tools.sh
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-8.png)

## Provisioning Compute Resources

**1. Create a Directory for Your Infrastructure**

```sh
mkdir k8s-infra-aws
cd k8s-infra-aws
```

**2. Install Python `venv`**

```sh
sudo apt update
sudo apt install python3.8-venv -y
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-9.png)


**3. Create a New Pulumi Project**

```sh
pulumi new aws-python
```
**4. Update the `__main.py__` file:**

```python
import pulumi
import pulumi_aws as aws
import os

# Create a VPC
vpc = aws.ec2.Vpc(
    'kubernetes-vpc',
    cidr_block='10.0.0.0/16',
    enable_dns_support=True,
    enable_dns_hostnames=True,
    tags={'Name': 'kubernetes-the-hard-way'}
)

# Create a subnet
subnet = aws.ec2.Subnet(
    'kubernetes-subnet',
    vpc_id=vpc.id,
    cidr_block='10.0.1.0/24',
    map_public_ip_on_launch=True,
    tags={'Name': 'kubernetes'}
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway(
    'kubernetes-internet-gateway',
    vpc_id=vpc.id,
    tags={'Name': 'kubernetes'}
)

# Create a Route Table
route_table = aws.ec2.RouteTable(
    'kubernetes-route-table',
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block='0.0.0.0/0',
            gateway_id=internet_gateway.id,
        )
    ],
    tags={'Name': 'kubernetes'}
)

# Associate the route table with the subnet
route_table_association = aws.ec2.RouteTableAssociation(
    'kubernetes-route-table-association',
    subnet_id=subnet.id,
    route_table_id=route_table.id
)

# Create a security group with egress and ingress rules
security_group = aws.ec2.SecurityGroup(
    'kubernetes-security-group',
    vpc_id=vpc.id,
    description="Kubernetes security group",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol='-1',
            from_port=0,
            to_port=0,
            cidr_blocks=['10.0.0.0/16', '10.200.0.0/16'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=22,
            to_port=22,
            cidr_blocks=['0.0.0.0/0'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=6443,
            to_port=6443,
            cidr_blocks=['0.0.0.0/0'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='tcp',
            from_port=443,
            to_port=443,
            cidr_blocks=['0.0.0.0/0'],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol='icmp',
            from_port=-1,
            to_port=-1,
            cidr_blocks=['0.0.0.0/0'],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol='-1',  # -1 allows all protocols
            from_port=0,
            to_port=0,
            cidr_blocks=['0.0.0.0/0'],  # Allow all outbound traffic
        )
    ],
    tags={'Name': 'kubernetes'}
)

# Create EC2 Instances for Controllers
controller_instances = []
for i in range(2):
    controller = aws.ec2.Instance(
        f'controller-{i}',
        instance_type='t2.small',
        ami='ami-01811d4912b4ccb26',  # Update with correct Ubuntu AMI ID
        subnet_id=subnet.id,
        key_name="kubernetes",
        vpc_security_group_ids=[security_group.id],
        associate_public_ip_address=True,
        private_ip=f'10.0.1.1{i}',
        tags={
            'Name': f'controller-{i}'
        }
    )
    controller_instances.append(controller)

# Create EC2 Instances for Workers
worker_instances = []
for i in range(2):
    worker = aws.ec2.Instance(
        f'worker-{i}',
        instance_type='t2.small',
        ami='ami-01811d4912b4ccb26',  # Update with correct Ubuntu AMI ID
        subnet_id=subnet.id,
        key_name="kubernetes",
        vpc_security_group_ids=[security_group.id],
        associate_public_ip_address=True,
        private_ip=f'10.0.1.2{i}',
        tags={'Name': f'worker-{i}'}
    )
    worker_instances.append(worker)

# Create a Network Load Balancer
nlb = aws.lb.LoadBalancer(
    'kubernetes-nlb',
    internal=False,
    load_balancer_type='network',
    subnets=[subnet.id],
    name='kubernetes'
)

# Create a Target Group for the Load Balancer
target_group = aws.lb.TargetGroup(
    'kubernetes-target-group',
    port=6443,
    protocol='TCP',
    vpc_id=vpc.id,
    target_type='ip',
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        protocol='TCP',
    )
)

# Register Instances in Target Group
def create_attachment(name, target_id):
    return aws.lb.TargetGroupAttachment(
        name,
        target_group_arn=target_group.arn,
        target_id=target_id,
        port=6443
    )

# Iterate over controller instances and create TargetGroupAttachment
for i, instance in enumerate(controller_instances):
    # Use `apply` to get the resolved values of `instance.private_ip` and `instance.tags["Name"]`
    target_id = instance.private_ip
    attachment_name = instance.tags["Name"].apply(lambda tag_name: f'controller-{tag_name}-tg-attachment-{i}')
    
    # Ensure that `name` and `target_id` are resolved before creating the resource
    attachment = pulumi.Output.all(target_id, attachment_name).apply(lambda vals: create_attachment(vals[1], vals[0]))

    # Debug output
    pulumi.log.info(f'Creating TargetGroupAttachment with name: {attachment_name}')

# Create a Listener for the Load Balancer
listener = aws.lb.Listener(
    'kubernetes-listener',
    load_balancer_arn=nlb.arn,
    port=443,
    protocol='TCP',
    default_actions=[aws.lb.ListenerDefaultActionArgs(
        type='forward',
        target_group_arn=target_group.arn,
    )]
)

# Export Public DNS Name of the NLB
pulumi.export('kubernetes_public_address', nlb.dns_name)

# Export Public and Private IPs of Controller and Worker Instances
controller_public_ips = [controller.public_ip for controller in controller_instances]
controller_private_ips = [controller.private_ip for controller in controller_instances]
worker_public_ips = [worker.public_ip for worker in worker_instances]
worker_private_ips = [worker.private_ip for worker in worker_instances]

pulumi.export('controller_public_ips', controller_public_ips)
pulumi.export('controller_private_ips', controller_private_ips)
pulumi.export('worker_public_ips', worker_public_ips)
pulumi.export('worker_private_ips', worker_private_ips)

# Export the VPC ID and Subnet ID for reference
pulumi.export('vpc_id', vpc.id)
pulumi.export('subnet_id', subnet.id)

# create config file
def create_config_file(ip_list):
    # Define the hostnames for each IP address
    hostnames = ['controller-0', 'controller-1', 'worker-0', 'worker-1']
    
    config_content = ""
    
    # Iterate over IP addresses and corresponding hostnames
    for hostname, ip in zip(hostnames, ip_list):
        config_content += f"Host {hostname}\n"
        config_content += f"    HostName {ip}\n"
        config_content += f"    User ubuntu\n"
        config_content += f"    IdentityFile ~/.ssh/kubernetes.id_rsa\n\n"
    
    # Write the content to the SSH config file
    config_path = os.path.expanduser("~/.ssh/config")
    with open(config_path, "w") as config_file:
        config_file.write(config_content)

# Collect the IPs for all nodes
all_ips = [controller.public_ip for controller in controller_instances] + [worker.public_ip for worker in worker_instances]

# Create the config file with the IPs once the instances are ready
pulumi.Output.all(*all_ips).apply(create_config_file)
```

**5. Generate the key Pair**

```sh
cd ~/.ssh/
aws ec2 create-key-pair --key-name kubernetes --output text --query 'KeyMaterial' > kubernetes.id_rsa
chmod 400 kubernetes.id_rsa
```

**6. Create Infra**

```sh
pulumi up --yes
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-10.png)

## Certificate Generation

**1. Create a directory to store all the necessary certifications and config files.**

```sh
mkdir k8s-files
cd k8s-files
```

**2. Create a script `(certificate.sh)` in the `k8s-files` files directory to create the necessary certificates.**

```sh
#!/bin/bash

KUBERNETES_PUBLIC_ADDRESS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns ${LOAD_BALANCER_ARN} \
  --output text --query 'LoadBalancers[].DNSName')
export KUBERNETES_PUBLIC_ADDRESS

KUBERNETES_HOSTNAMES=kubernetes,kubernetes.default,kubernetes.default.svc,kubernetes.default.svc.cluster,kubernetes.svc.cluster.local
export KUBERNETES_HOSTNAMES
           
# Generate CA configuration and certificate
cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "kubernetes": {
        "usages": ["signing", "key encipherment", "server auth", "client auth"],
        "expiry": "8760h"
      }
    }
  }
}
EOF

cat > ca-csr.json <<EOF
{
  "CN": "Kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "Kubernetes",
      "OU": "CA",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -initca ca-csr.json | cfssljson -bare ca

# Generate Admin Client Certificate
cat > admin-csr.json <<EOF
{
  "CN": "admin",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:masters",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes admin-csr.json | cfssljson -bare admin

# Generate Kubelet Client Certificates
for i in 0 1; do
  instance="worker-${i}"
  instance_hostname="ip-10-0-1-2${i}"
  
  cat > ${instance}-csr.json <<EOF
{
  "CN": "system:node:${instance_hostname}",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:nodes",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

  external_ip=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=${instance}" "Name=instance-state-name,Values=running" --output text --query 'Reservations[].Instances[].PublicIpAddress')
  internal_ip=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=${instance}" "Name=instance-state-name,Values=running" --output text --query 'Reservations[].Instances[].PrivateIpAddress')

  cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=${instance_hostname},${external_ip},${internal_ip} -profile=kubernetes ${instance}-csr.json | cfssljson -bare ${instance}
done

# Generate Kube Controller Manager Certificate
cat > kube-controller-manager-csr.json <<EOF
{
  "CN": "system:kube-controller-manager",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:kube-controller-manager",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager

# Generate Kube Proxy Certificate
cat > kube-proxy-csr.json <<EOF
{
  "CN": "system:kube-proxy",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:node-proxier",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-proxy-csr.json | cfssljson -bare kube-proxy

# Generate Kube Scheduler Certificate
cat > kube-scheduler-csr.json <<EOF
{
  "CN": "system:kube-scheduler",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "system:kube-scheduler",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes kube-scheduler-csr.json | cfssljson -bare kube-scheduler

# Generate Kubernetes API Server Certificate
cat > kubernetes-csr.json <<EOF
{
  "CN": "kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "Kubernetes",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -hostname=10.32.0.1,10.0.1.10,10.0.1.11,${KUBERNETES_PUBLIC_ADDRESS},127.0.0.1,${KUBERNETES_HOSTNAMES} -profile=kubernetes kubernetes-csr.json | cfssljson -bare kubernetes

# Generate Service Account Certificate
cat > service-account-csr.json <<EOF
{
  "CN": "service-accounts",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "US",
      "L": "Portland",
      "O": "Kubernetes",
      "OU": "Kubernetes The Hard Way",
      "ST": "Oregon"
    }
  ]
}
EOF

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=kubernetes service-account-csr.json | cfssljson -bare service-account

echo "All certificates generated successfully."

for instance in worker-0 worker-1; do
  external_ip=$(aws ec2 describe-instances --filters \
    "Name=tag:Name,Values=${instance}" \
    "Name=instance-state-name,Values=running" \
    --output text --query 'Reservations[].Instances[].PublicIpAddress')

  scp -i ~/.ssh/kubernetes.id_rsa ca.pem ${instance}-key.pem ${instance}.pem ubuntu@${external_ip}:~/
done

for instance in controller-0 controller-1; do
  external_ip=$(aws ec2 describe-instances --filters \
    "Name=tag:Name,Values=${instance}" \
    "Name=instance-state-name,Values=running" \
    --output text --query 'Reservations[].Instances[].PublicIpAddress')

  scp -i ~/.ssh/kubernetes.id_rsa \
    ca.pem ca-key.pem kubernetes-key.pem kubernetes.pem \
    service-account-key.pem service-account.pem ubuntu@${external_ip}:~/
done
```

This script will install all the necessary certificates.

**3. Now, Save the script as `certificate.sh`**

**4. Make the script executable:**

```sh
chmod +x certificate.sh
```
**5. Run the script:**

```sh
./certificate.sh
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-11.png)

## Client Authentication Configs

Create a script `(kube_config.sh)` in the `k8s-files` files directory to create the necessary certificates.

```sh
#!/bin/bash

# Retrieve the Kubernetes Public DNS Address
KUBERNETES_PUBLIC_ADDRESS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns ${LOAD_BALANCER_ARN} \
  --output text --query 'LoadBalancers[0].DNSName')

echo "Kubernetes Public Address: ${KUBERNETES_PUBLIC_ADDRESS}"

# Generate kubeconfig for each worker node
for instance in worker-0 worker-1; do
  kubectl config set-cluster kubernetes-the-hard-way \
    --certificate-authority=ca.pem \
    --embed-certs=true \
    --server=https://${KUBERNETES_PUBLIC_ADDRESS}:443 \
    --kubeconfig=${instance}.kubeconfig

  kubectl config set-credentials system:node:${instance} \
    --client-certificate=${instance}.pem \
    --client-key=${instance}-key.pem \
    --embed-certs=true \
    --kubeconfig=${instance}.kubeconfig

  kubectl config set-context default \
    --cluster=kubernetes-the-hard-way \
    --user=system:node:${instance} \
    --kubeconfig=${instance}.kubeconfig

  kubectl config use-context default --kubeconfig=${instance}.kubeconfig
done

# Generate kubeconfig for kube-proxy
kubectl config set-cluster kubernetes-the-hard-way \
  --certificate-authority=ca.pem \
  --embed-certs=true \
  --server=https://${KUBERNETES_PUBLIC_ADDRESS}:443 \
  --kubeconfig=kube-proxy.kubeconfig

kubectl config set-credentials system:kube-proxy \
  --client-certificate=kube-proxy.pem \
  --client-key=kube-proxy-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-proxy.kubeconfig

kubectl config set-context default \
  --cluster=kubernetes-the-hard-way \
  --user=system:kube-proxy \
  --kubeconfig=kube-proxy.kubeconfig

kubectl config use-context default --kubeconfig=kube-proxy.kubeconfig

# Generate kubeconfig for kube-controller-manager
kubectl config set-cluster kubernetes-the-hard-way \
  --certificate-authority=ca.pem \
  --embed-certs=true \
  --server=https://127.0.0.1:6443 \
  --kubeconfig=kube-controller-manager.kubeconfig

kubectl config set-credentials system:kube-controller-manager \
  --client-certificate=kube-controller-manager.pem \
  --client-key=kube-controller-manager-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-controller-manager.kubeconfig

kubectl config set-context default \
  --cluster=kubernetes-the-hard-way \
  --user=system:kube-controller-manager \
  --kubeconfig=kube-controller-manager.kubeconfig

kubectl config use-context default --kubeconfig=kube-controller-manager.kubeconfig

# Generate kubeconfig for kube-scheduler
kubectl config set-cluster kubernetes-the-hard-way \
  --certificate-authority=ca.pem \
  --embed-certs=true \
  --server=https://127.0.0.1:6443 \
  --kubeconfig=kube-scheduler.kubeconfig

kubectl config set-credentials system:kube-scheduler \
  --client-certificate=kube-scheduler.pem \
  --client-key=kube-scheduler-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-scheduler.kubeconfig

kubectl config set-context default \
  --cluster=kubernetes-the-hard-way \
  --user=system:kube-scheduler \
  --kubeconfig=kube-scheduler.kubeconfig

kubectl config use-context default --kubeconfig=kube-scheduler.kubeconfig

# Generate kubeconfig for admin user
kubectl config set-cluster kubernetes-the-hard-way \
  --certificate-authority=ca.pem \
  --embed-certs=true \
  --server=https://127.0.0.1:6443 \
  --kubeconfig=admin.kubeconfig

kubectl config set-credentials admin \
  --client-certificate=admin.pem \
  --client-key=admin-key.pem \
  --embed-certs=true \
  --kubeconfig=admin.kubeconfig

kubectl config set-context default \
  --cluster=kubernetes-the-hard-way \
  --user=admin \
  --kubeconfig=admin.kubeconfig

kubectl config use-context default --kubeconfig=admin.kubeconfig

# Distribute kubeconfig files to worker instances
for instance in worker-0 worker-1; do
  external_ip=$(aws ec2 describe-instances --filters \
    "Name=tag:Name,Values=${instance}" \
    "Name=instance-state-name,Values=running" \
    --output text --query 'Reservations[].Instances[].PublicIpAddress')

  scp -i ~/.ssh/kubernetes.id_rsa \
    ${instance}.kubeconfig kube-proxy.kubeconfig ubuntu@${external_ip}:~/
done

# Distribute kubeconfig files to controller instances
for instance in controller-0 controller-1; do
  external_ip=$(aws ec2 describe-instances --filters \
    "Name=tag:Name,Values=${instance}" \
    "Name=instance-state-name,Values=running" \
    --output text --query 'Reservations[].Instances[].PublicIpAddress')
  
  scp -i ~/.ssh/kubernetes.id_rsa \
    admin.kubeconfig kube-controller-manager.kubeconfig kube-scheduler.kubeconfig ubuntu@${external_ip}:~/
done

# Generate encryption key
ENCRYPTION_KEY=$(head -c 32 /dev/urandom | base64)

# Create encryption config file
cat > encryption-config.yaml <<EOF
kind: EncryptionConfig
apiVersion: v1
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: ${ENCRYPTION_KEY}
      - identity: {}
EOF

# Copy the encryption config file to each controller instance
for instance in controller-0 controller-1; do
  external_ip=$(aws ec2 describe-instances --filters \
    "Name=tag:Name,Values=${instance}" \
    "Name=instance-state-name,Values=running" \
    --output text --query 'Reservations[].Instances[].PublicIpAddress')
  
  scp -i ~/.ssh/kubernetes.id_rsa encryption-config.yaml ubuntu@${external_ip}:~/
done

echo "Kubernetes configuration files and encryption config have been generated and distributed."
```

This script will install all the necessary Client Authentication Configs.

**1. Now, Save the script as `kube_config.sh`**

**2. Make the script executable:**

```sh
chmod +x kube_config.sh
```
**3. Run the script**

```sh
./kube_config.sh
```
![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-12.png)

## Bootstrapping an etcd Cluster Member

> NOTES: The commands in this lab must be run on each controller instances: `controller-0`, `controller-1`

### Login to each controller instance using the `ssh` command.

```sh
ssh controller-0
ssh controller-1
```

### Change the hostname

**1. Controller-0**

```sh
sudo hostnamectl set-hostname controller-0
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-13.png)

**2. Controller-1**

```sh
sudo hostnamectl set-hostname controller-1
```


## Script file for bootstrapping etcd

Create a script file in both the controller instances named as `bootstrap_etcd.sh`

```sh
#!/bin/bash

# Set the etcd version
ETCD_VERSION="v3.5.16"

# Download and install the etcd binaries
wget -q --show-progress --https-only --timestamping \
  "https://github.com/etcd-io/etcd/releases/download/${ETCD_VERSION}/etcd-${ETCD_VERSION}-linux-amd64.tar.gz"

# Extract and install the etcd server and etcdctl command line utility
tar -xvf etcd-${ETCD_VERSION}-linux-amd64.tar.gz
sudo mv etcd-${ETCD_VERSION}-linux-amd64/etcd* /usr/local/bin/

# Create necessary directories
sudo mkdir -p /etc/etcd /var/lib/etcd
sudo chmod 700 /var/lib/etcd

# Copy TLS certificates (Ensure you have ca.pem, kubernetes-key.pem, and kubernetes.pem in the current directory)
sudo cp ca.pem kubernetes-key.pem kubernetes.pem /etc/etcd/

# Set environment variables based on the etcd member
export INTERNAL_IP="<CONTROLLER_INSTANCE_PRIVATE_IP>"
export ETCD_NAME="<ETCD_NAME>"

echo "Internal IP set to: $INTERNAL_IP"
echo "etcd member name set to: $ETCD_NAME"

# Create the etcd systemd service file
cat <<EOF | sudo tee /etc/systemd/system/etcd.service
[Unit]
Description=etcd
Documentation=https://github.com/coreos

[Service]
Type=notify
ExecStart=/usr/local/bin/etcd \\
  --name ${ETCD_NAME} \\
  --cert-file=/etc/etcd/kubernetes.pem \\
  --key-file=/etc/etcd/kubernetes-key.pem \\
  --peer-cert-file=/etc/etcd/kubernetes.pem \\
  --peer-key-file=/etc/etcd/kubernetes-key.pem \\
  --trusted-ca-file=/etc/etcd/ca.pem \\
  --peer-trusted-ca-file=/etc/etcd/ca.pem \\
  --peer-client-cert-auth \\
  --client-cert-auth \\
  --initial-advertise-peer-urls https://${INTERNAL_IP}:2380 \\
  --listen-peer-urls https://${INTERNAL_IP}:2380 \\
  --listen-client-urls https://${INTERNAL_IP}:2379,https://127.0.0.1:2379 \\
  --advertise-client-urls https://${INTERNAL_IP}:2379 \\
  --initial-cluster-token etcd-cluster-0 \\
  --initial-cluster controller-0=https://10.0.1.10:2380,controller-1=https://10.0.1.11:2380 \\
  --initial-cluster-state new \\
  --data-dir=/var/lib/etcd
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to register the etcd service
sudo systemctl daemon-reload

# Enable and start the etcd service
sudo systemctl enable etcd
sudo systemctl start etcd
```

### NOTE: 

Please update the placeholder values of <INTERNAL_IP> and <ETCD_NAME> for `Controller-0`:

```sh
INTERNAL_IP="10.0.1.10"
ETCD_NAME="controller-0"
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-15.png)

For `Controller-1`

```sh
INTERNAL_IP="10.0.1.11"
ETCD_NAME="controller-1"
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-16.png)


**1. After updating, Save the script as `bootstrap_etcd.sh`**

**2. Make it executable:**
```sh
chmod +x bootstrap_etcd.sh
```
**3. Run the script**

```sh
./bootstrap_etcd.sh
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-17.png)


## Verify the etcd Cluster

First check if etcd service is ruinning on both nodes or not

```sh
sudo systemctl status etcd
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-18.png)

Once the etcd service is **running** on both nodes, verify the cluster status by listing the cluster members:

```sh
sudo ETCDCTL_API=3 etcdctl member list \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/etcd/ca.pem \
  --cert=/etc/etcd/kubernetes.pem \
  --key=/etc/etcd/kubernetes-key.pem
```

> output

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-19.png)

## Provision the Kubernetes Control Plane

Start by creating the necessary configuration directory for Kubernetes:

```sh
sudo mkdir -p /etc/kubernetes/config
```

This directory will hold the configuration files for the Kubernetes control plane components.

### Download and Install the Kubernetes Controller Binaries

Next, download the official Kubernetes binaries for the **API server, controller manager, scheduler, and kubectl**:

```sh
wget -q --show-progress --https-only --timestamping \
  "https://storage.googleapis.com/kubernetes-release/release/v1.21.0/bin/linux/amd64/kube-apiserver" \
  "https://storage.googleapis.com/kubernetes-release/release/v1.21.0/bin/linux/amd64/kube-controller-manager" \
  "https://storage.googleapis.com/kubernetes-release/release/v1.21.0/bin/linux/amd64/kube-scheduler" \
  "https://storage.googleapis.com/kubernetes-release/release/v1.21.0/bin/linux/amd64/kubectl"
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image.png)

After downloading the binaries, give them execution permissions and move them to `/usr/local/bin/:`

```sh
chmod +x kube-apiserver kube-controller-manager kube-scheduler kubectl
sudo mv kube-apiserver kube-controller-manager kube-scheduler kubectl /usr/local/bin/
```

### Configure the Kubernetes API Server

Create the directory to store the API server's certificates and configuration files and move the necessary TLS certificates and encryption configuration file into the directory:

```sh
sudo mkdir -p /var/lib/kubernetes/

sudo mv ca.pem ca-key.pem kubernetes-key.pem kubernetes.pem \
  service-account-key.pem service-account.pem \
  encryption-config.yaml /var/lib/kubernetes/
```

These certificates are used to secure communication between the API server, etcd, and other Kubernetes components.


### Set Private IP and Public IP Addresses

The instance `Private IP` address will be used to advertise the API Server to members of the cluster. Retrieve the private IP address for the current compute instance:

### For Controller-0

Set the private ip of the controller instance.

```bash
INTERNAL_IP="10.0.1.10"
export INTERNAL_IP
echo $INTERNAL_IP
```

### Set `KUBERNETES_PUBLIC_ADDRESS`

Set the Public IP of the controller instance

```sh
KUBERNETES_PUBLIC_ADDRESS="<PUBLIC_IP_OF_CONTROLLER-0>"
export KUBERNETES_PUBLIC_ADDRESS
echo $KUBERNETES_PUBLIC_ADDRESS
```

### For Controller-1

Set the private ip of the controller instance.

```bash
INTERNAL_IP="10.0.1.11"
export INTERNAL_IP
echo $INTERNAL_IP
```

### Set `KUBERNETES_PUBLIC_ADDRESS`

Set the Public IP of the controller instance.

```sh
KUBERNETES_PUBLIC_ADDRESS="<PUBLIC_IP_OF_CONTROLLER-1>"
export KUBERNETES_PUBLIC_ADDRESS
echo $KUBERNETES_PUBLIC_ADDRESS
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-1.png)

### Create the `kube-apiserver.service` systemd unit file:

```sh
cat <<EOF | sudo tee /etc/systemd/system/kube-apiserver.service
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-apiserver \\
  --advertise-address=${INTERNAL_IP} \\
  --allow-privileged=true \\
  --apiserver-count=2 \\
  --audit-log-maxage=30 \\
  --audit-log-maxbackup=3 \\
  --audit-log-maxsize=100 \\
  --audit-log-path=/var/log/audit.log \\
  --authorization-mode=Node,RBAC \\
  --bind-address=0.0.0.0 \\
  --client-ca-file=/var/lib/kubernetes/ca.pem \\
  --enable-admission-plugins=NamespaceLifecycle,NodeRestriction,LimitRanger,ServiceAccount,DefaultStorageClass,ResourceQuota \\
  --etcd-cafile=/var/lib/kubernetes/ca.pem \\
  --etcd-certfile=/var/lib/kubernetes/kubernetes.pem \\
  --etcd-keyfile=/var/lib/kubernetes/kubernetes-key.pem \\
  --etcd-servers=https://10.0.1.10:2379,https://10.0.1.11:2379 \\
  --event-ttl=1h \\
  --encryption-provider-config=/var/lib/kubernetes/encryption-config.yaml \\
  --kubelet-certificate-authority=/var/lib/kubernetes/ca.pem \\
  --kubelet-client-certificate=/var/lib/kubernetes/kubernetes.pem \\
  --kubelet-client-key=/var/lib/kubernetes/kubernetes-key.pem \\
  --runtime-config='api/all=true' \\
  --service-account-key-file=/var/lib/kubernetes/service-account.pem \\
  --service-account-signing-key-file=/var/lib/kubernetes/service-account-key.pem \\
  --service-account-issuer=https://${KUBERNETES_PUBLIC_ADDRESS}:443 \\
  --service-cluster-ip-range=10.32.0.0/24 \\
  --service-node-port-range=30000-32767 \\
  --tls-cert-file=/var/lib/kubernetes/kubernetes.pem \\
  --tls-private-key-file=/var/lib/kubernetes/kubernetes-key.pem \\
  --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

This file defines how the API server is launched and managed. Key configuration includes:

- **Advertise and Bind Addresses:** Defines internal and external IP addresses for communication.
- **Authorization:** Uses Node and RBAC authorization modes.
- **TLS and Client Certificates:** Specifies certificates for secure communication with etcd and Kubelets.
- **Admission Plugins:** Controls how resources are created in the cluster.

### Configure the Kubernetes Controller Manager

Move the `kube-controller-manager` kubeconfig into place:

```sh
sudo mv kube-controller-manager.kubeconfig /var/lib/kubernetes/
```

Create the `kube-controller-manager.service` systemd unit file:

```sh
cat <<EOF | sudo tee /etc/systemd/system/kube-controller-manager.service
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-controller-manager \\
  --bind-address=0.0.0.0 \\
  --cluster-cidr=10.200.0.0/16 \\
  --cluster-name=kubernetes \\
  --cluster-signing-cert-file=/var/lib/kubernetes/ca.pem \\
  --cluster-signing-key-file=/var/lib/kubernetes/ca-key.pem \\
  --kubeconfig=/var/lib/kubernetes/kube-controller-manager.kubeconfig \\
  --leader-elect=true \\
  --root-ca-file=/var/lib/kubernetes/ca.pem \\
  --service-account-private-key-file=/var/lib/kubernetes/service-account-key.pem \\
  --service-cluster-ip-range=10.32.0.0/24 \\
  --use-service-account-credentials=true \\
  --v=4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

The controller manager is responsible for maintaining the desired state of the cluster, managing controllers like node, pod, and service controllers.

### Configure the Kubernetes Scheduler

**Move the `kube-scheduler` kubeconfig into place:**

```bash
sudo mv kube-scheduler.kubeconfig /var/lib/kubernetes/
```

**Create the `kube-scheduler.yaml` configuration file:**

```yaml
cat <<EOF | sudo tee /etc/kubernetes/config/kube-scheduler.yaml
apiVersion: kubescheduler.config.k8s.io/v1beta1
kind: KubeSchedulerConfiguration
clientConnection:
  kubeconfig: "/var/lib/kubernetes/kube-scheduler.kubeconfig"
leaderElection:
  leaderElect: true
EOF
```

**Create the `kube-scheduler.service` systemd unit file:**

```bash
cat <<EOF | sudo tee /etc/systemd/system/kube-scheduler.service
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-scheduler \\
  --config=/etc/kubernetes/config/kube-scheduler.yaml \\
  --v=4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
```

The scheduler is responsible for deciding which node will run newly created pods.

### Start the Controller Services

Reload the systemd configuration and start the control plane services:

```sh
sudo systemctl daemon-reload
sudo systemctl enable kube-apiserver kube-controller-manager kube-scheduler
sudo systemctl start kube-apiserver kube-controller-manager kube-scheduler
```

> Allow up to 10 seconds for the Kubernetes API Server to fully initialize.

### Verification

Verify that the Kubernetes control plane is running by checking the cluster status:

```sh
kubectl cluster-info --kubeconfig admin.kubeconfig
```
>OUTPUT:

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-2.png)

> Remember to run the above command on each controller node: `controller-0`, `controller-1`.

### Add Host File Entries

In order for `kubectl exec` commands to work, the controller nodes must each be able to resolve the worker hostnames.  This is not set up by default in AWS. The workaround is to add manual host entries on each of the controller nodes with this command:

```sh
cat <<EOF | sudo tee -a /etc/hosts
10.0.1.20 ip-10-0-1-20
10.0.1.21 ip-10-0-1-21
EOF
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-3.png)

> If this step is missed, the [DNS Cluster Add-on](12-dns-addon.md) testing will
fail with an error like this: `Error from server: error dialing backend: dial tcp: lookup ip-10-0-1-21 on 127.0.0.53:53: server misbehaving`.

## RBAC for Kubelet Authorization

In this section you will configure RBAC permissions to allow the Kubernetes API Server to access the Kubelet API on each worker node. Access to the Kubelet API is required for retrieving metrics, logs, and executing commands in pods.

> This tutorial sets the Kubelet `--authorization-mode` flag to `Webhook`. Webhook mode uses the [SubjectAccessReview](https://kubernetes.io/docs/admin/authorization/#checking-api-access) API to determine authorization.

> The commands in this section will effect the entire cluster and only need to be run `once` from one of the controller nodes.

## Create the `system:kube-apiserver-to-kubelet`

Create the `system:kube-apiserver-to-kubelet` [ClusterRole](https://kubernetes.io/docs/admin/authorization/rbac/#role-and-clusterrole) with permissions to access the Kubelet API and perform most common tasks associated with managing pods:

```sh
cat <<EOF | kubectl apply --kubeconfig admin.kubeconfig -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "true"
  labels:
    kubernetes.io/bootstrapping: rbac-defaults
  name: system:kube-apiserver-to-kubelet
rules:
  - apiGroups:
      - ""
    resources:
      - nodes/proxy
      - nodes/stats
      - nodes/log
      - nodes/spec
      - nodes/metrics
    verbs:
      - "*"
EOF
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-4.png)

The Kubernetes API Server authenticates to the Kubelet as the `kubernetes` user using the client certificate as defined by the `--kubelet-client-certificate` flag.

Bind the `system:kube-apiserver-to-kubelet` ClusterRole to the `kubernetes` user:

```bash
cat <<EOF | kubectl apply --kubeconfig admin.kubeconfig -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: system:kube-apiserver
  namespace: ""
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:kube-apiserver-to-kubelet
subjects:
  - apiGroup: rbac.authorization.k8s.io
    kind: User
    name: kubernetes
EOF
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-5.png)

### Verification of cluster public endpoint

> The compute instances created in this tutorial will not have permission to complete this section. **Run the following commands from the same machine used to create the compute instances**.

Retrieve the `kubernetes-the-hard-way` Load Balancer address(Run it from poridhi vs code):

```sh
KUBERNETES_PUBLIC_ADDRESS=$(aws elbv2 describe-load-balancers \
  --load-balancer-arns ${LOAD_BALANCER_ARN} \
  --output text --query 'LoadBalancers[].DNSName')
```
```sh
echo $KUBERNETES_PUBLIC_ADDRESS
```
> Output
```sh
kubernetes-77dd3661caa2c707.elb.ap-southeast-1.amazonaws.com
```
Make a HTTP request for the Kubernetes version info:

```sh
curl --cacert ca.pem https://${KUBERNETES_PUBLIC_ADDRESS}/version
```

> output

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Kubernetes%20Tasks/kubernetes-the-hard-way/lab-5/images/image-6.png)


So, we have bootstrapped the kubernetes control plane. In the next lab, we will bootstrap the kubernetes worker nodes.