# Automating Lambda Function Deployment

This project demonstrates the automated deployment of a Lambda function using Pulumi and GitHub Actions. By integrating Pulumi for infrastructure as code and GitHub Actions for continuous deployment, it ensures a smooth, repeatable process for provisioning AWS resources and deploying serverless applications. The automation setup enhances the efficiency and reliability of managing cloud infrastructure, streamlining the deployment process while maintaining high standards of observability.

![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/lambda-overview.png)

## Project Directory

```
project-root/
├── Deploy-Lambda/
│   ├── Dockerfile
│   ├── index.js
│   ├── package.json
│   └── __main__.py
│   └── requirements.txt
└── infrastructure/
     ├── __main__.py
     ├── Dockerfile
     ├── lambda_function.py
     ├── network.py
     ├── security.py
     ├── storage.py
     └── requirements.txt
└── .github/
     └── workflows/
         ├── deploy.yml
         └── infra.yml     
```


## Locally Set Up Pulumi for the `infrastructure` Directory

### Step 1: Install Pulumi

```sh
curl -fsSL https://get.pulumi.com | sh
```

This command installs Pulumi on your local machine.

### Step 2: Log in to Pulumi

```sh
pulumi login
```

This command logs you into your Pulumi account, enabling you to manage your infrastructure as code.

### Step 3: Initialize Pulumi Project

```sh
cd infra
pulumi new aws-python
```

This command initializes a new Pulumi project using the AWS Python template in the `infra` directory.

## Infrastructure Code Breakdown

### `infrastructure/__main__.py`

```python
import pulumi
from network import create_network_infrastructure
from security import create_security_groups
from lambda_function import create_lambda_function
from storage import create_storage_and_outputs

# Create network infrastructure
network = create_network_infrastructure()

# Create security groups
security_groups = create_security_groups(network["vpc"].id)

# Create Lambda function and related resources
lambda_resources = create_lambda_function(
    network["vpc"].id,
    network["private_subnet"].id,
    security_groups["lambda_security_group"].id
)

# Create S3 bucket and prepare for output storage
bucket, upload_exports_to_s3 = create_storage_and_outputs(network["vpc"].id)

# Collect all outputs
all_outputs = {
    "vpc_id": network["vpc"].id,
    "public_subnet_id": network["public_subnet"].id,
    "private_subnet_id": network["private_subnet"].id,
    "public_route_table_id": network["public_route_table"].id,
    "private_route_table_id": network["private_route_table"].id,
    "lambda_security_group_id": security_groups["lambda_security_group"].id,
    "lambda_role_arn": lambda_resources["lambda_role"].arn,
    "repository_url": lambda_resources["ecr_repo"].repository_url,
    "ecr_registry_id": lambda_resources["ecr_repo"].registry_id,
    "lambda_function_name": lambda_resources["lambda_function"].name,
    "lambda_function_arn": lambda_resources["lambda_function"].arn,
    "bucket_name": bucket.id,
}

# Upload outputs to S3
pulumi.Output.all(**all_outputs).apply(lambda resolved: upload_exports_to_s3(resolved))

# Export some values for easy access
pulumi.export('vpc_id', network["vpc"].id)
pulumi.export('lambda_function_name', lambda_resources["lambda_function"].name)
pulumi.export('bucket_name', bucket.id)
```

### Explanation

This script is the main entry point for the Pulumi project. It orchestrates the creation of various resources such as the network infrastructure, security groups, Lambda function, and S3 bucket. It also collects the output values and exports them for easy access.

### `infrastructure/lambda_function.py`

```python
import pulumi
import pulumi_aws as aws
import pulumi_docker as docker
import base64

def create_lambda_function(vpc_id, private_subnet_id, lambda_security_group_id):
    # Create IAM Role for Lambda
    lambda_role = aws.iam.Role("lambda-role",
                               assume_role_policy="""{
                                   "Version": "2012-10-17",
                                   "Statement": [
                                       {
                                           "Action": "sts:AssumeRole",
                                           "Principal": {
                                               "Service": "lambda.amazonaws.com"
                                           },
                                           "Effect": "Allow",
                                           "Sid": ""
                                       }
                                   ]
                               }""")

    # Attach IAM Policy to Lambda Role
    lambda_policy_attachment = aws.iam.RolePolicyAttachment("lambda-policy-attachment",
        role=lambda_role.name,
        policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
    )

    # Create IAM Policy for Lambda Role to access S3
    lambda_policy = aws.iam.Policy("lambda-policy",
        policy="""{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        "arn:aws:s3:::lambda-function-bucket-poridhi",
                        "arn:aws:s3:::lambda-function-bucket-poridhi/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "ec2:CreateNetworkInterface",
                        "ec2:DeleteNetworkInterface",
                        "ec2:DescribeNetworkInterfaces"
                    ],
                    "Resource": "*"
                }
            ]
        }"""
    )

    # Attach IAM Policy to Lambda Role
    lambda_policy_attachment_2 = aws.iam.RolePolicyAttachment("lambda-policy-attachment_2",
        role=lambda_role.name,
        policy_arn=lambda_policy.arn
    )

    # Create ECR Repository
    repo = aws.ecr.Repository('my-app-repo',
        image_tag_mutability="MUTABLE",
        image_scanning_configuration={
            "scanOnPush": True
        }
    )

    # Get repository credentials
    creds = repo.registry_id.apply(
        lambda registry_id: aws.ecr.get_credentials(registry_id=registry_id)
    )

    decoded_creds = creds.authorization_token.apply(
        lambda token: base64.b64decode(token).decode('utf-8').split(':')
    )

    registry_server = creds.proxy_endpoint

    # Define the ECR image name
    ecr_image_name = repo.repository_url.apply(lambda url: f"{url}:latest")

    # Push the Docker image to the ECR repository
    image = docker.Image('my-node-app',
        image_name=ecr_image_name,
        build=docker.DockerBuildArgs(
            context=".",
            dockerfile="Dockerfile",
        ),
        registry={
            "server": registry_server,
            "username": decoded_creds.apply(lambda creds: creds[0]),
            "password": decoded_creds.apply(lambda creds: creds[1]),
        }
    )

    # Create Lambda function
    lambda_function = aws.lambda_.Function("my-lambda-function",
        role=lambda_role.arn,
        image_uri=image.image_name,
        package_type="Image",
        timeout=400,
        memory_size=1024,
        vpc_config={
            "subnet_ids": [private_subnet_id],
            "security_group_ids": [lambda_security_group_id],
        },
        environment={
            "variables": {
                "ENV_VAR_1": "value1",
                "ENV_VAR_2": "value2",
            }
        }
    )

    # Create a CloudWatch Log Group for the Lambda function
    log_group = aws.cloudwatch.LogGroup("lambda-log-group",
        name=lambda_function.name.apply(lambda name: f"/aws/lambda/{name}"),
        retention_in_days=14
    )

    return {
        "lambda_role": lambda_role,
        "lambda_function": lambda_function,
        "ecr_repo": repo
    }
```

### Explanation

This code snippet defines the Lambda function, including the IAM roles and policies required for it to run. It also sets up an ECR repository to store the Docker image for the Lambda function and ensures that the Lambda function can access necessary AWS resources like S3.

### `infrastructure/network.py`

```python
# network.py

import pulumi
import pulumi_aws as aws

def create_network_infrastructure():
    # Create VPC
    vpc = aws.ec2.Vpc("my-vpc",
                      cidr_block="10.0.0.0/16",
                      tags={"Name": "my-vpc"})

    # Create Internet Gateway
    igw = aws.ec2.InternetGateway("my-vpc-igw",
                                  vpc_id=vpc.id,
                                  opts=pulumi.ResourceOptions(depends_on=[vpc]),
                                  tags={"Name": "my-vpc-igw"})

    # Create Route Table for Public Subnet
    public_route_table = aws.ec2.RouteTable("my-vpc-public-rt",
                                            vpc_id=vpc.id,
                                            routes=[{
                                                "cidr_block": "0.0.0.0

/0",
                                                "gateway_id": igw.id,
                                            }],
                                            opts=pulumi.ResourceOptions(depends_on=[igw]),
                                            tags={"Name": "my-vpc-public-rt"})

    # Create Public Subnet
    public_subnet = aws.ec2.Subnet("public-subnet",
                                   vpc_id=vpc.id,
                                   cidr_block="10.0.1.0/24",
                                   availability_zone="us-east-1a",
                                   map_public_ip_on_launch=True,
                                   opts=pulumi.ResourceOptions(depends_on=[vpc]),
                                   tags={"Name": "public-subnet"})

    # Associate Route Table with Public Subnet
    public_route_table_association = aws.ec2.RouteTableAssociation("public-subnet-association",
                                                                   subnet_id=public_subnet.id,
                                                                   route_table_id=public_route_table.id,
                                                                   opts=pulumi.ResourceOptions(depends_on=[public_subnet, public_route_table]))

    # Create Private Subnet
    private_subnet = aws.ec2.Subnet("private-subnet",
                                    vpc_id=vpc.id,
                                    cidr_block="10.0.2.0/24",
                                    availability_zone="us-east-1b",
                                    map_public_ip_on_launch=False,
                                    opts=pulumi.ResourceOptions(depends_on=[vpc]),
                                    tags={"Name": "private-subnet"})

    # Create NAT Gateway
    eip = aws.ec2.Eip("my-eip")
    nat_gateway = aws.ec2.NatGateway("my-nat-gateway",
                                     subnet_id=public_subnet.id,
                                     allocation_id=eip.id,
                                     opts=pulumi.ResourceOptions(depends_on=[public_subnet, eip]),
                                     tags={"Name": "my-nat-gateway"})

    # Create Route Table for Private Subnet
    private_route_table = aws.ec2.RouteTable("my-vpc-private-rt",
                                             vpc_id=vpc.id,
                                             routes=[{
                                                 "cidr_block": "0.0.0.0/0",
                                                 "gateway_id": nat_gateway.id,
                                             }],
                                             opts=pulumi.ResourceOptions(depends_on=[nat_gateway]),
                                             tags={"Name": "my-vpc-private-rt"})

    # Associate Route Table with Private Subnet
    private_route_table_association = aws.ec2.RouteTableAssociation("private-subnet-association",
                                                                    subnet_id=private_subnet.id,
                                                                    route_table_id=private_route_table.id,
                                                                    opts=pulumi.ResourceOptions(depends_on=[private_subnet, private_route_table]))

    return {
        "vpc": vpc,
        "public_subnet": public_subnet,
        "private_subnet": private_subnet,
        "public_route_table": public_route_table,
        "private_route_table": private_route_table
    }
```

### Explanation

This code defines the network infrastructure, including creating a VPC, subnets, route tables, and NAT gateway. It ensures the Lambda function can communicate within the specified network.

### `infrastructure/storage.py`

```python
import pulumi
import pulumi_aws as aws
import json

def create_storage_and_outputs(vpc_id):
    # Create S3 bucket
    bucket = aws.s3.Bucket("lambda-function-bucket-poridhi",
        bucket="lambda-function-bucket-poridhi-1213",
        acl="private",
        tags={"Name": "Lambda Function Bucket"}
    )

    def upload_exports_to_s3(outputs):
        # Convert outputs to JSON
        outputs_json = json.dumps(outputs, indent=2)
        
        # Create an S3 object with the JSON content
        aws.s3.BucketObject("pulumi-exports",
            bucket=bucket.id,
            key="pulumi-exports.json",
            content=outputs_json,
            content_type="application/json"
        )

    return bucket, upload_exports_to_s3
```

### Explanation

This code snippet creates an S3 bucket and defines a function to upload Pulumi outputs to the bucket. This allows other parts of the infrastructure to access these outputs.

### `infrastructure/Dockerfile`

```dockerfile
FROM nginx:latest
```

### Explanation

This is a simple Dockerfile that uses the latest Nginx image. This is used to demonstrate the deployment of a Dockerized Lambda function.

### `infrastructure/requirements.txt`

```
pulumi>=3.0.0,<4.0.0
pulumi-aws>=6.0.2,<7.0.0
pulumi_docker>=3.0.0,<4.0.0
```

### Explanation

This file lists the required Pulumi packages for the infrastructure code.

## Setup Infrastructure for Build Image and Update Lambda Function

### `Deploy-Lambda/__main__.py`

```python
import pulumi
import pulumi_aws as aws
import json
import base64
import pulumi_docker as docker
import subprocess
import time

class LambdaUpdater(pulumi.dynamic.ResourceProvider):
    def create(self, props):
        cmd = f"aws lambda update-function-code --function-name {props['function_name']} --image-uri {props['image_uri']} --region {props['region']}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        # Generate a unique ID for this update
        new_id = f"{props['function_name']}_{props['timestamp']}"
        
        return pulumi.dynamic.CreateResult(id_=new_id, outs=props)

    def update(self, id, props, olds):
        cmd = f"aws lambda update-function-code --function-name {props['function_name']} --image-uri {props['image_uri']} --region {props['region']}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        
        # Use the existing ID
        props['id'] = id
        
        return pulumi.dynamic.UpdateResult(outs=props)

class LambdaUpdate(pulumi.dynamic.Resource):
    def __init__(self, name, props, opts = None):
        super().__init__(LambdaUpdater(), name, props, opts)
        self.function_name = props['function_name']
        self.image_uri = props['image_uri']
        self.region = props['region']
        self.timestamp = props['timestamp']

def get_exports_from_s3(bucket_name, object_key):
    # Use the get_object function to retrieve the S3 object
    s3_object = aws.s3.get_object(bucket=bucket_name, key=object_key)
    
    # Check if s3_object.body is a string or an Output
    if isinstance(s3_object.body, str):
        # If it's a string, parse it and wrap it in a Pulumi Output
        return pulumi.Output.from_input(json.loads(s3_object.body))
    else:
        # If it's an Output, apply json.loads to it
        return s3_object.body.apply(lambda body: json.loads(body))

# Usage
exports = get_exports_from_s3('lambda-function-bucket-poridhi-1213', 'pulumi-exports.json')

# Get ECR repository details from exports
repository_url = exports.apply(lambda exp: exp['repository_url'])
ecr_registry_id = exports.apply(lambda exp: exp['ecr_registry_id'])

# Get repository credentials
creds = aws.ecr.get_credentials_output(registry_id=ecr_registry_id)

decoded_creds = creds.authorization_token.apply(
    lambda token: base64.b64decode(token).decode('utf-8').split(':')
)

registry_server = creds.proxy_endpoint

# Define the ECR image name
ecr_image_name = repository_url.apply(lambda url: f"{url}:latest")

# Push the Docker image to the ECR repository
image = docker.Image('my-node-app',
    image_name=ecr_image_name,
    build=docker.DockerBuildArgs(
        context=".",
        dockerfile="Dockerfile",
    ),
    registry={
        "server": registry_server,
        "username": decoded_creds.apply(lambda creds: creds[0]),
        "password": decoded_creds.apply(lambda creds: creds[1]),
    }
)

lambda_function_name = exports.apply(lambda exp: exp['lambda_function_name'])
lambda_role_arn = exports.apply(lambda exp: exp['lambda_role_arn'])
lambda_function_arn = exports.apply(lambda exp: exp['lambda_function_arn'])

# Update the Lambda function using AWS CLI
update_lambda = LambdaUpdate('update-lambda-function',
    {
        'function_name': lambda_function_name,
        'image_uri': image.image_name,
        'region': aws.config.region,
        'timestamp': str(time.time())  # Ensure a unique ID for the update
    },
    opts=pulumi.ResourceOptions(depends_on=[image])
)

api = aws.apigateway.RestApi("myApi",
    description="API Gateway for Lambda function",
)
default_resource = aws.apigateway.Resource("defaultResource",
    parent_id=api.root_resource_id,
    path_part="default",
    rest_api=api.id,
)

# Create a resource
lambda_resource = aws.apigateway.Resource("lambdaResource",
    parent_id=default_resource.id,
    path_part="my-lambda-function",
    rest_api=api.id,
)
test1_resource = aws.apigateway.Resource("test1Resource",
    parent_id=lambda_resource.id,
    path_part="test1",
    rest_api=api.id,
)
test2_resource = aws.apigateway.Resource("test2Resource",
    parent_id=lambda_resource.id,
    path_part="test2",
    rest_api=api.id,
)
test1_method = aws.apigateway.Method("test1_Method",
    http_method="GET",
    authorization="NONE",
    resource_id=test1_resource.id,
    rest_api=api.id,
)

test2_method = aws.ap

igateway.Method("test2_Method",
    http_method="GET",
    authorization="NONE",
    resource_id=test2_resource.id,
    rest_api=api.id,
)

# Create a method for the GET request
method = aws.apigateway.Method("myMethod",
    http_method="GET",
    authorization="NONE",
    resource_id=lambda_resource.id,
    rest_api=api.id,
)

integration = aws.apigateway.Integration("myIntegration",
    http_method=method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_function_arn.apply(lambda arn: f"arn:aws:apigateway:{aws.config.region}:lambda:path/2015-03-31/functions/{arn}/invocations"),
    resource_id=lambda_resource.id,
    rest_api=api.id,
)
test1_integration = aws.apigateway.Integration("test1Integration",
    http_method=test1_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_function_arn.apply(lambda arn: f"arn:aws:apigateway:{aws.config.region}:lambda:path/2015-03-31/functions/{arn}/invocations"),
    resource_id=test1_resource.id,
    rest_api=api.id,
)
test2_integration = aws.apigateway.Integration("test2Integration",
    http_method=test2_method.http_method,
    integration_http_method="POST",
    type="AWS_PROXY",
    uri=lambda_function_arn.apply(lambda arn: f"arn:aws:apigateway:{aws.config.region}:lambda:path/2015-03-31/functions/{arn}/invocations"),
    resource_id=test2_resource.id,
    rest_api=api.id,
)

# Grant API Gateway permission to invoke the Lambda function
permission = aws.lambda_.Permission("lambda_Permission",
    action="lambda:InvokeFunction",
    function=lambda_function_arn,
    principal="apigateway.amazonaws.com",
    source_arn=api.execution_arn.apply(lambda arn: f"{arn}/*/*"),
)

# Deploy the API
deployment = aws.apigateway.Deployment("myDeployment",
    rest_api=api.id,
    # Ensure deployment triggers on changes to the integration
    triggers={
        "integration": integration.id,
        "test1_integration": test1_integration.id,
        "test2_integration": test2_integration.id,
    },
    opts=pulumi.ResourceOptions(depends_on=[integration]),
)

# Create a stage
stage = aws.apigateway.Stage("myStage",
    deployment=deployment.id,
    rest_api=api.id,
    stage_name="prod",
)
pulumi.export('image_url', image.image_name)
```

### Explanation

This script handles the process of updating the Lambda function with a new Docker image and setting up an API Gateway for the Lambda function. It uses a custom dynamic Pulumi resource to execute the AWS CLI commands needed to update the Lambda function's code.

### `Deploy-Lambda/requirements.txt`

```
pulumi>=3.0.0,<4.0.0
pulumi-aws>=6.0.2,<7.0.0
pulumi_docker>=3.0.0,<4.0.0
```

### Explanation

This file lists the required Pulumi packages for the deployment code.

## Locally Set Up Node.js App in `Deploy-Lambda` Directory

1. **Initialize Node.js Project**:

   ```sh
   cd deploy-in-lambda
   npm init -y
   ```

2. **Create `Deploy-Lambda/index.js`**:

   ```javascript
   exports.handler = async (event) => {
    try {
      let response;
      switch (event.httpMethod) {
        case 'GET':
          if (event.path === '/default/my-lambda-function') {
            response = {
              statusCode: 200,
              body: JSON.stringify('Hello from Lambda Function!'),
            };
          } else if (event.path === '/default/my-lambda-function/test1') {
            response = {
              statusCode: 200,
              body: JSON.stringify('This is test1 route!!'),
            };
          } else if (event.path === '/default/my-lambda-function/test2') {
            response = {
              statusCode: 200,
              body: JSON.stringify('This is test2 route!'),
            };
          } else {
            response = {
              statusCode: 404,
              body: JSON.stringify('Not Found'),
            };
          }
          break;
        default:
          response = {
            statusCode: 405,
            body: JSON.stringify('Method Not Allowed'),
          };
      }
  
      return response;
    } catch (error) {
      console.error('Handler error:', error);
      return {
        statusCode: 500,
        body: JSON.stringify('Internal Server Error'),
      };
    }
  };
   ```

3. **Create `Deploy-Lambda/package.json`**:

   ```json
   {
      "name": "lambda-function",
      "version": "1.0.0",
      "description": "A simple AWS Lambda function",
      "main": "index.js",
      "scripts": {
        "start": "node index.js"
      },
      "author": "Fazlul Karim",
      "license": "ISC"
   }
   ```

4. **Create `Deploy-Lambda/Dockerfile`**:

   ```dockerfile
   # Stage 1: Build Stage
   FROM node:20 as build-stage

   # Set the working directory
   WORKDIR /app

   # Copy package.json and package-lock.json
   COPY package.json package-lock.json ./

   # Install dependencies
   RUN npm install --production

   # Copy source files
   COPY index.js ./

   # Stage 2: Final Stage
   FROM public.ecr.aws/lambda/nodejs:20

   # Copy necessary files from the build stage
   COPY --from=build-stage /app /var/task/

   # Set the CMD to your handler
   CMD [ "index.handler" ]
   ```

### Explanation

This Node.js application serves as the Lambda function's code. The Dockerfile builds the application and prepares it to run in an AWS Lambda environment using the provided public ECR image.

## Create a Token for Login to Pulumi

1. **Create Pulumi Access Token**:
    - Go to the Pulumi Console at [https://app.pulumi.com](https://app.pulumi.com).
    - Navigate to `Settings` > `Access Tokens`.
    - Click `Create Token`, give it a name, and copy the token.

    ![](https://github.com/Galadon123/Lambda-Function-with-Pulumi-python/blob/main/image/l-2.png)

## Create a GitHub Repo and Set Up Secrets

1. **Create a GitHub Repository**:
    - Navigate to GitHub and create a new repository.

2. **Add GitHub Secrets**:
    - Go to `Settings` > `Secrets and variables` > `Actions`.
    - Add the following secrets:
        - `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
        - `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
        - `PULUMI_ACCESS_TOKEN`: Your Pulumi access token.

    ![](https://github.com/Galadon123/Lambda-Function-with-Pulumi-python/blob/main/image/l-3.png)

## Create Two Workflows

### `.github/workflows/infra.yml`

```yaml
name: Pulumi Deploy
on:
  push:
    branches:
      - main
    paths:
      - 'infrastructure/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m venv infrastructure/venv
          source infrastructure/venv/bin/activate
          pip install --upgrade pip setuptools wheel
          pip install pulumi pulumi-aws pulumi-docker

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: |
          source infrastructure/venv/bin/activate
          pulumi login

      - name: Pulumi stack select
        run: |
          source infrastructure/venv/bin/activate
          pulumi stack select Galadon123/Lambda-Infrastructure --cwd infrastructure

      - name: Pulumi refresh
        run: |
          source infrastructure/venv/bin/activate
          pulumi refresh --yes --cwd infrastructure

      - name: Pulumi up
        run: |
          source infrastructure/venv/bin/activate
          pulumi up --yes --cwd infrastructure
```

### Explanation

This GitHub Actions workflow sets up the Pulumi environment, installs dependencies, configures AWS credentials, logs in to Pulumi, and deploys the infrastructure code whenever there are changes in the `infrastructure` directory.

### `.github/workflows/deploy.yml`

```yaml
name: Pulumi Deploy Lambda

on:
  push:
    branches:
      - main
    paths:
      - 'Deploy-Lambda/**'
  workflow_dispatch:
  workflow_run:
    workflows: ["Pulumi Deploy"]
    types:
      - completed

jobs:
  deploy

:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Create virtual environment
        run: |
          python -m venv Deploy-Lambda/venv
          source Deploy-Lambda/venv/bin/activate
          pip install --upgrade pip setuptools wheel
          pip install pulumi pulumi-aws pulumi-docker

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: |
          source Deploy-Lambda/venv/bin/activate
          pulumi login

      - name: Pulumi stack select
        run: |
          source Deploy-Lambda/venv/bin/activate
          pulumi stack select Galadon123/lambda-function-deploy --cwd Deploy-Lambda

      - name: Pulumi refresh
        run: |
          source Deploy-Lambda/venv/bin/activate
          pulumi refresh --yes --cwd Deploy-Lambda

      - name: Pulumi up
        run: |
          source Deploy-Lambda/venv/bin/activate
          pulumi up --yes --cwd Deploy-Lambda
```

### Explanation

This GitHub Actions workflow is triggered by changes in the `Deploy-Lambda` directory. It sets up the environment, installs dependencies, configures AWS credentials, logs in to Pulumi, and deploys the Lambda function and related resources.

## Git Push the Project

1. **Initialize Git Repository**:

    ```sh
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    ```

2. **Add Remote and Push**:

    ```sh
    git remote add origin https://github.com/yourusername/your-repo.git
    git push -u origin main
    ```

## Observe the Workflow Actions Section for Errors

- Navigate to the `Actions` tab in your GitHub repository.
- Observe the workflows and ensure they run without errors.
- If errors occur, click on the failed job to view the logs and debug accordingly.

## Testing Lambda Function with JSON Query

1. **Select Your Lambda Function**:
   - In the Lambda console, find and select your deployed Lambda function.

2. **Create a Test Event**:
   - Click on the "Test" button in the top-right corner.
   - If this is your first time, you will be prompted to configure a test event.

3. **Configure the Test Event and Test**:
   - Enter a name for the test event.
   - Replace the default JSON with your desired test JSON query, for example:
     ```json
     {
      "httpMethod": "GET",
      "path": "/default/my-lambda-function"
     }
     ```

     Outputs:

     ![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/o-1.png)

     ```json
     {
      "httpMethod": "GET",
      "path": "/default/my-lambda-function/test1"
     }
     ```
     Outputs:

     ![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/o-2.png)

     ```json
     {
      "httpMethod": "GET",
      "path": "/default/my-lambda-function/test2"
     }
     ```

     Outputs:

     ![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/o-3.png)

### Test Each API-Gateway Endpoint
Make sure to test each of the API-Gateway endpoints:
1. `/default/my-lambda-function`
2. `/default/my-lambda-function/test1`
3. `/default/my-lambda-function/test2`

Each endpoint should return the respective message as defined in your Lambda function handler.

![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/w-3.png)
![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/w-1.png)
![](https://github.com/Galadon123/Automating-Lambda-Function-Deployment-with-Pulumi/blob/main/images/w-2.png)

## Summary

By following this guide, you have set up a fully automated process for deploying an AWS Lambda function using Pulumi and GitHub Actions. This setup ensures that your cloud infrastructure and serverless applications are deployed consistently and reliably, with high standards of observability and efficiency. The integration of Pulumi and GitHub Actions provides a robust CI/CD pipeline, streamlining the management of your AWS resources.