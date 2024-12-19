# Automating Lambda Function Tracing

This project demonstrates the automated deployment of a Lambda function using Pulumi and GitHub Actions, combined with an observability stack. By integrating Pulumi for infrastructure as code and GitHub Actions for continuous deployment, it ensures a smooth, repeatable process for provisioning AWS resources and deploying serverless applications. The automation setup enhances the efficiency and reliability of managing cloud infrastructure, streamlining the deployment process while maintaining high standards of observability and traceability.

![](https://github.com/Galadon123/-Lambda-Function-Deployment/blob/main/image/f.png)
### Grafana and Tracing
The observability stack, featuring Grafana, Tempo, and the OpenTelemetry Collector, is deployed on an EC2 instance. Grafana provides powerful visualization capabilities, allowing you to monitor various metrics and performance indicators. Tempo, integrated with Grafana, enables distributed tracing, helping you track the flow of requests through your system and identify performance bottlenecks. The OpenTelemetry Collector collects and exports trace data, ensuring comprehensive monitoring and insights into application behavior and performance.

![](https://github.com/Galadon123/-Lambda-Function-Deployment/blob/main/image/Screenshot%202024-07-02%20174136.png)
## Project Directory

```
project-root/
├── infra/
│   ├── __init__.py
│   ├── __main__.py
│   ├── vpc.py
│   ├── subnet.py
│   ├── ecr_repository.py
│   ├── lambda_role.py
│   ├── s3_bucket.py
│   └── security_group.py
├── deploy-in-lambda/
│   ├── index.js
│   ├── package.json
│   └── Dockerfile
├── .github/
│   └── workflows/
│       ├── infra.yml
│       └── deploy.yml       
```

### Locally Set Up Pulumi for the `infra` Directory

#### Step 1: Install Pulumi

```sh
curl -fsSL https://get.pulumi.com | sh
```

This command installs Pulumi on your local machine.

#### Step 2: Log in to Pulumi

```sh
pulumi login
```

This command logs you into your Pulumi account, enabling you to manage your infrastructure as code.

#### Step 3: Initialize Pulumi Project

```sh
cd infra
pulumi new aws-python
```

This command initializes a new Pulumi project using the AWS Python template in the `infra` directory.

#### Step 4: Configure AWS Credentials

Ensure that your AWS credentials are set up in your environment:

```sh
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

This step ensures that Pulumi can authenticate with AWS to create and manage resources.

#### Step 5: Install Python Dependencies

```sh
python -m venv venv
source venv/bin/activate
pip install pulumi pulumi-aws
```

These commands create a virtual environment, activate it, and install the necessary Pulumi packages.

### Infrastructure Code Breakdown

 `infra/__main__.py`

This is the main entry point for Pulumi to execute. It imports and initializes the infrastructure components.

```python
import pulumi
import pulumi_aws as aws
import json
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
                                            "cidr_block": "0.0.0.0/0",
                                            "gateway_id": igw.id,
                                        }],
                                        opts=pulumi.ResourceOptions(depends_on=[igw]),
                                        tags={"Name": "my-vpc-public-rt"})

# Create Public Subnet within VPC c
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
                                                               opts=pulumi.ResourceOptions(depends_on=[public_route_table]))

# Create Security Group for EC2 Instance
ec2_security_group = aws.ec2.SecurityGroup("ec2-security-group",
                                           vpc_id=vpc.id,
                                           description="Allow SSH and HTTP traffic",
                                           ingress=[
                                               {
                                                   "protocol": "tcp",
                                                   "from_port": 22,
                                                   "to_port": 22,
                                                   "cidr_blocks": ["0.0.0.0/0"],
                                               },
                                               {
                                                   "protocol": "tcp",
                                                   "from_port": 80,
                                                   "to_port": 80,
                                                   "cidr_blocks": ["0.0.0.0/0"],
                                               },
                                           ],
                                           egress=[
                                               {
                                                   "protocol": "-1",
                                                   "from_port": 0,
                                                   "to_port": 0,
                                                   "cidr_blocks": ["0.0.0.0/0"],
                                               },
                                           ],
                                           opts=pulumi.ResourceOptions(depends_on=[vpc]),
                                           tags={"Name": "ec2-security-group"})

ec2_instance = aws.ec2.Instance("my-ec2-instance",
                                instance_type="t2.micro",
                                vpc_security_group_ids=[ec2_security_group.id],
                                subnet_id=public_subnet.id,
                                ami="ami-04a81a99f5ec58529",  # Example AMI ID, replace with your desired AMIs
                                tags={"Name": "my-ec2-instance"},
                                opts=pulumi.ResourceOptions(depends_on=[public_subnet, ec2_security_group]))
# Create Private Subnet within VPC
private_subnet = aws.ec2.Subnet("private-subnet",
                                vpc_id=vpc.id,
                                cidr_block="10.0.2.0/24",
                                availability_zone="us-east-1b",
                                map_public_ip_on_launch=False,
                                opts=pulumi.ResourceOptions(depends_on=[vpc]),
                                tags={"Name": "private-subnet"})

# Create Route Table for Private Subnet
private_route_table = aws.ec2.RouteTable("my-vpc-private-rt",
                                         vpc_id=vpc.id,
                                         routes=[{
                                             "cidr_block": "10.0.0.0/16",
                                             "gateway_id": "local",
                                         }],
                                         opts=pulumi.ResourceOptions(depends_on=[igw]),
                                         tags={"Name": "my-vpc-private-rt"})

# Associate Route Table with Private Subnet
private_route_table_association = aws.ec2.RouteTableAssociation("private-subnet-association",
                                                                subnet_id=private_subnet.id,
                                                                route_table_id=private_route_table.id,
                                                                opts=pulumi.ResourceOptions(depends_on=[private_route_table]))

# Create Security Group for Lambda functions
lambda_security_group = aws.ec2.SecurityGroup("lambda-security-group",
                                              vpc_id=vpc.id,
                                              description="Allow all traffic",
                                              ingress=[{
                                                  "protocol": "-1",  # All protocols
                                                  "from_port": 0,
                                                  "to_port": 0,
                                                  "cidr_blocks": ["0.0.0.0/0"],
                                              }],
                                              egress=[{
                                                  "protocol": "-1",  # All protocols
                                                  "from_port": 0,
                                                  "to_port": 0,
                                                  "cidr_blocks": ["0.0.0.0/0"],
                                              }],
                                              opts=pulumi.ResourceOptions(depends_on=[vpc]),
                                              tags={"Name": "lambda-security-group"})

# Create IAM Role for Lambda with trust policy
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

# Create Inline Policy allowing GetObject on pulumi-outputs.json in the S3 bucket
bucket_name = "lambda-function-bucket-poridhi"
bucket = aws.s3.Bucket(bucket_name)

# Get the ARN of the bucket
bucket_arn = bucket.arn

lambda_s3_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowLambdaReadS3",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_arn}/pulumi-outputs.json"
            ]
        }
    ]
}

lambda_s3_policy = aws.iam.Policy("lambdaS3Policy", policy=json.dumps(lambda_s3_policy_document))

# Attach the policy to tb he IAM Role
lambda_role_policy_attachment = aws.iam.RolePolicyAttachment("lambdaRolePolicyAttachment",
                                                             role=lambda_role.name,
                                                             policy_arn=lambda_s3_policy.arn)

# Create ECR Repository f
repository = aws.ecr.Repository("my-ecr-repo",
                                 opts=pulumi.ResourceOptions(depends_on=[lambda_role]))

# Export Outputs
pulumi.export("vpc_id", vpc.id)
pulumi.export("public_subnet_id", public_subnet.id)
pulumi.export("private_subnet_id", private_subnet.id)
pulumi.export("public_route_table_id", public_route_table.id)
pulumi.export("private_route_table_id", private_route_table.id)
pulumi.export("ec2_security_group_id", ec2_security_group.id)
pulumi.export("lambda_security_group_id", lambda_security_group.id)
pulumi.export("lambda_role_arn", lambda_role.arn)
pulumi.export("bucket_name", bucket.bucket)
pulumi.export("ecr_repo_url", repository.repository_url)
pulumi.export("ecr_registry", repository.registry_id)
pulumi.export("ec2_private_ip", ec2_instance.private_ip)
```

## Locally Set Up Node.js App

1. **Initialize Node.js Project**:
    ```sh
    cd deploy-in-lambda
    npm init -y
    ```

2. **Create `index.js`**:
```javascript
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-otlp-grpc');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { trace, context } = require('@opentelemetry/api');
const grpc = require('@grpc/grpc-js');
const AWS = require('aws-sdk');
const express = require('express');
const awsServerlessExpress = require('aws-serverless-express');
const awsServerlessExpressMiddleware = require('aws-serverless-express/middleware');

const app = express();
const server = awsServerlessExpress.createServer(app);

app.use(express.json());
app.use(awsServerlessExpressMiddleware.eventContext());

let otelInitialized = false;

async function initializeOpenTelemetry() {
  if (!otelInitialized) {
    console.log("Initializing OpenTelemetry...");
    try {
      const traceExporter = new OTLPTraceExporter({
        url: 'http://10.0.1.183:4317',  // Replace with your otel-instance Private IP
        credentials: grpc.credentials.createInsecure(),
      });

      const sdk = new NodeSDK({
        traceExporter,
        instrumentations: [getNodeAutoInstrumentations()],
      });

      await sdk.start();
      otelInitialized = true;
      console.log('OpenTelemetry SDK initialized');
    } catch (error) {
      console.error("Error initializing OpenTelemetry:", error);
    }
  }
}

// Initialize OpenTelemetry outside the handler to ensure it runs on cold start
initializeOpenTelemetry();

app.get('/', (req, res) => {
  const currentSpan = trace.getTracer('default').startSpan('GET /');
  context.with(trace.setSpan(context.active(), currentSpan), () => {
    const traceId = currentSpan.spanContext().traceId;
    console.log(`Trace ID for GET /: ${traceId}`);
    res.send(`Hello, World! Trace ID: ${traceId}`);
    currentSpan.end();
  });
});

app.get('/trace', (req, res) => {
  const currentSpan = trace.getTracer('default').startSpan('GET /trace');
  context.with(trace.setSpan(context.active(), currentSpan), () => {
    const traceId = currentSpan.spanContext().traceId;
    console.log(`Trace ID for GET /trace: ${traceId}`);
    res.send(`This route is traced with OpenTelemetry! Trace ID: ${traceId}`);
    console.log('Trace route accessed');
    currentSpan.end();
  });
});

app.get('/slow', (req, res) => {
  const currentSpan = trace.getTracer('default').startSpan('GET /slow');
  context.with(trace.setSpan(context.active(), currentSpan), () => {
    setTimeout(() => {
      const traceId = currentSpan.spanContext().traceId;
      console.log(`Trace ID for GET /slow: ${traceId}`);
      res.send(`This is a slow route. Trace ID: ${traceId}`);
      currentSpan.end();
    }, 3000);
  });
});

app.get('/error', (req, res) => {
  const currentSpan = trace.getTracer('default').startSpan('GET /error');
  context.with(trace.setSpan(context.active(), currentSpan), () => {
    const traceId = currentSpan.spanContext().traceId;
    console.log(`Trace ID for GET /error: ${traceId}`);
    res.status(500).send(`This route returns an error. Trace ID: ${traceId}`);
    currentSpan.setStatus({ code: trace.SpanStatusCode.ERROR });
    currentSpan.end();
  });
});

exports.handler = (event, context) => {
  console.log("Handler invoked");
  return awsServerlessExpress.proxy(server, event, context, 'PROMISE').promise;
}
```

3. **Create `package.json`**:
```json
    {
  "name": "lambda-function",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "dependencies": {
    "@grpc/grpc-js": "^1.8.12",
    "@opentelemetry/api": "^1.9.0",
    "@opentelemetry/auto-instrumentations-node": "^0.47.1",
    "@opentelemetry/exporter-otlp-grpc": "^0.26.0",
    "@opentelemetry/sdk-node": "^0.52.1",
    "aws-sdk": "^2.1000.0",
    "aws-serverless-express": "^3.4.0",
    "express": "^4.19.2"
  },
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "author": "",
  "license": "ISC"
  }
```

4. **Install Dependencies**:
    ```sh
    npm install
    ```

## Dockerfile

```dockerfile
# Use the official AWS Lambda node image
FROM public.ecr.aws/lambda/nodejs:16

# Copy function code
COPY index.js package.json package-lock.json ./

# Install production dependencies
RUN npm install --only=production

# Command can be overwritten by providing a different command in the template directly.
CMD [ "index.handler" ]
```

## Create a Token for Login to Pulumi

1. **Create Pulumi Access Token**:
    - Go to the Pulumi Console at https://app.pulumi.com.
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

### `infra.yml`

```yaml
name: Pulumi Infra Setup

on:
  push:
    branches:
      - main
    paths:
      - 'infra/**'

jobs:
  setup_infra:
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
          python -m venv venv
          source venv/bin/activate
          pip install pulumi pulumi-aws

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Pulumi login
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
        run: pulumi login

      - name: Pulumi stack select
        run: pulumi stack select dev-p --cwd infra

      - name: Pulumi refresh
        run: pulumi refresh --yes --cwd infra

      - name: Pulumi up
        run: pulumi up --yes --cwd infra

      - name: Get Pulumi outputs
        run: pulumi stack output --json --cwd infra > outputs.json

      - name: Extract bucket name from Pulumi outputs
        id: get_bucket_name
        run: echo "::set-output name=bucket_name::$(jq -r .bucket_name outputs.json)"

      - name: Export Pulumi outputs to S3
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
          S3_BUCKET_NAME: ${{ steps.get_bucket_name.outputs.bucket_name }}
          S3_FILE_NAME: pulumi-outputs.json
        run: |
          aws s3 cp outputs.json s3://$S3_BUCKET_NAME/$S3_FILE_NAME

      - name: Clean up outputs.json
        run: rm outputs.json

      - name: Set output for S3 bucket name
        id: set_s3_output
        run: echo "bucket_name=${{ steps.get_bucket_name.outputs.bucket_name }}" >> $GITHUB_ENV
```

### `deploy-lambda.yml`

```yaml
name: Push Docker and Deploy Lambda

on:
  push:
    branches:
      - main
    paths:
      - 'deploy-in-lambda/**'
  workflow_run:
    workflows: ["Pulumi Infra Setup"]
    types:
      - completed

jobs:
  push_docker_and_deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      - name: Download Pulumi outputs from S3
        env:
          S3_BUCKET_NAME: ${{ github.event.workflow_run.outputs.bucket_name }}
        run: |
          aws s3 cp s3://$S3_BUCKET_NAME/pulumi-outputs.json ./outputs.json

      - name: Parse Pulumi outputs
        id: parse_outputs
        run: |
          ECR_REPO_URL=$(jq -r '.ecr_repo_url' ./outputs.json)
          ECR_REGISTRY=$(jq -r '.ecr_registry' ./outputs.json)
          LAMBDA_ROLE_ARN=$(jq -r '.lambda_role_arn' ./outputs.json)
          PRIVATE_SUBNET_ID=$(jq -r '.private_subnet_id' ./outputs.json)
          SECURITY_GROUP_ID=$(jq -r '.lambda_security_group_id' ./outputs.json)
          GRAFANA_TEMPO_PRIVATE_IP=$(jq -r '.ec2_private_ip' ./outputs.json)
          echo "ECR_REPO_URL=$ECR_REPO_URL" >> $GITHUB_ENV
          echo "ECR_REGISTRY=$ECR_REGISTRY" >> $GITHUB_ENV
          echo "LAMBDA_ROLE_ARN=$LAMBDA_ROLE_ARN" >> $GITHUB_ENV
          echo "PRIVATE_SUBNET_ID=$PRIVATE_SUBNET_ID" >> $GITHUB_ENV
          echo "SECURITY_GROUP_ID=$SECURITY_GROUP_ID" >> $GITHUB_ENV
          echo "GRAFANA_TEMPO_PRIVATE_IP=$GRAFANA_TEMPO_PRIVATE_IP" >> $GITHUB_ENV

      - name: Install AWS CLI
        run: |
          sudo apt-get update
          sudo apt-get install -y python3-pip
          pip3 install awscli

      - name: Login to AWS ECR
        env:
          AWS_REGION: us-east-1
          ECR_REPO_URL: ${{ env.ECR_REPO_URL }}
        run: |
          aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL

      - name: Build and push Docker image
        env:
          ECR_REPO_URL: ${{ env.ECR_REPO_URL }}
          IMAGE_TAG: latest
        run: |
          cd deploy-in-lambda
          docker build -t $ECR_REPO_URL:$IMAGE_TAG .
          docker push $ECR_REPO_URL:$IMAGE_TAG

      - name: Create or update Lambda function
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
          ECR_REPO_URL: ${{ env.ECR_REPO_URL }}
          IMAGE_TAG: latest
          LAMBDA_ROLE_ARN: ${{ env.LAMBDA_ROLE_ARN }}
          PRIVATE_SUBNET_ID: ${{ env.PRIVATE_SUBNET_ID }}
          SECURITY_GROUP_ID: ${{ env.SECURITY_GROUP_ID }}
          GRAFANA_TEMPO_PRIVATE_IP: ${{ env.GRAFANA_TEMPO_PRIVATE_IP }}
        run: |
          FUNCTION_NAME=my-node-app-lambda-function
          IMAGE_URI=$ECR_REPO_URL:$IMAGE_TAG
          EXISTING_FUNCTION=$(aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION 2>&1 || true)
          if echo "$EXISTING_FUNCTION" | grep -q 'ResourceNotFoundException'; then
            echo "Creating new Lambda function..."
            aws lambda create-function \
              --function-name $FUNCTION_NAME \
              --package-type Image \
              --code ImageUri=$IMAGE_URI \
              --role $LAMBDA_ROLE_ARN \
              --vpc-config SubnetIds=$PRIVATE_SUBNET_ID,SecurityGroupIds=$SECURITY_GROUP_ID \
              --region $AWS_REGION
          else
            echo "Updating existing Lambda function..."
            aws lambda update-function-code \
              --function-name $FUNCTION_NAME \
              --image-uri $IMAGE_URI \
              --region $AWS_REGION
          fi
```

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

![](https://github.com/Galadon123/Lambda-Function-with-Pulumi-python/blob/main/image/l-w-1.png)
![](https://github.com/Galadon123/Lambda-Function-with-Pulumi-python/blob/main/image/l-w-2.png)

## Resource Map Verification

After the Pulumi infrastructure setup, you can verify the resources in the AWS Management Console to ensure everything is created correctly.

![Resource Map](https://github.com/Galadon123/-Lambda-Function-Deployment/blob/main/image/o-4.png)

## Testing Lambda Function with JSON Query



1. **Select Your Lambda Function**:
   - In the Lambda console, find and select your deployed Lambda function.

2. **Create a Test Event**:
   - Click on the "Test" button in the top-right corner.
   - If this is your first time, you will be prompted to configure a test event.

3. **Configure the Test Event**:
   - Enter a name for the test event.
   - Replace the default JSON with your desired test JSON query, for example:
     ```json
     {
       "httpMethod": "GET",
       "path": "/",
       "headers": {
         "Content-Type": "application/json"
       },
       "body": null,
       "isBase64Encoded": false
     }
     ```

4. **Save and Test**:
   - Save the test event configuration.
   - Click on "Test" to execute the test event.

5. **View Results**:
   - Check the execution results, which will appear on the Lambda console.
   - Review the logs and output to verify that the Lambda function executed correctly.

   ![](https://github.com/Galadon123/-Lambda-Function-Deployment/blob/main/image/o-5.png)

This process allows you to test your Lambda function directly within the AWS Lambda console using a JSON query.

## EC2 Instance Setup for Grafana, Tempo, and OpenTelemetry Collector

### Step 1: Install Docker
1. Update packages and install Docker:
    ```sh
    sudo apt-get update -y
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
    ```

### Step 2: Install Docker Compose
1. Install Docker Compose:
    ```sh
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    ```

### Step 3: Set Up Directory Structure
1. Create a directory for your setup:
    ```sh
    mkdir ~/grafana-tempo-otel
    cd ~/grafana-tempo-otel
    ```

### Step 4: Create Configuration Files

#### `tempo.yaml`
Create `tempo.yaml` with the following content:
```yaml
auth_enabled: false

server:
  http_listen_port: 3200

ingester:
  trace_idle_period: 30s
  max_block_bytes: 5000000
  max_block_duration: 5m

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/traces

compactor:
  compaction:
    block_retention: 48h

querier:
  frontend_worker:
    frontend_address: 127.0.0.1:9095
```

#### `otel-collector-config.yaml`
Create `otel-collector-config.yaml` with the following content:
```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: "0.0.0.0:4317"

processors:
  batch:

exporters:
  otlp:
    endpoint: "tempo:4317"
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp]
```

#### `docker-compose.yml`
Create `docker-compose.yml` with the following content:
```yaml
version: '3'

services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

  tempo:
    image: grafana/tempo:latest
    ports:
      - "3200:3200"
    command: ["tempo", "serve", "--config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml

  otel-collector:
    image: otel/opentelemetry-collector:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"  # Expose the OTLP gRPC endpoint
      - "4318:4318"  # Expose the OTLP HTTP endpoint
```

### Step 5: Start Services
1. Navigate to the directory where you created the files and start the services using Docker Compose:
    ```sh
    cd ~/grafana-tempo-otel
    sudo docker-compose up -d
    ```

## Example Scenario: Trace Data Flow

1. **Application (Lambda Function)**:
    - Your application generates trace data and sends it to the OpenTelemetry Collector endpoint (`http://${ec2InstancePrivateIP}:4317`).

2. **OpenTelemetry Collector**:
    - The Collector receives the traces via the OTLP receiver.
    - The traces pass through the processing pipeline.
    - The `logging` exporter logs the trace data for debugging.
    - The `otlp` exporter sends the trace data to Tempo.

3. **Grafana Tempo**:
    - Tempo receives the trace data on its gRPC endpoint (`tempo:4317`).
    - Tempo processes and stores the traces in `/tmp/tempo/traces`.

4. **Grafana**:
    - Grafana queries Tempo to retrieve the stored trace data.
    - The traces are visualized in Grafana’s user interface, allowing you to analyze them.

## Grafana Setup for Traces with Tempo

### Step 1: Access Grafana
1. Open a web browser and navigate to `http://<ec2_instance_public_ip>:3000`.
2. Log in with the default credentials:
    - **Username**: admin
    - **Password**: admin

### Step 2: Add Tempo Data Source
1. In the Grafana UI, go to **Configuration** (gear icon) > **Data Sources**.
2. Click on **Add data source**.
3. Select **Tempo** from the list of available data sources.

### Step 3: Configure Tempo Data Source
1. Set the **HTTP URL** to `http://tempo:3200`.
2. Click **Save & Test** to ensure the connection to Tempo is successful.

### Step 4: Create a Dashboard
1. Go to **Create** (plus icon) > **Dashboard**.
2. Click on **Add new panel**.

### Step 5: Query Traces
1. In the query editor, select the Tempo data source.
2. Use TraceQL to query the traces. For example:
    ```traceql
    {}
    ```
    ![TraceQL](https://github.com/Galadon123/-Lambda-Function-Deployment/blob/main/image/o-1.png)
## Step 6: Managing and Understanding Trace Data
![](https://github.com/Galadon123/-Lambda-Function-Deployment/blob/main/image/o-2.png)

#### Explanation of Image Observations

1. **Disconnected Dots in Grafana Dashboard**: The dots represent trace data points. Disconnected dots indicate that traces are not being generated continuously.
2. **Lambda Function Invocation**: Each dot corresponds to a single invocation of the Lambda function. The intervals between dots show the time gap between successive invocations.


By following these steps, you can set up an EC2 instance to host Grafana, Tempo, and the OpenTelemetry Collector, enabling you to visualize and analyze trace data generated by your application. This setup ensures a robust and efficient workflow for deploying serverless applications and monitoring their performance.