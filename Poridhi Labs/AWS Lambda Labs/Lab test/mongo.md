

## **Automating MongoDB Deployment and Operations with AWS Lambda & API Gateway**

This guide explains how to:
1. Deploy MongoDB on an EC2 Ubuntu instance using AWS Lambda.
2. Create Lambda functions to interact with MongoDB (POST and GET requests).
3. Expose these functions via API Gateway.

---

## **1. Set Up Required IAM Roles**

### A. Create Lambda Execution Role
1. Go to IAM Console → Roles → Create Role
2. Select "AWS Service" and choose "Lambda"
3. Attach the following policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEC2FullAccess`
4. Name the role `LambdaMongoDBDeploymentRole` and create it.

---

## **2. Deploy MongoDB on EC2**

### Step 1: Create Lambda Function to Deploy MongoDB on EC2

1. Go to Lambda Console → Create Function.
2. Name the function `deploy_mongodb`.
3. Choose **Python 3.9** as the runtime.
4. Attach the `LambdaMongoDBDeploymentRole`.
5. Use the following code:

```python
import json
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    instance_params = {
        'ImageId': 'ami-0c02fb55956c7d316',  # Ubuntu 22.04 LTS AMI (change as per your region)
        'InstanceType': 't2.micro',
        'MinCount': 1,
        'MaxCount': 1,
        'SecurityGroupIds': ['sg-0bf3cab7329a1c1fe'],  # Replace with your security group ID
        'SubnetId': 'subnet-05c5672f1e80b5086',  # Replace with your subnet ID
        'KeyName': 'mongodb-ec2-key',  # Replace with your key pair name
        'IamInstanceProfile': {'Name': 'EC2SSMRole'},  # Role for SSM access
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

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'EC2 instance with MongoDB created successfully.',
                'instance_id': instance_id
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
```

---

### Step 2: Create Security Group for MongoDB
1. Go to EC2 Console → Security Groups → Create Security Group.
2. Name it `MongoDB-EC2-SG`.
3. Add inbound rules:
   - **Type:** Custom TCP (Port 27017) → **Source:** Your IP or `0.0.0.0/0` (for testing).
   - **Type:** SSH (Port 22) → **Source:** Your IP.

---

### Step 3: Create Key Pair
1. Go to EC2 Console → Key Pairs → Create Key Pair.
2. Name it `mongodb-ec2-key`.
3. Choose RSA and `.pem` format, then download the key.

---

## **3. Create Lambda Functions for MongoDB Operations**

### Step 1: Install `pymongo` and Create a Lambda Layer
1. Install `pymongo` locally:
   ```bash
   mkdir -p python/lib/python3.9/site-packages
   pip install pymongo -t python/lib/python3.9/site-packages
   zip -r pymongo_layer.zip python
   ```
2. Upload the layer to AWS Lambda:
   - Go to AWS Lambda Console → Layers → Create Layer.
   - Name the layer `pymongo_layer`.
   - Upload the `pymongo_layer.zip` file.
   - Choose compatible runtimes (e.g., Python 3.9).
   - Click **Create**.

---

### Step 2: Create `create_post` Lambda Function
1. Go to Lambda Console → Create Function.
2. Name the function `create_post`.
3. Attach the `pymongo_layer` and `LambdaMongoDBDeploymentRole`.
4. Use the following code:

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

---

### Step 3: Create `fetch_posts` Lambda Function
1. Go to Lambda Console → Create Function.
2. Name the function `fetch_posts`.
3. Attach the `pymongo_layer` and `LambdaMongoDBDeploymentRole`.
4. Use the following code:

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

---

## **4. Create API Gateway**

1. Go to API Gateway Console → Create API → **REST API**.
2. Create resources `/posts` and `/posts/{id}`.
3. Add methods:
   - **POST** for `/posts` → Integration type: **Lambda Function** → Select `create_post`.
   - **GET** for `/posts` → Integration type: **Lambda Function** → Select `fetch_posts`.
4. Deploy API → Create a new stage `prod`.

---

## **5. Testing & Troubleshooting**

### Test MongoDB Deployment
1. Use the `/deploy` endpoint to deploy MongoDB on EC2:
   ```bash
   curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/deploy
   ```

### Test POST Request
1. Use the `/posts` endpoint to create a post:
   ```bash
   curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/posts \
   -H "Content-Type: application/json" \
   -d '{"title": "My First Post", "content": "This is a test post."}'
   ```

### Test GET Request
1. Use the `/posts` endpoint to fetch all posts:
   ```bash
   curl -X GET https://your-api-id.execute-api.region.amazonaws.com/prod/posts
   ```

---



