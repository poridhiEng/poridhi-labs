

# **Automated EC2 Deployment & MongoDB Management with Lambda & API Gateway**

This guide explains how to deploy an EC2 instance with MongoDB using AWS Lambda and API Gateway, ensuring proper permissions and security settings. It also includes Lambda functions for creating and fetching users in the MongoDB database, along with steps to add a custom layer for `pymongo`.

Automating EC2 instance deployment with MongoDB using AWS Lambda and API Gateway simplifies infrastructure management. This serverless approach enables dynamic provisioning, efficient database operations, and secure API access. It’s ideal for applications requiring on-demand database instances, scalable cloud environments, and automated infrastructure setups.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/1.svg)



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

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image.png)


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
5. Name the role `LambdaMongoDBDeploymentRole` and create it.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-2.png)

### B. Create EC2 Role
1. Go to IAM Console → Roles → Create Role
2. Select "AWS Service" and choose "EC2"
3. Attach the following policies:
   - `AmazonSSMManagedInstanceCore`
   - `AmazonEC2FullAccess`
4. Name it `EC2SSMRole` and create the role.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-24.png)


## 3. Create Security Group

1. Go to EC2 Console → Security Groups → Create Security Group.
2. Name it `MongoDB-EC2-SG`.
3. Add inbound rules:
   - **Type:** Custom TCP (Port 27017) → **Source:** Anywhere-IPv4 (0.0.0.0/0)
   - **Type:** SSH (Port 22) → **Source:** Anywhere-IPv4 (0.0.0.0/0)



## 4. Create Key Pair

1. Go to EC2 Console → Key Pairs → Create Key Pair
2. Name it `mongodb-ec2-key`
3. Choose RSA and `.pem` format.
4. Click **Create key pair**.
4. Then download the key.


## 5. Create Lambda Function for EC2 Deployment

1. Go to Lambda Console → Create Function.
2. Name the function `deploy_mongodb`.
3. Choose **Python 3.9** as the runtime.
4. Attach the `LambdaMongoDBDeploymentRole`.
4. Set timeout to **9 minutes** in Configuration → General Configuration

6. Use the following code:

```python
import json
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    instance_params = {
        'ImageId': 'ami-0672fd5b9210aa093',  # Ubuntu 22.04 LTS AMI (change as per your region)
        'InstanceType': 't2.micro',
        'MinCount': 1,
        'MaxCount': 1,
        'SecurityGroupIds': ['sg-0c88be8b68d4a7b94'],  # Replace with your security group ID
        'SubnetId': 'subnet-031e6cf0de9091b0a',  # Replace with your subnet ID
        'KeyName': 'mongodb-ec2-key',  # Replace with your key pair name
        'IamInstanceProfile': {'Name': 'EC2SSMRole2'},  # Role for SSM access
        'UserData': '''#!/bin/bash
            # Update and install MongoDB
            sudo apt update -y
            sudo apt install -y gnupg curl
            curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-archive-keyring.gpg
            echo "deb [signed-by=/usr/share/keyrings/mongodb-archive-keyring.gpg] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
            sudo apt update -y
            sudo apt install -y mongodb-org

            # Start MongoDB service
            sudo systemctl start mongod
            sudo systemctl enable mongod

            # Allow remote access (Optional)
            sudo sed -i "s/bindIp: 127.0.0.1/bindIp: 0.0.0.0/" /etc/mongod.conf
            sudo systemctl restart mongod
            sudo ufw allow 27017
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
                    'message': 'EC2 instance with MongoDB created successfully.',
                    'instance_id': instance_id,
                    'public_ip': public_ip,
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

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

Replace the `ImageId`, `SecurityGroupIds`, `SubnetId` in `instance_params` with valid values.

7. Click **Deploy**.

8. Test the lambda function
    - Go to **Test** tab
    - Create a test event **test** with empty event json:
        ```json
        {}
        ```
    - Click **Save** then click **Test**

    - You will see a EC2 creation was successful and MongoDB was setup successfully.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-3.png)






## 6. Create Lambda Functions for MongoDB Operations

### A. Create `create_post` Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `create_post`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaMongoDBDeploymentRole`

4. Set timeout to **5 minutes** in Configuration → General Configuration   
5. Replace the code with:

```python
import json
from pymongo import MongoClient

# MongoDB Configuration
MONGO_HOST = "your-ec2-public-ip"  # Replace with EC2 public IP
MONGO_PORT = 27017
MONGO_DB = "myapp"
MONGO_COLLECTION = "posts"

def lambda_handler(event, context):
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        # Insert a new post
        post = {
            "title": event.get("title", "Default Title"),
            "content": event.get("content", "Default Content")
        }
        result = collection.insert_one(post)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Post created successfully.',
                'post_id': str(result.inserted_id)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

Replace the `MONGO_HOST` value with your EC2 instance public IP.

6. Click **Deploy**.

### B. Create `fetch_posts` Lambda Function
1. Go to Lambda Console → Create Function
2. Choose "Author from scratch"
3. Enter details:
   - **Function name:** `fetch_posts`
   - **Runtime:** Python 3.9
   - **Architecture:** x86_64
   - **Permissions:** Use existing role → `LambdaMongoDBDeploymentRole`

4. Set timeout to **5 minutes** in Configuration → General Configuration   
5. Replace the code with:

```python
import json
from pymongo import MongoClient

# MongoDB Configuration
MONGO_HOST = "your-ec2-public-ip"  # Replace with EC2 public IP
MONGO_PORT = 27017
MONGO_DB = "myapp"
MONGO_COLLECTION = "posts"

def lambda_handler(event, context):
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        # Fetch all posts
        posts = list(collection.find({}, {'_id': 0}))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Posts fetched successfully.',
                'posts': posts
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

Replace the `MONGO_HOST` value with your EC2 instance public IP.

6. Click **Deploy**.










## 7. Add a Custom Layer for `pymongo`

### Steps to Create and Attach a Custom Layer

1. Intall `zip` in your local machine if not already installed:

    ```bash
    sudo apt update
    sudo apt install zip
    ```

2. Install `pymongo` locally:

   ```bash
   mkdir -p python/lib/python3.9/site-packages
   pip install pymongo -t python/lib/python3.9/site-packages
   zip -r pymongo_layer.zip python
   ```

3. Upload the layer to AWS Lambda:

   - Go to AWS Lambda Console → Layers → Create Layer.
   - Name the layer `pymongo_layer`.
   - Upload the `pymongo_layer.zip` file.
   - Choose compatible runtimes (e.g., Python 3.9).

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-4.png)

   - Click **Create**.


3. **Attach the Layer to Lambda Functions:**
   - Go to each Lambda function (`create_post` and `fetch_posts`).
   - Scroll to the **Layers** section and click **Add a layer**.
   - Select **Custom layers** and choose `pymongo_layer`.
   - Select available version.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-7.png)

   - Click **Add**.

## 8. Test `create_post` and `fetch_posts` lambda functions

1. Test the `create_post` lambda function

    - Go to `create_post` lambda function
    - Go to **Test** tab
    - Create a test event **test** with empty event json:
        ```json
        {}
        ```
    - Click **Save** then click **Test**

    - You will see a post has been created successfully.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-8.png)


2. Test the `fetch_posts` lambda function

    - Go to `fetch_posts` lambda function
    - Go to **Test** tab
    - Create a test event **test** with empty event json:
        ```json
        {}
        ```
    - Click **Save** then click **Test**

    - You will see demo post fetched successfully.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-9.png)



## 9. Create API Gateway

1. Go to API Gateway Console → Create API → **REST API**.

2. Name it `My-REST-API`.
3. Create resources `/deploy`, and `/posts`.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-16.png)

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-10.png)



4. Add methods:

     - **POST** for `/deploy` → Integration type: **Lambda Function** → Select `deploy_mongodb`.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-15.png)

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-17.png)

   - **POST** for `/posts` → Integration type: **Lambda Function** → Select `create_post`.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-11.png)
    
   - **GET** for `/posts` → Integration type: **Lambda Function** → Select `fetch_posts`.

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-12.png)

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-18.png)

5. Deploy API → Create a new stage `prod`.


## 10. Testing API gateway

1. **Get the invoke URL**:

     You can get the invoke url from the **Stages** of your REST API. 

     ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-14.png)



2. **Test MongoDB Deployment**:
    
    Use the `/deploy` endpoint to deploy MongoDB on EC2. Replace `<Invoke URL>` with the invoke url your API

   ```bash
   curl -X POST <Invoke URL>/deploy
   ```

   Expected output:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-19.png)


Before using the following command, change the EC2 IP address in your `create_post` and `fetch_posts` lambda functions and deploy again.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-20.png)

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-21.png)

3. **Test POST Request**:
  
   Use the `/posts` endpoint to create a post. Replace `<Invoke URL>` with the invoke url your API

   ```bash
   curl -X POST <Invoke URL>/posts \
   -H "Content-Type: application/json" \
   -d '{"title": "My First Post", "content": "This is a test post."}'
   ```

   Expected output:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-22.png)

4. **Test GET Request**:

    Use the `/posts` endpoint to fetch all posts. Replace `<Invoke URL>` with the invoke url your API

   ```bash
   curl -X GET <Invoke URL>/posts
   ```

   Expected output:

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2008/images/image-23.png)






## Conclusion  

In this guide, we successfully automated the deployment of an EC2 instance with MongoDB using AWS Lambda and API Gateway. We also implemented Lambda functions for database operations, ensuring secure and efficient user management. This approach streamlines infrastructure provisioning while maintaining flexibility and scalability for cloud-based applications.
 