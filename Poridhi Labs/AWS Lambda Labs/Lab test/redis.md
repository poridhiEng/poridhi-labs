

## **Automating Redis Deployment and Operations with AWS Lambda & API Gateway**

This guide explains how to deploy a Redis instance using AWS Lambda and API Gateway. It includes steps to set up an **ElastiCache Redis cluster**, create Lambda functions to interact with Redis, and expose these functions via API Gateway.

---

## **1. Set Up Required IAM Roles**

### A. Create Lambda Execution Role
1. Go to IAM Console → Roles → Create Role
2. Select "AWS Service" and choose "Lambda"
3. Attach the following policies:
   - `AWSLambdaBasicExecutionRole`
   - `AmazonEC2FullAccess` (if using EC2 for Redis)
   - `AmazonElastiCacheFullAccess` (if using ElastiCache)
4. Name the role `LambdaRedisDeploymentRole` and create it.

---



---

## **3. Create Lambda Functions**

### A. Lambda Function to Deploy Redis 
If you’re deploying Redis on an EC2 instance, use this Lambda function to automate the setup:

```python
import json
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    instance_params = {
        'ImageId': 'ami-0672fd5b9210aa093',  # Amazon Linux 2 AMI (change as per your region)
        'InstanceType': 't2.micro',
        'MinCount': 1,
        'MaxCount': 1,
        'SecurityGroupIds': ['sg-09868cdfcad53cd69'],  # Replace with your security group ID
        'SubnetId': 'subnet-0149d396b60ecec3f',  # Replace with your subnet ID
        'KeyName': 'redis-ec2-key',  # Replace with your key pair name
        'IamInstanceProfile': {'Name': 'RedisSSMRole'}, 
        'UserData': '''#!/bin/bash
            # Update packages
            apt update -y
            apt install -y redis-server

            # Configure Redis
            sed -i "s/^bind 127.0.0.1 ::1/bind 0.0.0.0/" /etc/redis/redis.conf
            sed -i "s/^protected-mode yes/protected-mode no/" /etc/redis/redis.conf
            sed -i "s/^supervised no/supervised systemd/" /etc/redis/redis.conf

            # Restart Redis to apply changes
            systemctl restart redis-server
            systemctl enable redis-server
            sudo ufw allow 6379/tcp
        '''.encode('utf-8')
    }

    try:
        response = ec2.run_instances(**instance_params)
        instance_id = response['Instances'][0]['InstanceId']

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'EC2 instance with Redis created successfully.',
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

### B. Lambda Function to Interact with Redis

Install the `redis` Python library and create a Lambda layer:

1. **Install `redis` Locally:**
   ```bash
   mkdir -p python/lib/python3.9/site-packages
   pip install redis -t python/lib/python3.9/site-packages
   zip -r redis_layer.zip python
   ```

2. **Upload the Layer to AWS Lambda:**
   - Go to AWS Lambda Console → Layers → Create Layer.
   - Name the layer `redis_layer`.
   - Upload the `redis_layer.zip` file.
   - Choose compatible runtimes (e.g., Python 3.9).
   - Click **Create**.

3. **Create the Lambda Function:**
   - Go to Lambda Console → Create Function.
   - Name it `redis_operations`.
   - Attach the `redis_layer` and `LambdaRedisDeploymentRole`.
   - Use the following code:

```python
import json
import redis

# Redis Configuration
REDIS_HOST = "your-redis-endpoint"  # Replace with ElastiCache endpoint or EC2 public IP
REDIS_PORT = 6379

def lambda_handler(event, context):
    try:
        # Connect to Redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

        # Example: Set a key-value pair
        r.set('foo', 'bar')

        # Example: Get a value
        value = r.get('foo')

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Redis operation successful.',
                'value': value
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
2. Create resources `/deploy` (for Redis deployment) and `/redis` (for Redis operations).
3. Add methods:
   - **POST** for `/deploy` → Integration type: **Lambda Function** → Select the Redis deployment Lambda.
   - **POST** for `/redis` → Integration type: **Lambda Function** → Select the `redis_operations` Lambda.
4. Deploy API → Create a new stage `prod`.

---

## **5. Testing & Troubleshooting**

### Test Redis Deployment
1. Use the `/deploy` endpoint to deploy Redis on EC2:
   ```bash
   curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/deploy
   ```

### Test Redis Operations
1. Use the `/redis` endpoint to interact with Redis:
   ```bash
   curl -X POST https://your-api-id.execute-api.region.amazonaws.com/prod/redis
   ```

### Common Errors & Fixes
| Error | Solution |
|--------|------------|
| Connection refused | Ensure the Redis instance is running and the security group allows inbound traffic on port 6379. |
| Timeout | Increase the Lambda function timeout to 5 minutes. |
| UnauthorizedOperation | Ensure the Lambda execution role has the necessary permissions. |

---

---
