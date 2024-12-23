# Git-runner AWS

## Step 1: Setting up EC2 Instances with Pulumi

### Configure AWS CLI

- Configure AWS CLI with the necessary credentials. Run the following command and follow the prompts to configure it:

    ```sh
    aws configure
    ```
    
    This command sets up your AWS CLI with the necessary credentials, region, and output format.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Redis%20Labs/Lab%2001/images/image.png)

    You will find the `AWS Access key` and `AWS Seceret Access key` on Lab description page,where you generated the credentials.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Redis%20Labs/Lab%2001/images/image-1.png)

### Set Up a Pulumi Project

Now, let's create a new Pulumi project and write the code to provision our EC2 instances.

1. Create a new directory and initialize a Pulumi project:

   ```bash
   mkdir k3s-infra && cd k3s-infra
   pulumi new aws-javascript
   ```

    This command creates a new directory with the basic structure for a Pulumi project. Follow the prompts to set up your project.

2. Create Key Pair

    Create a new key pair for our instances using the following command:

    ```sh
    aws ec2 create-key-pair --key-name MyKeyPair --query 'KeyMaterial' --output text > MyKeyPair.pem
    ```

3. Set File Permissions of the key files

    ```sh
    chmod 400 MyKeyPair.pem
    ```


4. Replace the contents of `index.js` with the following code:

    ```javascript
    const pulumi = require("@pulumi/pulumi");
    const aws = require("@pulumi/aws");

    // Create a VPC
    const vpc = new aws.ec2.Vpc("k3s-vpc", {
        cidrBlock: "10.0.0.0/16",
        enableDnsHostnames: true,
        enableDnsSupport: true,
        tags: {
            Name: "k3s-vpc",
        },
    });
    exports.vpcId = vpc.id;

    // Create a single public subnet
    const publicSubnet = new aws.ec2.Subnet("k3s-subnet", {
        vpcId: vpc.id,
        cidrBlock: "10.0.1.0/24",
        availabilityZone: "ap-southeast-1a",
        mapPublicIpOnLaunch: true,
        tags: {
            Name: "k3s-subnet",
        },
    });
    exports.publicSubnetId = publicSubnet.id;

    // Create an Internet Gateway
    const internetGateway = new aws.ec2.InternetGateway("k3s-igw", {
        vpcId: vpc.id,
        tags: {
            Name: "k3s-igw",
        },
    });
    exports.igwId = internetGateway.id;

    // Create a Route Table
    const publicRouteTable = new aws.ec2.RouteTable("k3s-rt", {
        vpcId: vpc.id,
        tags: {
            Name: "k3s-rt",
        },
    });
    exports.publicRouteTableId = publicRouteTable.id;

    // Create a route in the Route Table for the Internet Gateway
    new aws.ec2.Route("igw-route", {
        routeTableId: publicRouteTable.id,
        destinationCidrBlock: "0.0.0.0/0",
        gatewayId: internetGateway.id,
    });

    // Associate Route Table with the public subnet
    new aws.ec2.RouteTableAssociation("rt-association", {
        subnetId: publicSubnet.id,
        routeTableId: publicRouteTable.id,
    });

    // Create a Security Group for K3s Instances
    const k3sSecurityGroup = new aws.ec2.SecurityGroup("k3s-secgrp", {
        vpcId: vpc.id,
        description: "Allow SSH and K3s traffic",
        ingress: [
            { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] }, // SSH
            { protocol: "tcp", fromPort: 6443, toPort: 6443, cidrBlocks: ["0.0.0.0/0"] }, // K3s API
        ],
        egress: [
            { protocol: "-1", fromPort: 0, toPort: 0, cidrBlocks: ["0.0.0.0/0"] }, // Allow all outbound traffic
        ],
        tags: {
            Name: "k3s-secgrp",
        },
    });
    exports.k3sSecurityGroupId = k3sSecurityGroup.id;

    // Define an AMI for the EC2 instances
    const amiId = "ami-01811d4912b4ccb26"; // Ubuntu 24.04 LTS

    // Create K3s Instances
    const createInstance = (name) => {
        return new aws.ec2.Instance(name, {
            instanceType: "t2.micro",
            vpcSecurityGroupIds: [k3sSecurityGroup.id],
            ami: amiId,
            subnetId: publicSubnet.id,
            keyName: "MyKeyPair", // Update with your key pair
            associatePublicIpAddress: true,
            tags: {
                Name: name,
                Environment: "Development",
                Project: "K3sSetup",
            },
        });
    };

    // Create the master node
    const masterNode = createInstance("k3s-master-node");

    // Create the worker nodes
    const workerNode1 = createInstance("k3s-worker-node-1");
    const workerNode2 = createInstance("k3s-worker-node-2");

    // Export the instance details
    exports.masterNodeDetails = { id: masterNode.id, publicIp: masterNode.publicIp };
    exports.workerNode1Details = { id: workerNode1.id, publicIp: workerNode1.publicIp };
    exports.workerNode2Details = { id: workerNode2.id, publicIp: workerNode2.publicIp };
    ```

5. Deploy the infrastructure:

   ```bash
   pulumi up
   ```

## Step 2: Install K3S using Ansible

### Create Directory

```bash 
mkdir ansible-k3s && cd ansible-k3s
```

### Install Ansible

To install Ansible on an Ubuntu machine, run these commands:

```bash
sudo apt-get update -y
sudo apt install software-properties-common -y
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install -y ansible
```

### Project Structure

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

### ansible.cfg

```bash
[defaults]
inventory = inventory
roles_path = roles
deprecation_warnings = False
```

### inventory

```ini
[k3s-master]
master ansible_host=13.212.88.123 ansible_user=ubuntu ansible_ssh_private_key_file=../Infra/MyKeyPair.pem

[k3s-workers]
worker1 ansible_host=46.137.227.11 ansible_user=ubuntu ansible_ssh_private_key_file=../Infra/MyKeyPair.pem
worker2 ansible_host=18.143.108.8 ansible_user=ubuntu ansible_ssh_private_key_file=../Infra/MyKeyPair.pem
```

### playbook.yml

```bash
- hosts: k3s-master
  roles:
    - role: k3s
      k3s_role: master

- hosts: k3s-workers
  roles:
    - role: k3s
      k3s_role: worker
```

### roles/k3s/tasks/main.yml

```bash
- name: Include tasks for K3s Master
  include_tasks: master.yml
  when: k3s_role == "master"

- name: Include tasks for K3s Worker
  include_tasks: worker.yml
  when: k3s_role == "worker"
```

### roles/k3s/tasks/master.yml

```bash
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

### roles/k3s/tasks/worker.yml:

```bash
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

### roles/k3s/vars/main.yml:

```bash
k3s_role: master
```

### Run Playbook

```bash
ansible-playbook playbook.yml
```

### Check Installation

SSH into instances and run:

```bash
kubectl get nodes
```

