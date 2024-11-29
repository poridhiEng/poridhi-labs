# Launch multiple EC2 instances with different AMI IDs using Ansible and install Nginx into these instances

This lab will guide you through the process of launching multiple EC2 instances with different AMI (Amazon Machine Image) IDs using Ansible. Additionally, we'll demonstrate how to install and configure `NGINX`, a popular web server, on these instances.

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2011/images/image-4.png)

### Overview

In this tutorial, we'll cover the following key steps:

1. **Create AWS infrastructure and launch EC2 isntances**.

    - Setting Up the Environment with prequisites.

    - Defining Ansible Playbooks and Roles for creating AWS infrastructure, launcing EC2 instances for different Linux distribution.

    - Creating AWS infrastucture and Launching EC2 Instances.

2. **Installing and Configuring NGINX**

### Prerequisites

Before diving into the tutorial, make sure you have the following:

- Ansible installed on your local machine.
- AWS CLI configured with your AWS credentials.


## Project Structure:

The project is organized into the following directories and files:

```sh
ansible/
├── ansible.cfg
├── hosts.ini
├── hosts.ini.j2
├── roles/
│   ├── nginx/
│   │   ├── tasks/
│   │       ├── main.yml
│   ├── vpc/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── vars/
│   │       └── main.yml
│   ├── instance/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── vars/
│   │       └── main.yml
│   ├── security/
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── vars/
│   │       └── main.yml
│   └── keypair/
│       ├── tasks/
│       │   └── main.yml
│       └── vars/
│           └── main.yml
├── create_infra.yml
├── install_nginx.yml
```

You can create the directories and files using the following `mkdir` and `touch` commands. Run this command from your project's root directory:

```sh
mkdir -p roles/vpc/tasks roles/vpc/vars \
         roles/instance/tasks roles/instance/vars \
         roles/security/tasks roles/security/vars \
         roles/keypair/tasks roles/keypair/vars \
         roles/nginx/tasks

touch roles/vpc/tasks/main.yml roles/vpc/vars/main.yml \
      roles/instance/tasks/main.yml roles/instance/vars/main.yml \
      roles/security/tasks/main.yml roles/security/vars/main.yml \
      roles/keypair/tasks/main.yml roles/keypair/vars/main.yml \
      roles/nginx/tasks/main.yml

touch ansible.cfg \
        hosts.ini \
        hosts.ini.j2 \
        create_infra.yml \
        install_nginx.yml
```

### Explanation:
- `mkdir -p` creates the directories, including parent directories as needed.
- `touch` creates the empty `main.yml` files in each `tasks` and `vars` directory.

## Create AWS infrastructure and launch EC2 isntances.

### Step 01: Install Required Dependencies

- We will require `boto3` and `botocore` libraries. We can install them using pip:

    ```sh
    pip install boto3 botocore
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-7.png)

- Install amazon aws collection

    ```sh
    ansible-galaxy collection install amazon.aws
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-8.png)

### Step 02: Set Up AWS Configuration

Now We need to configure our AWS credentials. We can do this by using the AWS credentials file.

- Configure AWS CLI

    ```sh
    aws configure
    ```
- You will be prompted to enter your `AWS Access Key ID`, `Secret Access Key`, `default region name`, and `default output format`:

    ```sh
    AWS Access Key ID [None]: YOUR_ACCESS_KEY_ID
    AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
    Default region name [None]: YOUR_DEFAULT_REGION
    Default output format [None]: json
    ```
    Replace `YOUR_ACCESS_KEY_ID`, `YOUR_SECRET_ACCESS_KEY`, and `YOUR_DEFAULT_REGION` with the respective values. For the default region, make sure to use a region `ap-southeast-1`.

- You can see the AWS CLI configuration file located at `~/.aws/config` and `~/.aws/credentials`.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image.png)

### Step 03: Create the key pair for the EC2 instance

- Run this command to create key-pair:

    ```sh
    ssh-keygen
    ```
    This will create a keypair( public-key and private-key ) in the `~/.ssh/` directory.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-1.png)

    We will use the public-key for instance creation and private key for ssh.


### Step 04: Create Roles to organize the tasks (AWS infrastructure and EC2 launch)

### 1. VPC Role

**Purpose**: This role will handle the creation of the VPC, Subnet, Internet Gateway, and Route Table.

- Update the `vpc/tasks/main.yml` file with these contents:

```yml
---
- name: Create VPC
  amazon.aws.ec2_vpc_net:
    name: my_vpc
    cidr_block: "{{ vpc_cidr_block }}"
    region: "{{ region }}"
    tags:
      Name: my_vpc
  register: vpc

- name: Create subnet
  amazon.aws.ec2_vpc_subnet:
    vpc_id: "{{ vpc.vpc.id }}"
    cidr: "{{ subnet_cidr_block }}"
    region: "{{ region }}"
    tags:
      Name: my_subnet
  register: subnet

- name: Create internet gateway
  amazon.aws.ec2_vpc_igw:
    vpc_id: "{{ vpc.vpc.id }}"
    region: "{{ region }}"
    tags:
      Name: my_igw
  register: igw

- name: Set up public subnet route table
  amazon.aws.ec2_vpc_route_table:
    vpc_id: "{{ vpc.vpc.id }}"
    region: "{{ region }}"
    tags:
      Name: Public-route-table
    subnets:
      - "{{ subnet.subnet.id }}"
    routes:
      - dest: 0.0.0.0/0
        gateway_id: "{{ igw.gateway_id }}"
  register: public_route_table
```

- **vars/main.yml**

```yml
---
vpc_cidr_block: "10.0.0.0/16"
subnet_cidr_block: "10.0.1.0/24"
region: "ap-southeast-1"
```

### 2. Instance Role

**Purpose**: This role manages the launching of the EC2 instances.

- Update the `instance/tasks/main.yml` file with these contents:

```yml
- name: Launch EC2 instances
  amazon.aws.ec2_instance:
    name: "{{ item.name }}"
    key_name: "{{ key_name }}"
    instance_type: "{{ item.instance_type }}"
    image_id: "{{ item.ami_id }}"
    region: "{{ region }}"
    vpc_subnet_id: "{{ subnet.subnet.id }}"
    security_group: "{{ sg.group_id }}"
    network:
      assign_public_ip: true
    tags:
      Name: "{{ item.name }}"
    wait: yes
    state: present
  with_items:
    - { name: "Ubuntu-Instance", ami_id: "ami-id-of-ubuntu", instance_type: "t2.micro" }
    - { name: "AmazonLinux-Instance", ami_id: "ami-id-of-amazon-linux", instance_type: "t2.micro" }
    - { name: "RedHat-Instance", ami_id: "ami-id-of-redhat", instance_type: "t2.micro" }
  register: ec2

# - name: Debug EC2 module output
#   debug:
#     var: ec2

- name: Define group mappings
  set_fact:
    group_mappings:
      Ubuntu-Instance: ubuntu
      AmazonLinux-Instance: amazon
      RedHat-Instance: redhat

- name: Collect instance IPs and add to groups
  set_fact:
    instance_ips: "{{ instance_ips | default({}) | combine({ item.tags.Name: item.network_interfaces[0].association.public_ip }) }}"
  with_items: "{{ ec2.results | map(attribute='instances') | flatten }}"
  when: item.state.name == 'running'

- name: Generate hosts.ini
  template:
    src: hosts.ini.j2
    dest: ./hosts.ini
  vars:
    ubuntu_instance_ip: "{{ instance_ips['Ubuntu-Instance'] }}"
    amazon_instance_ip: "{{ instance_ips['AmazonLinux-Instance'] }}"
    redhat_instance_ip: "{{ instance_ips['RedHat-Instance'] }}"

- name: Display instance details
  debug:
    msg: "Instance {{ item.instance_id }} with public IP {{ item.network_interfaces[0].association.public_ip }} is launched and running."
  with_items: "{{ ec2.results | map(attribute='instances') | flatten }}"
  when: item.state.name == 'running'
```

**NOTE:** Make sure to replace the `ami_id` with the correct one.

### Explanation of the role:

This role automates the process of launching EC2 instances with different AMI IDs and dynamically generates a hosts.ini file for further Ansible playbook operations. Let's break down each task in this role:

1. Define Group Mapping
    - This task sets up a dictionary called `group_mappings` that maps instance names to their respective groups (e.g., Ubuntu, Amazon Linux, Red Hat). This is used later to determine the group for each instance.

2. Collect Instance IPs and add to the group:

    - This task collects the public IP addresses of running instances and adds them to the `instance_ips` dictionary. The dictionary keys are the instance names, and the values are the public IP addresses.
    - This task uses the `set_fact` module to update the `instance_ips` dictionary with the public IP addresses of running instances.
    - The `with_items` loop iterates over the list of instances returned by the `ec2 module.
    - The `when` condition ensures that only running instances are processed.

3. Generate the `hosts.ini`:

    - Task: Uses a template to generate the hosts.ini file.
    - Template File: `hosts.ini.j2` is the source template.
    - Destination File: `hosts.ini` is the generated file.
    - Variables: Passes the IP addresses of the instances to the template.


- **vars/main.yml**

```yaml
---
key_name: "my-key-pair"         # your key-pair name
region: "ap-southeast-1"        # your preferred region
```

### 3. Security Role

**Purpose**: This role is responsible for creating the Security Group.

- Update `security/tasks/main.yml` file with these contents:

```yml
---
- name: Create security group
  amazon.aws.ec2_security_group:
    name: "{{ security_group_name }}"
    description: "{{ security_group_description }}"
    vpc_id: "{{ vpc.vpc.id }}"
    region: "{{ region }}"
    rules:
      - proto: tcp
        from_port: 22
        to_port: 22
        cidr_ip: 0.0.0.0/0
      - proto: tcp
        from_port: 80
        to_port: 80
        cidr_ip: 0.0.0.0/0
      - proto: tcp
        from_port: 443
        to_port: 443
        cidr_ip: 0.0.0.0/0
    tags:
      Name: "{{ security_group_name }}"
  register: sg
```

- **vars/main.yml**

```yml
---
security_group_name: "my_security_group"
security_group_description: "My security group for EC2 instance"
```

### 4. Keypair Role

**Purpose**: This role generates and manages the Key Pair.

- **tasks/main.yml**

```yml
---
- name: Create key pair using key_material obtained using 'file' lookup plugin
  amazon.aws.ec2_key:
    name: "{{ key_name }}"
    key_material: "{{ lookup('file', private_key_path + '.pub') }}"
  register: key_pair
```

- **vars/main.yml**

```yaml
---
key_name: "my-key-pair"
private_key_path: "~/.ssh/id_rsa" # Replace with your private key file path
```

### Step 5: Inventory file setup

We will ssh into the remote instances and install nginx. So, we need to have the ip address of the remote isntances. As we are using ansible for provisioning and launching ec2 instances, we have to dynamically populated the inventory file. To do this we will use jinja2 templating.

- Create `hosts.ini.j2` fill and fill with these contents:

```ini
[ubuntu]
ubuntu-instance ansible_host={{ ubuntu_instance_ip }} ansible_user=ubuntu

[amazon]
amazonlinux-instance ansible_host={{ amazon_instance_ip }} ansible_user=ec2-user

[redhat]
redhat-instance ansible_host={{ redhat_instance_ip }} ansible_user=ec2-user

[launched:children]
ubuntu
amazon
redhat
```
- keep the `hosts.ini` file empty. It will be dynamically populated with the correct instance IPs, ensuring the Ansible inventory is up-to-date.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2011/images/image-5.png)

    Here, we can see after running the playbook, the inventory file is automatically updated.

### Step 6: Playbook

- The `create_infra.yml` playbook is the main entry point that includes and executes all the roles to create the necessary aws infrastructure and ec2 instances

```yaml
---
- name: Create VPC, subnet, route table, internet gateway, security group, and launch EC2 instance
  hosts: localhost
  connection: local
  gather_facts: no
  roles:
    - vpc       
    - keypair   
    - security
    - instance
```

## Step 6: Run the Playbook and verify

- Navigate to the `ansible` directory and execute the playbook using the following command:

   ```sh
   cd ansible
   ansible-playbook create_infra.yml
   ```
    This command will execute the playbook and create the necessary resouces. Check any error while running the playbook. If everything is alright, you will get output something like this:

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2011/images/image.png)

- You can go to the aws console to see if all the necessary rources are created or not.

    - Check VPC:

        ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-3.png)

    - Check ec2 instance:

        ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2011/images/image-1.png)
    


So, we have done our first part of the task - creating aws infrastructure and launch ec2.


## 2. Installing and Configuring NGINX

For installing and configuring NGINX into those remote instances:

### Step 01: Ansible configuration file

Fill the ansible.cfg file with these contents:

```sh
[defaults]
inventory = hosts.ini
private_key_file = ~/.ssh/id_rsa # update the path according to your key path
host_key_checking = False
```

### Step 02: Write the Nginx installation role for different Linux distribution

- **Nginx role Purpose**: This role installs and configures Nginx web server.

- **tasks/main.yml**

```yml
---
- name: Install Python 3 on Amazon Linux
  when: ansible_os_family == "RedHat" and ansible_distribution == "Amazon"
  dnf:
    name: python3
    state: present

- name: Install Python 3 on Red Hat
  when: ansible_os_family == "RedHat" and ansible_distribution != "Amazon"
  dnf:
    name: python3
    state: present

- name: Install NGINX on Ubuntu
  when: ansible_os_family == "Debian"
  apt:
    name: nginx
    state: present
    update_cache: yes

- name: Install NGINX on Amazon Linux
  when: ansible_os_family == "RedHat" and ansible_distribution == "Amazon"
  dnf:
    name: nginx
    state: present

- name: Install NGINX on Red Hat
  when: ansible_os_family == "RedHat" and ansible_distribution != "Amazon"
  dnf:
    name: nginx
    state: present

- name: Start and enable NGINX service on Ubuntu
  when: ansible_os_family == "Debian"
  service:
    name: nginx
    state: started
    enabled: yes

- name: Start and enable NGINX service on Amazon Linux
  when: ansible_os_family == "RedHat" and ansible_distribution == "Amazon"
  service:
    name: nginx
    state: started
    enabled: yes

- name: Start and enable NGINX service on Red Hat
  when: ansible_os_family == "RedHat" and ansible_distribution != "Amazon"
  service:
    name: nginx
    state: started
    enabled: yes
```

This role installs `Python 3` and `NGINX` on different Linux distributions (Ubuntu, Amazon Linux, and Red Hat) and ensures that the NGINX service is started and enabled on boot. The tasks are conditionally executed based on the target system's operating system family and distribution, using appropriate package managers (`apt` for Ubuntu and `dnf` for Red Hat and Amazon Linux).

## Step 3: Playbook

- The `install_nginx.yml` playbook will install contain the role to install and configure nginx

```yml
---
- name: Install NGINX on different instances
  hosts: launched
  become: yes
  roles:
    - nginx
```

## Step 4: Run the playbook and verify

- Navigate to the `ansible` directory and execute the playbook using the following command:

   ```sh
   cd ansible
   ansible-playbook install_nginx.yml
   ```
    This command will execute the playbook and create the necessary resouces. Check any error while running the playbook. If everything is alright, you will get output something like this:

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2011/images/image-2.png)

- For further verification we can ssh into any instance and check the status of the nginx

    ```sh
    ssh -i "path_to_your_key" ec2-user@public_ip_of_amazon_linux
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2011/images/image-3.png)

    Here, we can see the nginx is successfully installed and running.


So we have completed our task successfully.

### Conclusion

In this tutorial, we've explored how to leverage Ansible for automating the deployment of EC2 instances with different AMI IDs and installing NGINX on these instances. By following the steps outlined, you have:

1. **Launched EC2 Instances**: Used Ansible to provision multiple EC2 instances with specific AMI IDs, demonstrating how to handle different instance types and configurations.
3. **Installed NGINX**: Applied Ansible roles to install and manage the NGINX web server across various operating systems, including Ubuntu, Amazon Linux, and Red Hat.

Feel free to expand upon this foundational setup by integrating additional features or automating other tasks.

