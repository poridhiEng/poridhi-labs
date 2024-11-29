# AWS Infrastructure Deployment with Ansible

This lab guides you through the process of automating the deployment of an AWS VPC, Subnet, Internet Gateway, Route Table, Security Group, Key Pair, and EC2 Instance using Ansible.

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image.png)

## Project Structure

The project is organized into the following directories and files:

```sh
ansible/
├── create_infra.yml
```

## Prerequisite: Ansible Installed in your control node.

To install Ansible on an Ubuntu machine, run these commands:

```sh
sudo apt-get update -y
sudo apt install software-properties-common -y
sudo apt-add-repository --yes --update ppa:ansible/ansible
sudo apt-get install -y ansible
```

Check the Ansible version to verify the installation:

![Check Ansible Version](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2001/images/image-1.png)

## Step by step guide

## Step 01: Install Required Dependencies

- We will require `boto3` and `botocore` libraries. We can install them using pip:

    ```sh
    pip install boto3 botocore
    ```
    - **Boto3**

    Boto3 is the Amazon Web Services (AWS) Software Development Kit (SDK) for Python. It provides a high-level, object-oriented API as well as low-level direct access to AWS services. Boto3 makes it easy to integrate AWS services with Python applications.

    - **Botocore**

    Botocore is the low-level foundation library for Boto3. It provides the core functionality for making raw HTTP requests to AWS services. While Boto3 is built on top of Botocore, the latter can be used independently for more granular control over AWS interactions.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-1.png)

- Install amazon aws collection

    ```sh
    ansible-galaxy collection install amazon.aws
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-2.png)
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

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-3.png)


## Step 03: Create the key pair for the EC2 instance

- Run this command to create key-pair:

    ```sh
    ssh-keygen
    ```
    This will create a keypair( public-key and private-key ) in the `~/.ssh/` directory.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-4.png)

    We will use the public-key for instance creation and private key for ssh.

## Step 4: Playbook

The `create_infra.yml` file is the main entry point that includes and executes all the roles.

```yml
---
- name: Create VPC, subnet, route table, internet gateway and launch EC2 instance
  hosts: localhost
  connection: local
  gather_facts: no
  vars:
    vpc_cidr_block: "10.0.0.0/16"
    subnet_cidr_block: "10.0.1.0/24"
    region: "ap-southeast-1"     # Replace with the your preferred region
    ami: "ami-060e277c0d4cce553" # Replace with your preferred AMI ID
    instance_type: "t2.micro"
    key_name: "my-key-pair"
    security_group_name: "my_security_group"
    security_group_description: "My security group for EC2 instance"
    private_key_path: "/root/.ssh/id_rsa" # Replace with your key path

  tasks:
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

    - name: Create key pair using key_material obtained using 'file' lookup plugin
      amazon.aws.ec2_key:
        name: "{{ key_name }}"
        key_material: "{{ lookup('file', private_key_path + '.pub') }}"
      register: key_pair

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

### Explanation of the Playbook

This Ansible playbook is designed to automate the creation of AWS infrastructure, Here’s a detailed breakdown of each part of the playbook:

1. **Create VPC**: Establish a new VPC with the specified CIDR block and region, and tag it.

2. **Create Subnet**: Add a subnet to the VPC using the provided CIDR block, and tag it.

3. **Create Internet Gateway**: Create and attach an internet gateway to the VPC, and tag it.

4. **Set Up Route Table**: Create a route table, associate it with the subnet, and add a route to direct traffic to the internet gateway. Tag the route table.

5. **Create Security Group**: Define a security group with rules for SSH, HTTP, and HTTPS access, and tag it.

6. **Create Key Pair**:
    - Uses the `amazon.aws.ec2_key` module to create a key pair using the public key material obtained from the specified file path.

7. **Launch EC2 Instance**:
    - Uses the `amazon.aws.ec2_instance` module to launch an EC2 instance with the specified AMI, instance type, key pair, and security group.
    - Assigns a public IP address to the instance.
    - Tags the instance with the name `my_instance`.
    - Waits for the instance to be running before proceeding.
    - Registers the EC2 instance information.

8. **Output Instance Information**:
    - Uses the `debug` module to print the EC2 instance ID and public IP address.

## Step 5: Run the Playbook

- Navigate to the `ansible` directory and execute the playbook using the following command:

   ```sh
   cd ansible
   ansible-playbook create_infra.yml
   ```
    This command will execute the playbook and create the necessary resouces. Check any error while running the playbook. If everything is alright, you will get output something like this:

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-5.png)

## Verification

- You can go to the aws console to see if all the necessary rources are created or not.

    - Check VPC:

        ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-7.png)

    - Check ec2 instance:

       ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-6.png)


- As we have the private key in our local machine, we can ssh into the instance that we have created:

    ```sh
    ssh -i ~/.ssh/id_rsa ubuntu@public_instance_ip
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2009/images/image-8.png)

So, we have successfully completed the task.

---

### Conclusion

In this lab, we have walked through the process of using Ansible to automate the provisioning of AWS infrastructure.