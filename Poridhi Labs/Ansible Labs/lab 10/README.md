# AWS Infrastructure Deployment with Ansible (Role-based)

In the previous lab, we have created the AWS infrastucture (AWS VPC, Subnet, Internet Gateway, Route Table, Security Group, Key Pair, and EC2 Instance) using Ansible using a single playbook. Now in this lab we will organize the infrastucture into distinct roles to ensure modularity and ease of management.

<!-- ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-6.png) -->


![](./images/arch.drawio.svg)

## Project Structure

The project is organized into the following directories and files:

```sh
ansible/
├── roles/
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

```

You can create the directories and files using the following `mkdir` and `touch` commands. Run this command from your project's root directory:

```sh
mkdir -p roles/vpc/tasks roles/vpc/vars \
         roles/instance/tasks roles/instance/vars \
         roles/security/tasks roles/security/vars \
         roles/keypair/tasks roles/keypair/vars

touch roles/vpc/tasks/main.yml roles/vpc/vars/main.yml \
      roles/instance/tasks/main.yml roles/instance/vars/main.yml \
      roles/security/tasks/main.yml roles/security/vars/main.yml \
      roles/keypair/tasks/main.yml roles/keypair/vars/main.yml
```

### Explanation:
- `mkdir -p` creates the directories, including parent directories as needed.
- `touch` creates the empty `main.yml` files in each `tasks` and `vars` directory.

## Step by step guide:

## Step 01: Install Required Dependencies

- We will require `boto3` and `botocore` libraries. We can install them using pip:

    ```sh
    pip install boto3 botocore
    ```
    - **Boto3**

    Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python. It provides a high-level, object-oriented API as well as low-level direct access to AWS services. Boto3 makes it easy to integrate AWS services with Python applications.

    - **Botocore**

    Botocore is the low-level foundation library for Boto3. It provides the core functionality for making raw HTTP requests to AWS services. While Boto3 is built on top of Botocore, the latter can be used independently for more granular control over AWS interactions.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-7.png)

- Install amazon aws collection

    ```sh
    ansible-galaxy collection install amazon.aws
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-8.png)

## Step 02: Set Up AWS Configuration

Now We need to configure our AWS credentials. We can do this by using the AWS credentials file.

- First ensure you have aws cli installed. If not, you can install it using pip:

    ```sh
    pip install awscli
    aws --version
    ```
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


## Step 03: Create the key pair for the EC2 instance

- Run this command to create key-pair:

    ```sh
    ssh-keygen
    ```
    This will create a keypair( public-key and private-key ) in the `~/.ssh/` directory.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-1.png)

    We will use the public-key for instance creation and private key for ssh.

## Step 04: Create Roles to organize the tasks

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
vpc_cidr_block: "10.0.0.0/16"
subnet_cidr_block: "10.0.1.0/24"
region: "ap-southeast-1"
```

### 2. Instance Role

**Purpose**: This role manages the launching of the EC2 instances.

- Update the `instance/tasks/main.yml` file with these contents:

```yml
---
- name: Launch EC2 instance
  amazon.aws.ec2_instance:
    name: my_instance
    key_name: "{{ key_name }}"
    instance_type: "{{ instance_type }}"
    image_id: "{{ ami }}"
    region: "{{ region }}"
    vpc_subnet_id: "{{ subnet.subnet.id }}"
    security_group: "{{ sg.group_id }}"
    network:
      assign_public_ip: true
    wait: yes
    tags:
      Name: my_instance
  register: ec2_instance

- name: Output instance information
  debug:
    msg: "EC2 instance launched with ID: {{ ec2_instance.instance_ids[0] }} and Public IP: {{ ec2_instance.instances[0].public_ip_address }}"
```

- **vars/main.yml**

```yaml
---
ami: "ami-060e277c0d4cce553"  # Replace with your preferred AMI ID
instance_type: "t2.micro"     # Replace with your instance type
key_name: "my-key-pair"       # Your key name   
region: "ap-southeast-1"      # region  
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

## Step 5: Playbook

The `create_infra.yml` file is the main entry point that includes and executes all the roles.

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


## Step 6: Run the Playbook

- Navigate to the `ansible` directory and execute the playbook using the following command:

   ```sh
   cd ansible
   ansible-playbook create_infra.yml
   ```
    This command will execute the playbook and create the necessary resouces. Check any error while running the playbook. If everything is alright, you will get output something like this:

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-2.png)

## Verification

- You can go to the aws console to see if all the necessary rources are created or not.

    - Check VPC:

        ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-3.png)

    - Check ec2 instance:

        ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-4.png)


- As we have the private key in our local machine, we can ssh into the instance that we have created:

    ```sh
    ssh -i ~/.ssh/id_rsa ubuntu@public_instance_ip
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2010/images/image-5.png)

So, we have successfully completed the task.

---

### Conclusion

In this lab, we have walked through the process of using Ansible to automate the provisioning of AWS infrastructure. We have organized the playbook into roles as Ansible roles improve automation by organizing tasks, promoting reusability, and simplifying complex configurations. They enhance collaboration, testing, and maintainability while making playbooks cleaner and more efficient.