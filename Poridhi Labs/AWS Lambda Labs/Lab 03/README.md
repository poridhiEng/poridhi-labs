# Creating an EC2 Instance with Lambda 


AWS Lambda is a serverless compute service that allows running code without provisioning or managing servers. In this hands-on lab, we will write a Lambda function in Python using the Boto3 library to create an EC2 instance. We will also set up an IAM role with a custom execution policy for our Lambda function. Once the instance is created, we will connect to it via SSH.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2003/images/1.svg)


### **Use Cases**
- Automating EC2 instance provisioning for on-demand workloads.
- Creating backup or test instances dynamically.
- Implementing auto-scaling mechanisms.
- Reducing infrastructure costs by spinning up instances only when needed.

## **Task Description**
We will:
1. Create an EC2 Key Pair.
2. Set up a Lambda function.
3. Configure an IAM role with necessary permissions.
4. Define environment variables.
5. Deploy and test the Lambda function.
6. Connect to the EC2 instance via SSH.



## **Step-by-Step Solution**

### **1. Create EC2 Key Pair**
1. Navigate to **EC2** in the AWS console.
2. In the navigation pane, under **NETWORK & SECURITY**, choose **Key Pairs**.
3. Click **Create Key Pair**.
4. Enter a key pair name (e.g., `LambdaEC2keypair`).
5. Click **Create** and download the private key file (`.pem`).
    
    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2003/images/image.png)

6. Store the file securely, as it will be needed for SSH access.

### **2. Create a Lambda Function**
1. Navigate to **Lambda** in the AWS console.
2. Click **Create function**.
3. Choose **Author from scratch** and configure the following:
   - **Name**: `CreateEC2`
   - **Runtime**: `Python 3.x`
   - **Role**: `Create a new role with basic Lambda permissions`

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2003/images/image-1.png)

4. Expand **Choose or create an execution role**.
5. Copy the execution role name and save it for later use.
6. Click **Create function**.
    

### **3. Configure IAM Role with Custom Policy**
1. Open a new browser tab and navigate to **IAM**.
2. Click **Roles** and search for the role created (in our case: `CreateEC2-role-6d4vz5u0`) for Lambda.
3. Select the role and click the attached policy.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2003/images/image-2.png)

4. Click **Edit policy > JSON** and replace the existing policy with:

```json
{
  "Version": "2025-02-07",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Action": [
        "ec2:RunInstances"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
```
5. Click **Review policy** and then **Save changes**.

### **4. Define Environment Variables**
1. In the Lambda console, navigate to the `CreateEC2` function.
2. Go to **Configuration** > **Environment variables**.
3. Set the following variables:
   - **Key:** `AMI` | **Value:** Copy the AMI ID of Ubuntu from the EC2 Launch Instance page.
   - **Key:** `INSTANCE_TYPE` | **Value:** `t2.micro`
   - **Key:** `KEY_NAME` | **Value:** Name of the EC2 key pair created earlier.
   - **Key:** `SUBNET_ID` | **Value:** Copy a public subnet ID from **VPC > Subnets**. (If there is no VPC/public subnet, create one first.)
4. Click **Save**.

### **5. Deploy and Test the Lambda Function**
1. In the **Function code** section, paste the Python script for launching an EC2 instance (from a provided GitHub source).

    ```python
    import os
    import boto3

    AMI = os.environ['AMI']
    INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
    KEY_NAME = os.environ['KEY_NAME']
    SUBNET_ID = os.environ['SUBNET_ID']

    ec2 = boto3.resource('ec2')


    def lambda_handler(event, context):

        instance = ec2.create_instances(
            ImageId=AMI,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            SubnetId=SUBNET_ID,
            MaxCount=1,
            MinCount=1
        )

        print("New instance created:", instance[0].id)
    ```

2. Click **Save**.
3. Click **Deploy**.
4. Click **Test** and define an empty test event (`{}`).
5. Click **Create**, then **Test**.
6. Navigate to **EC2 > Instances** and verify that an instance is initializing.

### **6. Connect to the EC2 Instance via SSH**
1. Open a terminal and navigate to the directory where the `.pem` file is stored.
2. Set file permissions:
   ```bash
   chmod 400 LambdaEC2keypair.pem
   ```
3. Connect via SSH:
   ```bash
   ssh -i LambdaEC2keypair.pem ec2-user@<IP_ADDRESS>
   ```
   - Replace `<IP_ADDRESS>` with the public IP of the EC2 instance.
4. Alternatively, use the **Connect** option in the AWS EC2 console to retrieve the SSH command.

## **Conclusion**
You have successfully created an AWS Lambda function that provisions an EC2 instance using Boto3. This method can be used to automate infrastructure deployment, implement auto-scaling, and reduce operational overhead. Great job on completing this hands-on lab!

