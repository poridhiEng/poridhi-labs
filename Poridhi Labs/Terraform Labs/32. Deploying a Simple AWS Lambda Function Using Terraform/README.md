## Deploying a Simple AWS Lambda Function Using Terraform

In this lab, you'll learn how to deploy a simple AWS Lambda function using Terraform. AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers. You'll deploy a basic Lambda function that returns a "Hello, World!" message when invoked.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/32.%20Deploying%20a%20Simple%20AWS%20Lambda%20Function%20Using%20Terraform/images/logo.png?raw=true)

## Objectives

1. Write a "Hello, World!" Lambda function in Node.js.
2. Package the function into a ZIP file.
3. Deploy the Lambda function using Terraform.
4. Set up an IAM role with necessary permissions.
5. Test the Lambda function using the AWS CLI and Console.

## Prerequisites

1. **AWS Account**: Ensure you have an active AWS account.
2. **AWS CLI**: Install and configure the AWS CLI with `aws configure`.
3. **Terraform**: Install Terraform on your local machine.

## What is an AWS Lambda Function?

AWS Lambda is a compute service that allows you to run code without managing servers. Simply write your code, upload it to Lambda, and the service takes care of scaling and execution. Lambda functions are often used in event-driven applications, such as responding to HTTP requests, processing S3 bucket files, or reacting to database changes.

## Project Directory Structure

```plaintext
terraform-lambda-lab/
├── function.zip
├── index.js
└── main.tf
```

- `index.js`: Contains the Node.js code for the AWS Lambda function.
- `function.zip`: The ZIP file containing the Lambda function code, created from `index.js`.
- `main.tf`: The Terraform configuration file that defines the AWS resources, including the Lambda function, IAM role, and permissions.

## Step 1: Writing the Lambda Function

### Create the Lambda Function

1. Create a directory for your Lambda function:

    ```bash
    mkdir terraform-lambda-lab
    cd terraform-lambda-lab
    ```

2. Inside this directory, create a file named `index.js` with the following content:

    ```javascript
    exports.handler = async (event) => {
        const response = {
            statusCode: 200,
            body: JSON.stringify('Hello, World!'),
        };
        return response;
    };
    ```

   This simple Node.js function returns a JSON response with the message "Hello, World!".

### Package the Lambda Function

Package the Lambda function into a ZIP file for deployment:

If `zip` is not installed on your machine, install it by running:

```bash
sudo apt install zip
```

Then, package the function:

```bash
zip function.zip index.js
```

This command creates a `function.zip` file containing your Lambda function code.

## Step 2: Setting Up Terraform

### Create the Terraform Configuration

Create a `main.tf` file with the following content:

```py
provider "aws" {
  region = "ap-southeast-1"
}

# IAM role for the Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
    }],
  })
}

# Attach the AWSLambdaBasicExecutionRole policy to the role
resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Deploy the Lambda function
resource "aws_lambda_function" "hello_world" {
  function_name = "hello-world-function"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "nodejs20.x"
  filename      = "${path.module}/function.zip"
  source_code_hash = filebase64sha256("${path.module}/function.zip")
}

# Permission to invoke the Lambda function
resource "aws_lambda_permission" "allow_invoke" {
  statement_id  = "AllowExecutionFromAny"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.hello_world.function_name
  principal     = "lambda.amazonaws.com"
}
```

### Explanation of `main.tf`

- **Provider Configuration:** Specifies the AWS region where resources will be deployed.
- **IAM Role:**
  - **aws_iam_role.lambda_role:** Creates an IAM role that the Lambda function will assume. The role includes a policy allowing Lambda to assume the role.
  - **aws_iam_role_policy_attachment.lambda_policy:** Attaches the AWS-provided `AWSLambdaBasicExecutionRole` policy to the IAM role, granting permissions to write logs to CloudWatch.
- **Lambda Function:** 
  - **aws_lambda_function.hello_world:** Deploys the Lambda function using the Node.js runtime. The function code is provided in the `function.zip` file, and the handler is set to `index.handler`.
  - **aws_lambda_permission.allow_invoke:** Grants permission for the Lambda function to be invoked by any AWS service.

## Step 3: Applying the Terraform Configuration

### Initialize Terraform

Initialize Terraform to set up the environment and download the necessary providers:

```bash
terraform init
```

### Apply the Configuration

Apply the Terraform configuration to deploy the Lambda function and related resources:

```bash
terraform apply
```

Type `yes` when prompted to confirm the creation of resources.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/32.%20Deploying%20a%20Simple%20AWS%20Lambda%20Function%20Using%20Terraform/images/4.png?raw=true)

## Step 4: Invoking the Lambda Function

### Use the AWS CLI to Invoke the Function

Invoke the Lambda function using the AWS CLI:

```bash
aws lambda invoke \
    --function-name hello-world-function \
    --payload '{}' \
    response.json
```

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/32.%20Deploying%20a%20Simple%20AWS%20Lambda%20Function%20Using%20Terraform/images/1.png?raw=true)

This command invokes the Lambda function and saves the response to `response.json`.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/32.%20Deploying%20a%20Simple%20AWS%20Lambda%20Function%20Using%20Terraform/images/2.png?raw=true)

### Check the Response

Check the contents of `response.json`:

```bash
cat response.json
```

You should see the "Hello, World!" message in the response.

### Test the Lambda Function in the AWS Console

1. **Log in to the AWS Management Console** and navigate to the **Lambda** service.
2. **Select your Lambda function** (e.g., `hello-world-function`).
3. Click on the **Test** button in the Lambda console.
4. **Create a new test event**:
    - Name the test event (e.g., "TestEvent").
    - Use the default JSON template for the test event.

    ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/32.%20Deploying%20a%20Simple%20AWS%20Lambda%20Function%20Using%20Terraform/images/6.png?raw=true)

5. **Click on Test** to invoke the function directly from the console.
6. **View the results**: The output should show the "Hello, World!" message.
   - ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/32.%20Deploying%20a%20Simple%20AWS%20Lambda%20Function%20Using%20Terraform/images/5.png?raw=true)



## Conclusion

In this lab, you created a simple "Hello, World!" AWS Lambda function using Node.js, packaged it into a ZIP file, and deployed it using Terraform. You also set up the necessary IAM role and permissions for the Lambda function, invoked it using the AWS CLI, and verified it using both the CLI and the AWS Management Console. This lab provides a foundational understanding of deploying Lambda functions with Terraform, which you can build upon for more complex serverless applications.
