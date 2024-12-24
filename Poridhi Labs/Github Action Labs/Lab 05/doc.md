# Git-runner AWS

## Step 1: Setting up EC2 Instances with Pulumi

### Configure AWS CLI

1. Install and configure the AWS CLI with your credentials by running:
   ```bash
   aws configure
   ```
   Follow the prompts to input:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region
   - Output format (e.g., `json`)

2. Your access keys can be found on the lab description page where the credentials were generated.

### Set Up a Pulumi Project

#### Create and Initialise the Pulumi Project

1. Create a new directory for the Pulumi project:

   ```bash
   mkdir k3s-infra && cd k3s-infra
   pulumi new aws-javascript
   ```
   This sets up a basic Pulumi project. Follow the prompts to provide details like project name and description.

#### Create a Key Pair

2. Create an EC2 key pair to allow SSH access to the instances:
   ```bash
   aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem
   ```

3. Set file permissions for the key file:
   ```bash
   chmod 400 MyKeyPair.pem
   ```

#### Write Pulumi Code

Replace the contents of `index.js` with the following code:

```javascript
const pulumi = require("@pulumi/pulumi");
const aws = require("@pulumi/aws");

// Create a VPC
const vpc = new aws.ec2.Vpc("k3s-vpc", {
    cidrBlock: "10.0.0.0/16",
    enableDnsHostnames: true,
    enableDnsSupport: true,
    tags: { Name: "k3s-vpc" },
});
exports.vpcId = vpc.id;

// Create a public subnet
const publicSubnet = new aws.ec2.Subnet("k3s-subnet", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "ap-southeast-1a",
    mapPublicIpOnLaunch: true,
    tags: { Name: "k3s-subnet" },
});
exports.publicSubnetId = publicSubnet.id;

// Internet Gateway
const internetGateway = new aws.ec2.InternetGateway("k3s-igw", {
    vpcId: vpc.id,
    tags: { Name: "k3s-igw" },
});
exports.igwId = internetGateway.id;

// Route Table
const publicRouteTable = new aws.ec2.RouteTable("k3s-rt", {
    vpcId: vpc.id,
    tags: { Name: "k3s-rt" },
});
exports.publicRouteTableId = publicRouteTable.id;

new aws.ec2.Route("igw-route", {
    routeTableId: publicRouteTable.id,
    destinationCidrBlock: "0.0.0.0/0",
    gatewayId: internetGateway.id,
});

new aws.ec2.RouteTableAssociation("rt-association", {
    subnetId: publicSubnet.id,
    routeTableId: publicRouteTable.id,
});

// Security Group
const k3sSecurityGroup = new aws.ec2.SecurityGroup("k3s-secgrp", {
    vpcId: vpc.id,
    description: "Allow SSH and K3s traffic",
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 6443, toPort: 6443, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [
        { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] },
    ],
    tags: { Name: "k3s-secgrp" },
});
exports.k3sSecurityGroupId = k3sSecurityGroup.id;

// AMI and Instances
const amiId = "ami-01811d4912b4ccb26"; // Ubuntu 24.04 LTS
const createInstance = (name) => new aws.ec2.Instance(name, {
    instanceType: "t3.small",
    vpcSecurityGroupIds: [k3sSecurityGroup.id],
    ami: amiId,
    subnetId: publicSubnet.id,
    keyName: "MyKeyPair",
    associatePublicIpAddress: true,
    tags: { Name: name, Environment: "Development", Project: "K3sSetup" },
});

const masterNode = createInstance("k3s-master-node");
const workerNode1 = createInstance("k3s-worker-node-1");
const workerNode2 = createInstance("k3s-worker-node-2");

exports.masterNodeDetails = { id: masterNode.id, publicIp: masterNode.publicIp };
exports.workerNode1Details = { id: workerNode1.id, publicIp: workerNode1.publicIp };
exports.workerNode2Details = { id: workerNode2.id, publicIp: workerNode2.publicIp };
```

#### Deploy the Infrastructure
Run the following command to provision the EC2 instances:

```bash
pulumi up --yes
```

## Step 2: Install K3S using Ansible

### Create Project Structure

This is the structure for ansible configurations we'll be creating:

```plaintext
ansible-k3s/
├── ansible.cfg
├── inventory
├── playbook.yml
├── roles/
    └── k3s/
        ├── tasks/
        │   ├── main.yml
        │   ├── master.yml
        │   └── worker.yml
        ├── vars/
            └── main.yml
```


Run the following commands to create the desired structure:

```bash 
# Create the main project directory
mkdir -p ansible-k3s/roles/k3s/tasks
mkdir -p ansible-k3s/roles/k3s/vars

# Create the necessary files
touch ansible-k3s/ansible.cfg
touch ansible-k3s/inventory
touch ansible-k3s/playbook.yml
touch ansible-k3s/roles/k3s/tasks/main.yml
touch ansible-k3s/roles/k3s/tasks/master.yml
touch ansible-k3s/roles/k3s/tasks/worker.yml
touch ansible-k3s/roles/k3s/vars/main.yml
```



### Install Ansible

Now navigate to the `ansible-k3s` directory. Then, install Ansible on your machine, run these commands:

```bash
sudo apt-get update -y
sudo apt install software-properties-common -y
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install -y ansible 
sudo ansible --version
```

### Configure Ansible

Populate the following files using the given configurations, playbook and role tasks.


#### `ansible.cfg`

```bash
[defaults]
inventory = inventory
roles_path = roles
deprecation_warnings = False
host_key_checking = False
```

#### `inventory`

```ini
[k3s-master]
master ansible_host=<public-ip-of-master> ansible_user=ubuntu ansible_ssh_private_key_file=../k3s-infra/MyKeyPair.pem

[k3s-workers]
worker1 ansible_host=<public-ip-of-worker-1> ansible_user=ubuntu ansible_ssh_private_key_file=../k3s-infra/MyKeyPair.pem
worker2 ansible_host=<public-ip-of-worker-2> ansible_user=ubuntu ansible_ssh_private_key_file=../k3s-infra/MyKeyPair.pem
```

#### `playbook.yml`

```yaml
- hosts: k3s-master
  roles:
    - role: k3s
      k3s_role: master

- hosts: k3s-workers
  roles:
    - role: k3s
      k3s_role: worker
```


#### `roles/k3s/tasks/main.yml`

```yaml
- name: Include tasks for K3s Master
  include_tasks: master.yml
  when: k3s_role == "master"

- name: Include tasks for K3s Worker
  include_tasks: worker.yml
  when: k3s_role == "worker"
```

#### `roles/k3s/tasks/master.yml`

```yaml
- name: Install K3s on Master
  shell: curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644
  become: true

- name: Retrieve K3s Token
  shell: cat /var/lib/rancher/k3s/server/node-token
  become: true
  register: k3s_token

- name: Save K3s Token for Workers
  copy:
    content: "{{ k3s_token.stdout }}"
    dest: /tmp/k3s_token
  delegate_to: localhost
```

#### `roles/k3s/tasks/worker.yml`

```yaml
- name: Create local token directory
  file:
    path: "/tmp/k3s_token_workers"
    state: directory
    mode: '0755'
  delegate_to: localhost

- name: Read K3s Token
  command: cat /tmp/k3s_token
  register: k3s_token
  delegate_to: localhost

- name: Install K3s on Worker
  shell: |
    curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" K3S_URL="https://{{ hostvars[groups['k3s-master'][0]]['ansible_default_ipv4']['address'] }}:6443" K3S_TOKEN="{{ k3s_token.stdout }}" sh -
  become: true
```

#### `roles/k3s/vars/main.yml`

```bash
k3s_role: master
```

### **Run Playbook**

```bash
ansible-playbook playbook.yml
```

### **Check Installation**

SSH into instances using public IP of master node and run:

```bash
kubectl get nodes
```

