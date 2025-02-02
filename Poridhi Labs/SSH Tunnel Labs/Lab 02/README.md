# Local Port Forwarding with Bastion Host

In cloud environments, it is common to have resources deployed in private subnets that are not directly accessible from the internet. To securely access these resources, a bastion host (also known as a jump box) is used. A bastion host resides in a public subnet and acts as an intermediary for accessing resources in private subnets.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/2.svg)


Local Port Forwarding is a SSH tunneling technique that allows you to securely access services in a private network through an intermediate server (Bastion Host). This lab demonstrates how to access a MySQL server in a private subnet through a bastion host in a public subnet.



### Architecture Overview

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/1.svg)

- Public Subnet: Contains the Bastion Host (Jump Server)
- Private Subnet: Contains the MySQL Server
- The Bastion Host acts as a secure gateway to access the private subnet
- SSH tunneling is used to forward local ports to the remote MySQL server

## Prerequisites
- AWS Account with appropriate permissions
- SSH key pair
- Basic understanding of VPC networking
- MySQL client installed on your local machine



## Task Description
You will:
1. Deploy the infrastructure using Pulumi
2. Configure MySQL on the private instance
3. Set up SSH local port forwarding
4. Connect to MySQL through the tunnel
5. Verify the setup





## **Step-by-Step Implementation**


### **Step 1. AWS CLI Configuration**

Run the following command to configure AWS CLI:

```bash
aws configure
```

This command prompts you for your AWS Access Key ID, Secret Access Key, region, and output format.


###  **Step 2: Set Up a Pulumi Project**

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/3.svg)

#### **Set Up a new directory**
Create a new directory for your project and navigate into it:

```sh
mkdir aws-pulumi-infra
cd aws-pulumi-infra
```

#### **Install python `venv`**

```sh 
sudo apt update
sudo apt install python3.8-venv -y
```

#### **Initialize a New Pulumi Project**
Run the following command to create a new Pulumi project:

```sh
pulumi new aws-python
```
Follow the prompts to set up your project.


#### **Create Key Pair**

Create a new key pair for our instances using the following command:

```sh
aws ec2 create-key-pair --key-name key-pair-poridhi-poc --query 'KeyMaterial' --output text > key-pair-poridhi-poc.pem
```

These commands will create key pair for our instances.

#### **Set File Permissions of the key files**
```sh
chmod 400 key-pair-poridhi-poc.pem
```

#### **Infrastructure Components**
1. VPC (10.0.0.0/16)
2. Public Subnet (10.0.1.0/24)
3. Private Subnet (10.0.2.0/24)
4. Internet Gateway
5. NAT Gateway
6. Route Tables
7. Security Groups
8. EC2 Instances (Bastion Host and MySQL Server)

Now, **Open `__main__.py` file in your project directory**:

```python

import pulumi
import pulumi_aws as aws

# Create a VPC
vpc = aws.ec2.Vpc("my-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_support=True,
    enable_dns_hostnames=True
)

# Create an Internet Gateway
internet_gateway = aws.ec2.InternetGateway("my-igw",
    vpc_id=vpc.id
)

# Create a Public Subnet
public_subnet = aws.ec2.Subnet("public-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    map_public_ip_on_launch=True
)

# Create a Private Subnet
private_subnet = aws.ec2.Subnet("private-subnet",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    map_public_ip_on_launch=False
)

# Create a Route Table for the Public Subnet
public_route_table = aws.ec2.RouteTable("public-route-table",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(
        cidr_block="0.0.0.0/0",
        gateway_id=internet_gateway.id,
    )]
)

# Associate the Public Subnet with the Public Route Table
public_route_table_association = aws.ec2.RouteTableAssociation("public-route-table-association",
    subnet_id=public_subnet.id,
    route_table_id=public_route_table.id
)

# Create a route table for the private subnet
private_route_table = aws.ec2.RouteTable("private-route-table",
    vpc_id=vpc.id,
    tags={
        "Name": "my-private-route-table"
    }
)

# Allocate an Elastic IP for the NAT Gateway
eip = aws.ec2.Eip("nat-eip", vpc=True)

# Create the NAT Gateway
nat_gateway = aws.ec2.NatGateway("nat-gateway",
    subnet_id=public_subnet.id,
    allocation_id=eip.id,
    tags={
        "Name": "my-nat-gateway"
    }
)

# Create a route in the route table for the NAT Gateway
private_route = aws.ec2.Route("nat-route",
    route_table_id=private_route_table.id,
    destination_cidr_block="0.0.0.0/0",
    nat_gateway_id=nat_gateway.id
)

# Associate the route table with the private subnet
private_route_table_association = aws.ec2.RouteTableAssociation("private-route-table-association",
    subnet_id=private_subnet.id,
    route_table_id=private_route_table.id
)

# Create a Security Group for the Bastion Host
bastion_sg = aws.ec2.SecurityGroup("bastion-sg",
    vpc_id=vpc.id,
    description="Allow SSH from all IPs",
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["0.0.0.0/0"],  # Allow SSH from anywhere
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
)

# Create a Security Group for the MySQL Server
mysql_sg = aws.ec2.SecurityGroup("mysql-sg",
    vpc_id=vpc.id,
    description="Allow SSH from Bastion Host and MySQL from Bastion Host",
    ingress=[
        # Allow SSH from the Bastion Host
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            security_groups=[bastion_sg.id],  # Restrict SSH to the Bastion Host
        ),
        # Allow MySQL from the Bastion Host
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=3306,
            to_port=3306,
            security_groups=[bastion_sg.id],  # Restrict MySQL to the Bastion Host
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            protocol="-1",
            from_port=0,
            to_port=0,
            cidr_blocks=["0.0.0.0/0"],  # Allow all outbound traffic
        ),
    ],
)

# Create the Bastion Host in the Public Subnet
bastion_host = aws.ec2.Instance("bastion-host",
    instance_type="t2.micro",
    ami="ami-0672fd5b9210aa093",  # Replace with your desired AMI ID
    vpc_security_group_ids=[bastion_sg.id],
    subnet_id=public_subnet.id,
    key_name="key-pair-poridhi-poc",  # Replace with your key pair name
    tags={
        "Name": "bastion-host",
    }
)

# Create the MySQL Server in the Private Subnet
mysql_server = aws.ec2.Instance("mysql-server",
    instance_type="t2.micro",
    ami="ami-0672fd5b9210aa093",  # Replace with your desired AMI ID
    vpc_security_group_ids=[mysql_sg.id],
    subnet_id=private_subnet.id,
    key_name="key-pair-poridhi-poc",  # Replace with your key pair name
    tags={
        "Name": "mysql-server",
    }
)

# Output the Public IP of the Bastion Host
pulumi.export("bastion_host_public_ip", bastion_host.public_ip)

# Output the Private IP of the MySQL Server
pulumi.export("mysql_server_private_ip", mysql_server.private_ip)
```


#### **Preview the deployment plan**

To preview the deployment plan, run the following command:

```bash
pulumi preview
```

This will show all the components ready to be deployed and provisioned.

#### **Deploy the Pulumi Stack**

Deploy the stack using the following command:

```sh
pulumi up
```
Review the changes and confirm by typing "yes".


#### **Verify the Deployment**

You can varify the creteated resources such as VPC, Subnet, EC2 instance using AWS console.


- VPC resource map:

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/image-1.png)

- EC2 instances:

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/image.png)








### **Step 3. Configure MySQL Server**

- Connect to bastion host:

    ```bash
    ssh -i <key-pair.pem> ubuntu@<bastion-public-ip>
    ```

- Create a file to copy the ssh key in the bastion server:
    ```bash
    vi key.pem
    ```

    Copy the SSH key and paste it into the key.pem file.

- Set permissions:

    ```bash
    chmod 400 key.pem
    ```

- Connect to MySQL server through bastion:
    ```bash
    ssh -i key.pem ubuntu@<mysql-private-ip>
    ```

- Install and configure MySQL:
    ```
    sudo apt update -y
    sudo apt install -y mysql-server
    sudo systemctl start mysql
    sudo systemctl enable mysql
    ```

- Secure MySQL installation:
    ```bash
    sudo mysql_secure_installation
    ```

- Log in to MySQL:
   ```bash
   sudo mysql -u root -p
   ```
   Press `Enter` when prompted for password.

- Create a database and user:

    Using the CIDR range of your public subnet. The private IP address of my bastion server is `10.0.1.102`. 

    ```sql
    CREATE DATABASE demo_db;
    CREATE USER 'demo_user'@'10.0.1.%' IDENTIFIED BY 'password';
    GRANT ALL PRIVILEGES ON *.* TO 'demo_user'@'10.0.1.%';
    FLUSH PRIVILEGES;
    EXIT;
    ```


- Log in as the new user:

   ```bash
   mysql -u demo_user -p
   ```
   Type `password` to login as the demo_user.

- Verify access to the database:

   ```sql
   USE demo_db;
   CREATE TABLE test_table (id INT, name VARCHAR(50));
   INSERT INTO test_table VALUES (1, 'Test Data');
   SELECT * FROM test_table;
   ```

- Check MySQL bind address:

    ```bash
    sudo vi /etc/mysql/mysql.conf.d/mysqld.cnf
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/image-3.png)

    Make sure the bind-address is set to `0.0.0.0` to allow remote connections:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/image-4.png)

- Reload the database:
   ```bash
   sudo systemctl restart mysql
   ```   


### **Step 3. Set Up Local Port Forwarding**

- Create SSH tunnel by running the following command from your local machine:
    ```bash
    ssh -i <key-pair.pem> -L 3306:<mysql-private-ip>:3306 ec2-user@<bastion-public-ip>
    ```

    This command creates a tunnel where:
    - `-L`: Specifies local port forwarding
    - `3306`: Local port on your machine
    - `<mysql-private-ip>:3306`: Remote MySQL server address and port
    - `ec2-user@<bastion-public-ip>`: Bastion host connection details

    For example, in our case: 

    ```bash
    ssh -v -i key-pair-poridhi-poc.pem -L 3306:10.0.2.69:3306 ubuntu@18.140.69.244
    ```

    How it works:

    ![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/4.svg)


### **Step 4. Connect to MySQL Through Tunnel**

1. Open a new terminal window.
2. Install the MySQL Client:

   ```bash
   sudo apt update
   sudo apt install mysql-client -y
   ```

2. Connect to the MySQL database using the tunnel:
   ```bash
   mysql -u demo_user -p -h 127.0.0.1 -P 3306
   ```

   Here password is `password`.

3. Verify access to the database:
   ```sql
   USE demo_db;
   SELECT * FROM test_table;
   ```

   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/SSH%20Tunnel%20Labs/Lab%2002/images/image-2.png)


## Cleanup

Terminate infrastructure

```bash
pulumi destroy
```



## Conclusion

By implementing Local Port Forwarding with a Bastion Host, we successfully established a secure method to access a MySQL server in a private subnet. This approach enhances security by restricting direct access to private resources while allowing controlled connectivity through SSH tunneling. By automating the infrastructure setup with Pulumi, we streamlined deployment and management, making it efficient and scalable for cloud environments.