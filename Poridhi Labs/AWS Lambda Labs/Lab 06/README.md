
# **Automated EC2 Deployment & MySQL Management with Lambda & API Gateway**

This guide explains how to deploy an EC2 instance with MySQL using AWS Lambda and API Gateway, ensuring proper permissions and security settings. It also includes Lambda functions for creating and fetching users in the MySQL database, along with steps to add a custom layer for `pymysql`.

Automating EC2 instance deployment with MySQL using AWS Lambda and API Gateway simplifies infrastructure management. This serverless approach enables dynamic provisioning, efficient database operations, and secure API access. It’s ideal for applications requiring on-demand database instances, scalable cloud environments, and automated infrastructure setups.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/1.svg)

## **1. Setting Up the Network Environment**  

Before deploying the EC2 instance, you need to create a VPC with the necessary networking components for internet access and communication. Follow these steps:  

- **Create a VPC** with a CIDR block (e.g., `10.0.0.0/16`).  
- **Create a Public Subnet** within the VPC (e.g., `10.0.0.0/24`).  
- Go to subnet settings and **Enable Auto-Assign Public IP** for the subnet.  
- **Create an Internet Gateway (IGW)** and attach it to the VPC.  
- **Create a Route Table** within this VPC.
- Associate **Route Table** with the public subnet.  
- **Add a Route** in the route table to direct `0.0.0.0/0` traffic to the IGW.  

- Go to your VPC and see the resource map as follows: 

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-18.png)


## 2. Set Up Required IAM Roles

### A. Create Lambda Execution Role
1. Create a custom policy to allow `iam:PassRole` for EC2 using the following JSON configuration:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "iam:PassRole",
                "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/EC2SSMRole"
            }
        ]
    }
    ``` 
    Replace the `<ACCOUNT_ID>` with your AWS account Id.
    Save the policy naming it `EC2PassRolePolicy`. 


2. Go to IAM Console → Roles → Create Role
3. Select "AWS Service" and choose "Lambda"
4. Attach the following policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEC2FullAccess`
   - `AmazonSSMFullAccess`
   - **Custom policy**: `EC2PassRolePolicy`
   
5. Name it `LambdaEC2DeploymentRole` and create the role.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-19.png)

### B. Create EC2 Role
1. Go to IAM Console → Roles → Create Role
2. Select "AWS Service" and choose "EC2"
3. Attach the following policies:
   - `AmazonSSMManagedInstanceCore`
   - `AmazonEC2FullAccess`
4. Name it `EC2SSMRole` and create the role.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-20.png)



## 3. Create Security Group
1. Navigate to EC2 Console → Security Groups → Create Security Group
2. Name it `MySQL-EC2-SG`
3. Add inbound rules:
   - **Type:** MySQL/Aurora (Port 3306) → **Source:** Anywhere-IPv4
   - **Type:** SSH (Port 22) → **Source:** Anywhere-IPv4

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-21.png)

4. Click **Create security group**.

## 4. Create Key Pair
1. Go to EC2 Console → Key Pairs → Create Key Pair
2. Name it `mysql-ec2-key`
3. Choose RSA and `.pem` format.
4. Click **Create key pair**.
4. Then download the key.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-22.png)


## 5. Create Lambda Function for EC2 Deployment
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `EC2MySQLDeployment`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaEC2DeploymentRole`
4. Set timeout to **9 minutes** in Configuration → General Configuration
5. Replace the code in the Lambda function with:

```python
import json
import boto3
import time
from botocore.exceptions import ClientError, WaiterError
def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    instance_params = {
        'ImageId': 'ami-0198a868663199764',  # Ubuntu 22.04 LTS AMI
        'InstanceType': 't2.micro',
        'MinCount': 1,
        'MaxCount': 1,
        'SecurityGroupIds': ['sg-0320080753abca516'],
        'SubnetId': 'subnet-033daf6f9aaac9520',
        'KeyName': 'mysql-ec2-key',
        'IamInstanceProfile': {'Name': 'SSMRole'},
        'UserData': '''#!/bin/bash
            # Update and install MySQL
            apt update -y
            DEBIAN_FRONTEND=noninteractive apt install -y mysql-server
            
            # Start MySQL service
            systemctl start mysql
            systemctl enable mysql
            
            # Secure MySQL installation
            mysql --execute="ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'MySecurePassword123';"
            mysql --execute="DELETE FROM mysql.user WHERE User='';"
            mysql --execute="DROP DATABASE IF EXISTS test;"
            mysql --execute="FLUSH PRIVILEGES;"
            
            # Create database and user with mysql_native_password
            mysql --user=root --password=MySecurePassword123 --execute="CREATE DATABASE myapp;"
            mysql --user=root --password=MySecurePassword123 --execute="CREATE USER 'myappuser'@'%' IDENTIFIED WITH mysql_native_password BY 'MyAppPassword123';"
            mysql --user=root --password=MySecurePassword123 --execute="GRANT ALL PRIVILEGES ON myapp.* TO 'myappuser'@'%';"
            mysql --user=root --password=MySecurePassword123 --execute="FLUSH PRIVILEGES;"
            
            # Configure MySQL for remote access
            cat > /etc/mysql/mysql.conf.d/mysqld.cnf << EOF
[mysqld]
user            = mysql
pid-file        = /var/run/mysqld/mysqld.pid
socket          = /var/run/mysqld/mysqld.sock
port            = 3306
basedir         = /usr
datadir         = /var/lib/mysql
tmpdir          = /tmp
bind-address    = 0.0.0.0
default_authentication_plugin = mysql_native_password
EOF
            # Restart MySQL and configure firewall
            systemctl restart mysql
            ufw allow 22
            ufw allow 3306
            echo "y" | ufw enable
            
            # Create a file to indicate completion
            echo "MySQL setup completed" > /var/log/mysql_setup_complete
        '''.encode('utf-8')
    }
    
    try:
        response = ec2.run_instances(**instance_params)
        instance_id = response['Instances'][0]['InstanceId']
        
        try:
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={'Delay': 5, 'MaxAttempts': 20}
            )
            
            instance_info = ec2.describe_instances(InstanceIds=[instance_id])
            public_ip = instance_info['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'Not assigned yet')
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'EC2 instance with MySQL created successfully.',
                    'instance_id': instance_id,
                    'public_ip': public_ip,
                    'mysql_user': 'myappuser',
                    'mysql_password': 'MyAppPassword123',
                    'mysql_database': 'myapp',
                    'status': 'INITIALIZING',
                    'next_steps': [
                        'Wait ~5 minutes for MySQL installation to complete',
                        f'SSH into instance: ssh -i mysql-ec2-key.pem ubuntu@{public_ip}',
                        'Verify MySQL status: sudo systemctl status mysql',
                        f'Test remote connection: mysql -h {public_ip} -u myappuser -pMyAppPassword123 myapp',
                        'Check setup completion: cat /var/log/mysql_setup_complete'
                    ],
                    'configuration_details': {
                        'authentication_method': 'mysql_native_password',
                        'remote_access': 'enabled',
                        'bind_address': '0.0.0.0',
                        'ports_opened': ['22 (SSH)', '3306 (MySQL)']
                    }
                })
            }
            
        except WaiterError:
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'EC2 instance created but still initializing',
                    'instance_id': instance_id,
                    'status': 'INITIALIZING'
                })
            }
            
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

Replace the `ImageId`, `SecurityGroupIds`, `SubnetId` in `instance_params` with valid values.

6. Click **Deploy**.

7. Test the lambda function
    - Go to **Test** tab
    - Create a test event **test** with empty event json:
        ```json
        {}
        ```
    - Click **Save** then click **Test**

    - You will see a EC2 creation was successful and MySQL was installed successfully.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image.png)         

## 6. Create Lambda Functions for MySQL Operations

### A. Create `create_user` Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `create_user`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaEC2DeploymentRole`

4. Set timeout to **5 minutes** in Configuration → General Configuration   
5. Replace the code with:

```python
import pymysql
import json
# MySQL Configuration
DB_HOST = "47.129.98.20"  # Replace with your EC2 public IP
DB_USER = "myappuser"
DB_PASSWORD = "MyAppPassword123"
DB_NAME = "myapp"
def lambda_handler(event, context):
    try:
        # Connect to MySQL
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, connect_timeout=5)
        cursor = conn.cursor()
        # Create Table
        create_table_sql = """CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        )"""
        cursor.execute(create_table_sql)
        # Insert User
        insert_user_sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
        user_data = ("John Doe", "john.doe@example.com")
        cursor.execute(insert_user_sql, user_data)
        # Commit changes and close connection
        conn.commit()
        cursor.close()
        conn.close()
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'User table created and user added successfully'})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
```

Replace the `DB_HOST` value with your EC2 instance public IP.

6. Click **Deploy**.

### B. Create `fetch_user` Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `fetch_user`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaEC2DeploymentRole`

4. Set timeout to **5 minutes** in Configuration → General Configuration   
5. Replace the code with:

```python
import pymysql
import json
# MySQL Configuration
DB_HOST = "47.129.98.20"  # Replace with your EC2 public IP
DB_USER = "myappuser"
DB_PASSWORD = "MyAppPassword123"
DB_NAME = "myapp"
def lambda_handler(event, context):
    try:
        # Connect to MySQL
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, connect_timeout=5)
        cursor = conn.cursor()
        # Fetch data
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        # Close connection
        cursor.close()
        conn.close()
        return {
            'statusCode': 200,
            'body': json.dumps({'users': users})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
```

Replace the `DB_HOST` value with your EC2 instance public IP.

6. Click **Deploy**.


## 7. Add a Custom Layer for `pymysql`

### Steps to Create and Attach a Custom Layer

1. **Install `pymysql` Locally:**

   - Create a directory named `python`:

     ```bash
     mkdir -p python/lib/python3.9/site-packages
     ```
   - Install `pymysql` into the directory:

     ```bash
     pip install pymysql -t python/lib/python3.9/site-packages
     ```
   - Zip the `python` folder:

     ```bash
     zip -r pymysql_layer.zip python
     ```

2. **Upload the Layer to AWS Lambda:**
   - Go to AWS Lambda Console → Layers → Create Layer.
   - Name the layer `pymysql_layer`.
   - Upload the `pymysql_layer.zip` file.
   - Choose compatible runtimes (e.g., Python 3.9).

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-16.png)

   - Click **Create**.

3. **Attach the Layer to Lambda Functions:**
   - Go to each Lambda function (`create_user` and `fetch_user`).
   - Scroll to the **Layers** section and click **Add a layer**.
   - Select **Custom layers** and choose `pymysql_layer`.
   - Select available version.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-17.png)

   - Click **Add**.

## 8. Test `create_user` and `fetch_user` lambda functions

1. Test the `create_user` lambda function

    - Go to `create_user` lambda function
    - Go to **Test** tab
    - Create a test event **test** with empty event json:
        ```json
        {}
        ```
    - Click **Save** then click **Test**

    - You will see a new user and user table has been created successfully.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-1.png)


2. Test the `fetch_user` lambda function

    - Go to `fetch_user` lambda function
    - Go to **Test** tab
    - Create a test event **test** with empty event json:
        ```json
        {}
        ```
    - Click **Save** then click **Test**

    - You will see demo users from the user table.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-2.png)


## 9. Create API Gateway
1. Go to API Gateway Console → Create API → **REST API**
2. Name it `My-REST-API`.
3. Create resources `/deploy`, `/create-user`, and `/fetch-user`.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-3.png)

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-4.png)

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-5.png)

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-6.png)

4. Add methods:
   - **POST** for `/deploy` → Integration type: **Lambda Function** → Select `EC2MySQLDeployment`
   - **POST** for `/create-user` → Integration type: **Lambda Function** → Select `create_user`
   - **GET** for `/fetch-user` → Integration type: **Lambda Function** → Select `fetch_user`

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-7.png)

5. Deploy API → Create a new stage `prod`

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-8.png)

6. Test the endpoints:

     You can get the invoke url from the **Stages** of your REST API. 

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-9.png)

    - Deploy EC2 instance:
        
        Replace `<Invoke URL>` with the invoke url your API.

        ```bash
        curl -X POST <Invoke URL>/deploy
        ```

        Expected output:

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-10.png)

        Copy the IP address of your EC2 instance.

    Before using the following command, change the EC2 IP address in your `create_user` and `fetch_user` lambda functions and deploy again.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-11.png)

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-12.png)

    - Create a user:

        Replace `<Invoke URL>` with the invoke url your API
        ```bash
        curl -X POST <Invoke URL>/create-user
        ```

        Expected output:

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-13.png)

    - Fetch users:

        Replace `<Invoke URL>` with the invoke url your API.
        ```bash
        curl -X GET <Invoke URL>/fetch-user
        ```

        Expected output:

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-14.png)



## 10. Testing & Troubleshooting

### Verify EC2 Instance
1. Go to EC2 Console → Check for running instances

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2006/images/image-15.png)

2. Get **Public IP** and connect:
   ```bash
   ssh -i mysql-ec2-key.pem ubuntu@EC2_PUBLIC_IP
   ```
3. Test MySQL:
   ```bash
   mysql -u myappuser -p  # Password: MyAppPassword123
   ```


## Conclusion  

In this guide, we successfully automated the deployment of an EC2 instance with MySQL using AWS Lambda and API Gateway. We also implemented Lambda functions for database operations, ensuring secure and efficient user management. This approach streamlines infrastructure provisioning while maintaining flexibility and scalability for cloud-based applications.
 