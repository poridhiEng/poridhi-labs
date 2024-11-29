# AWS Infrastructure Deployment with Ansible

This lab guides you through the process of automating the deployment of an AWS VPC, Subnet, Internet Gateway, Route Table using Ansible.

![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2008/images/image.png)

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

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2008/images/image-1.png)

- Install amazon aws collection

    ```sh
    ansible-galaxy collection install amazon.aws
    ```

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2008/images/image-2.png)
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

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2008/images/image-3.png)

## Step 3: Playbook

The `create_infra.yml` file is the main entry point that includes and executes all the roles.

```yml
---
- name: Create VPC, subnet, route table, internet gateway
  connection: local
  gather_facts: no
  vars:
    vpc_cidr_block: "10.0.0.0/16"
    subnet_cidr_block: "10.0.1.0/24"
    region: "ap-southeast-1"
    ami: "ami-060e277c0d4cce553" # Replace with your preferred AMI ID
    instance_type: "t2.micro"
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
```

### Explanation of the Playbook

This Ansible playbook is designed to automate the creation of AWS infrastructure Here’s a detailed breakdown of each part of the playbook:

1. **Create VPC**:
    - Uses the `amazon.aws.ec2_vpc_net` module to create a VPC with the specified CIDR block and region.
    - Tags the VPC with the name `my_vpc`.
    - Registers the VPC information for use in subsequent tasks.

2. **Create Subnet**:
    - Uses the `amazon.aws.ec2_vpc_subnet` module to create a subnet within the VPC.
    - Specifies the VPC ID, CIDR block, and region.
    - Tags the subnet with the name `my_subnet`.
    - Registers the subnet information.

3. **Create Internet Gateway**:
    - Uses the `amazon.aws.ec2_vpc_igw` module to create an internet gateway and attach it to the VPC.
    - Tags the internet gateway with the name `my_igw`.
    - Registers the internet gateway information.

4. **Set Up Public Subnet Route Table**:
    - Uses the `amazon.aws.ec2_vpc_route_table` module to create a route table for the VPC.
    - Associates the subnet with the route table.
    - Adds a route that directs traffic to the internet gateway for any destination (`0.0.0.0/0`).
    - Tags the route table with the name `Public-route-table`.
    - Registers the route table information.


## Step 4: Run the Playbook

- Navigate to the `ansible` directory and execute the playbook using the following command:

   ```sh
   cd ansible
   ansible-playbook create_infra.yml
   ```
    This command will execute the playbook and create the necessary resouces. Check any error while running the playbook. If everything is alright, you will get output something like this:

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2008/images/image-5.png)

## Verification

- You can go to the aws console(VPC) to see if all the necessary rources are created or not.

    ![alt text](https://github.com/Konami33/Ansible-Labs/raw/main/lab%2008/images/image-7.png)

So, we have successfully completed the task.

---

### Conclusion

In this lab, we have walked through the process of using Ansible to automate the provisioning of AWS infrastructure.