

---

# **Automating EC2 Instance Deployment and PostgreSQL Database Operations with AWS Lambda & API Gateway**

This guide explains how to deploy an EC2 instance with PostgreSQL using AWS Lambda and API Gateway, ensuring proper permissions and security settings. It also includes Lambda functions for creating and fetching users in the PostgreSQL database, along with steps to add a custom layer for `psycopg2`.

---

## 1. Set Up Required IAM Roles

### A. Create Lambda Execution Role
1. Go to IAM Console → Roles → Create Role
2. Select "AWS Service" and choose "Lambda"
3. Attach the following policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEC2FullAccess`
   - `AmazonSSMFullAccess`
   - **Custom policy** (to allow `iam:PassRole` for EC2)
4. Create a custom policy with the following JSON and attach it:
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
5. Name it `LambdaEC2DeploymentRole` and create the role.

### B. Create EC2 Role
1. Go to IAM Console → Roles → Create Role
2. Select "AWS Service" and choose "EC2"
3. Attach the following policies:
   - `AmazonSSMManagedInstanceCore`
   - `AmazonEC2FullAccess`
4. Name it `EC2SSMRole` and create the role.

---

## 2. Create Security Group
1. Navigate to EC2 Console → Security Groups → Create Security Group
2. Name it `PostgreSQL-EC2-SG`
3. Add inbound rules:
   - **Type:** PostgreSQL (Port 5432) → **Source:** Your IP
   - **Type:** SSH (Port 22) → **Source:** Your IP

---

## 3. Create Key Pair
1. Go to EC2 Console → Key Pairs → Create Key Pair
2. Name it `postgres-ec2-key`
3. Choose RSA and `.pem` format, then download the key.

---

## 4. Create AWS Lambda Function for EC2 Deployment
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `EC2PostgreSQLDeployment`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaEC2DeploymentRole`
4. Set timeout to **5 minutes** in Configuration → General Configuration
5. Replace the code in the Lambda function with:

```python
import json
import boto3
import time
from botocore.exceptions import ClientError, WaiterError

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    instance_params = {
        'ImageId': 'ami-0198a868663199764',  # Ubuntu 22.04 LTS AMI (Change as per your region)
        'InstanceType': 't2.micro',
        'MinCount': 1,
        'MaxCount': 1,
        'SecurityGroupIds': ['sg-0bf3cab7329a1c1fe'],  # Replace with your security group ID
        'SubnetId': 'subnet-05c5672f1e80b5086',  # Replace with your subnet ID
        'KeyName': 'postgres-ec2-key',  # Replace with your key pair name
        'IamInstanceProfile': {'Name': 'EC2SSMRole'},  # Role for SSM access
        'UserData': '''#!/bin/bash
            # Update and install PostgreSQL
            apt update -y
            apt install -y postgresql postgresql-contrib

            # Start PostgreSQL service
            systemctl start postgresql
            systemctl enable postgresql

            # Set up PostgreSQL database and user
            sudo -u postgres psql -c "CREATE DATABASE myapp;"
            sudo -u postgres psql -c "CREATE USER myappuser WITH PASSWORD 'MyAppPassword123';"
            sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE myapp TO myappuser;"

            # Allow remote access (Optional)
            echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/14/main/pg_hba.conf
            sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/14/main/postgresql.conf
            systemctl restart postgresql
            ufw allow 5432
        '''.encode('utf-8')
    }

    try:
        response = ec2.run_instances(**instance_params)
        instance_id = response['Instances'][0]['InstanceId']

        # Wait for instance to be running
        try:
            waiter = ec2.get_waiter('instance_running')
            waiter.wait(InstanceIds=[instance_id], WaiterConfig={'Delay': 5, 'MaxAttempts': 10})

            # Get instance details
            instance_info = ec2.describe_instances(InstanceIds=[instance_id])
            public_ip = instance_info['Reservations'][0]['Instances'][0].get('PublicIpAddress', 'Not assigned yet')

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'EC2 instance with PostgreSQL created successfully.',
                    'instance_id': instance_id,
                    'public_ip': public_ip,
                    'postgres_user': 'myappuser',
                    'postgres_database': 'myapp',
                    'status': 'INITIALIZING',
                    'next_steps': [
                        f'SSH into instance: ssh -i YOUR_KEY.pem ubuntu@{public_ip}',
                        'Check PostgreSQL status: systemctl status postgresql',
                        'Login to PostgreSQL: psql -h {public_ip} -U myappuser -d myapp'
                    ]
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

---

## 5. Create Lambda Functions for PostgreSQL Operations

### A. Create `create_user` Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `create_user`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaEC2DeploymentRole`
4. Replace the code with:

```python
import psycopg2
import json

# PostgreSQL Configuration
DB_HOST = "47.129.98.20"  # Replace with your EC2 public IP
DB_USER = "myappuser"
DB_PASSWORD = "MyAppPassword123"
DB_NAME = "myapp"

def lambda_handler(event, context):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )
        cursor = conn.cursor()

        # Create Table
        create_table_sql = """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
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

### B. Create `fetch_user` Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `fetch_user`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaEC2DeploymentRole`
4. Replace the code with:

```python
import psycopg2
import json

# PostgreSQL Configuration
DB_HOST = "47.129.98.20"  # Replace with your EC2 public IP
DB_USER = "myappuser"
DB_PASSWORD = "MyAppPassword123"
DB_NAME = "myapp"

def lambda_handler(event, context):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )
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

---

## 6. Add a Custom Layer for `psycopg2`

### Steps to Create and Attach a Custom Layer
1. **Install `psycopg2` Locally:**
   - Create a directory named `python`:
     ```bash
     mkdir -p python/lib/python3.9/site-packages
     ```
   - Install `psycopg2` into the directory:
     ```bash
     pip install psycopg2-binary -t python/lib/python3.9/site-packages
     ```
   - Zip the `python` folder:
     ```bash
     zip -r psycopg2_layer.zip python
     ```

2. **Upload the Layer to AWS Lambda:**
   - Go to AWS Lambda Console → Layers → Create Layer.
   - Name the layer `psycopg2_layer`.
   - Upload the `psycopg2_layer.zip` file.
   - Choose compatible runtimes (e.g., Python 3.9).
   - Click **Create**.

3. **Attach the Layer to Lambda Functions:**
   - Go to each Lambda function (`create_user` and `fetch_user`).
   - Scroll to the **Layers** section and click **Add a layer**.
   - Select **Custom layers** and choose `psycopg2_layer`.
   - Click **Add**.

---

## 7. Create API Gateway
1. Go to API Gateway Console → Create API → **REST API**
2. Create resources `/deploy`, `/create-user`, and `/fetch-user`.
3. Add methods:
   - **POST** for `/deploy` → Integration type: **Lambda Function** → Select `EC2PostgreSQLDeployment`
   - **POST** for `/create-user` → Integration type: **Lambda Function** → Select `create_user`
   - **GET** for `/fetch-user` → Integration type: **Lambda Function** → Select `fetch_user`
4. Deploy API → Create a new stage `prod`
5. Test the endpoints:
   - Deploy EC2 instance:
     ```bash
     curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/deploy
     ```
   - Create a user:
     ```bash
     curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/create-user
     ```
   - Fetch users:
     ```bash
     curl -X GET https://your-api-id.execute-api.region.amazonaws.com/prod/fetch-user
     ```

---

## 8. Testing & Troubleshooting
### Verify EC2 Instance
1. Go to EC2 Console → Check for running instances
2. Get **Public IP** and connect:
   ```bash
   ssh -i postgres-ec2-key.pem ubuntu@EC2_PUBLIC_IP
   ```
3. Test PostgreSQL:
   ```bash
   psql -h localhost -U myappuser -d myapp
   ```

### Common Errors & Fixes
| Error | Solution |
|--------|------------|
| UnauthorizedOperation: iam:PassRole | Attach a policy allowing `iam:PassRole` to Lambda execution role |
| EC2 instance not launching | Check VPC settings, IAM role, and security groups |
| PostgreSQL not installing | Check EC2 logs: `/var/log/cloud-init-output.log` |
| Connection refused on 5432 | Ensure security group allows inbound PostgreSQL traffic |

---


---


