# Automating EC2 Instance Deployment with MySQL using AWS Lambda & API Gateway

This guide explains how to deploy an EC2 instance with MySQL using AWS Lambda and API Gateway, ensuring proper permissions and security settings.

![architecure](./images/apig.drawio.svg)
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

## 2. Create Security Group
1. Navigate to EC2 Console → Security Groups → Create Security Group
2. Name it `MySQL-EC2-SG`
3. Add inbound rules:
   - **Type:** MySQL/Aurora (Port 3306) → **Source:** Your IP
   - **Type:** SSH (Port 22) → **Source:** Your IP

## 3. Create Key Pair
1. Go to EC2 Console → Key Pairs → Create Key Pair
2. Name it `mysql-ec2-key`
3. Choose RSA and `.pem` format, then download the key.

## 4. Create AWS Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `EC2MySQLDeployment`
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
        'KeyName': 'mysql-ec2-key',  # Replace with your key pair name
        'IamInstanceProfile': {'Name': 'EC2SSMRole'},  # Role for SSM access
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
            
            # Create database and user
            mysql --user=root --password=MySecurePassword123 --execute="CREATE DATABASE myapp;"
            mysql --user=root --password=MySecurePassword123 --execute="CREATE USER 'myappuser'@'localhost' IDENTIFIED BY 'MyAppPassword123';"
            mysql --user=root --password=MySecurePassword123 --execute="GRANT ALL PRIVILEGES ON myapp.* TO 'myappuser'@'localhost';"
            mysql --user=root --password=MySecurePassword123 --execute="FLUSH PRIVILEGES;"
            
            # Allow remote access (Optional)
            sed -i "s/bind-address.*/bind-address = 0.0.0.0/" /etc/mysql/mysql.conf.d/mysqld.cnf
            systemctl restart mysql
            ufw allow 3306
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
                    'message': 'EC2 instance with MySQL created successfully.',
                    'instance_id': instance_id,
                    'public_ip': public_ip,
                    'mysql_user': 'myappuser',
                    'mysql_database': 'myapp',
                    'status': 'INITIALIZING',
                    'next_steps': [
                        f'SSH into instance: ssh -i YOUR_KEY.pem ubuntu@{public_ip}',
                        'Check MySQL status: systemctl status mysql',
                        'Login to MySQL: mysql -u myappuser -pMyAppPassword123'
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

## 5. Create API Gateway
1. Go to API Gateway Console → Create API → **REST API**
2. Create a resource `/deploy`
3. Add a **POST method** → Integration type: **Lambda Function** → Select `EC2MySQLDeployment`
4. Deploy API → Create a new stage `prod`
5. Get the API URL and test with:
   ```bash
   curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/deploy
   ```

## 6. Testing & Troubleshooting
### Verify EC2 Instance
1. Go to EC2 Console → Check for running instances
2. Get **Public IP** and connect:
   ```bash
   ssh -i mysql-ec2-key.pem ubuntu@EC2_PUBLIC_IP
   ```
3. Test MySQL:
   ```bash
   mysql -u myappuser -p  # Password: MyAppPassword123
   ```

### Common Errors & Fixes
| Error | Solution |
|--------|------------|
| UnauthorizedOperation: iam:PassRole | Attach a policy allowing `iam:PassRole` to Lambda execution role |
| EC2 instance not launching | Check VPC settings, IAM role, and security groups |
| MySQL not installing | Check EC2 logs: `/var/log/cloud-init-output.log` |
| Connection refused on 3306 | Ensure security group allows inbound MySQL traffic |

## 7. Security Best Practices
1. **Rotate MySQL passwords** regularly
2. **Restrict Security Groups** to trusted IPs
3. **Enable CloudWatch Logs** for Lambda and EC2
4. **Use Secrets Manager** for storing credentials securely

## 8. Cleanup
To delete resources:
1. Terminate EC2 instance
2. Delete API Gateway
3. Remove Lambda function
4. Delete IAM roles if no longer needed

This updated guide ensures the correct IAM policies are applied and fixes the `iam:PassRole` issue. 🚀

