# **AWS S3 Event Notification with Lambda and SES**


In this lab, we will set up an AWS S3 bucket to trigger an AWS Lambda function whenever an object is created or deleted in the bucket. The Lambda function will, in turn, send an email notification using AWS Simple Email Service (SES). This tutorial will guide you through the step-by-step setup process, including IAM role creation, Lambda function configuration, SES email verification, and S3 event notification setup.



## **Architecture Explanation**

![](./images/1.svg)

The architecture consists of the following AWS services:
1. **Amazon S3**: Stores objects and triggers events when an object is created or deleted.
2. **AWS Lambda**: A function that processes S3 events and triggers email notifications.
3. **AWS Simple Email Service (SES)**: Sends an email notification to a predefined email address.
4. **AWS IAM**: Defines permissions for the Lambda function to interact with SES and S3.

### **Workflow:**
1. An object is added to or deleted from an S3 bucket.
2. The event triggers an AWS Lambda function.
3. The Lambda function processes the event and sends an email via SES.
4. The email is received by the recipient.



## **Task Description**
Your task is to set up:
- An S3 bucket with event notifications enabled.
- A Lambda function that processes S3 events.
- An IAM role with permissions for Lambda to access S3 and SES.
- An SES email identity for sending notifications.
- A test to verify the end-to-end setup.



## **Step-by-Step Solution**

### **Step 1: Create an IAM Policy and Role**
1. Open the **AWS IAM Console**.
2. Go to **Policies** and click **Create Policy**.
3. Add the following JSON:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "VisualEditor0",
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "ec2:RunInstances",
        "ec2:StartInstances",
        "ec2:StopInstances",
        "cloudwatch:DescribeAlarms",
        "compute-optimizer:GetEnrollmentStatus",
        "elasticloadbalancing:Describe*"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ec2:Region": "ap-southeast-1"
        }
      }
    },
    {
      "Sid": "SESLimitedAccess",
      "Effect": "Allow",
      "Action": [
        "ses:CreateCustomVerificationEmailTemplate",
        "ses:Describe*",
        "ses:Get*",
        "ses:List*",
        "ses:VerifyEmailAddress",
        "ses:VerifyEmailIdentity",
        "ses:CreateEmailIdentity",
        "ses:TagResource",
        "route53:List*",
        "ses:SendEmail",
        "ses:SendRawEmail",
        "ses:SendTemplatedEmail"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "ap-southeast-1"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": ["logs:*"],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::*"
    }
  ]
}
```    
4. Name the policy **LambdaS3SESAccess** and create it.



5. Go to **Roles** and click on **Create Role**.
6. Choose **AWS Service** and select **Lambda**.
7. Click **Next** and go to **Permissions**.
8. Search for **LambdaS3SESAccess** policy and select it then click next. 
7. Name the role **LambdaEmailNotifierRole** and create it.

    ![alt text](image.png)



### **Step 2: Create the Lambda Function**
1. Open the **AWS Lambda Console**.
2. Click **Create Function**.
3. Choose **Author from scratch**.
4. Name it **EmailNotifier**.
5. Choose **Python 3.X** as the runtime.
6. Choose **Use an existing role** and select **LambdaEmailNotifierRole**.

    ![alt text](image-1.png)

7. Click **Create Function**.



### **Step 3: Add the Lambda Function Code**
1. In the Lambda function editor, replace the default code with:

    ```python
    import boto3
    import json

    def lambda_handler(event, context):
        
        for e in event["Records"]:
            bucketName = e["s3"]["bucket"]["name"]
            objectName = e["s3"]["object"]["key"]
            eventName = e["eventName"]
        
        bClient = boto3.client("ses")
        
        eSubject = 'AWS' + str(eventName) + 'Event'
        
        eBody = """
            <br>
            Hey,<br>
            
            Welcome to Poridhi AWS Lambda Lab<br>
            AWS S3 Event Notification with Lambda and SES<br>
            
            We are here to notify you that {} an event was triggered.<br>
            Bucket name : {} <br>
            Object name : {}
            <br>
        """.format(eventName, bucketName, objectName)
        
        send = {"Subject": {"Data": eSubject}, "Body": {"Html": {"Data": eBody}}}
        result = bClient.send_email(Source= "<YOUR-MAIL-ADDRESS>", Destination= {"ToAddresses": ["<YOUR-MAIL-ADDRESS>"]}, Message= send)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    ```

    Replace `<YOUR-MAIL-ADDRESS>` with your valid email address.

2. Click **Deploy**.



### **Step 4: Verify Your Email in SES**
1. Open the **AWS SES Console**.
2. From the menu select **Identities** then click **Create Identity**. 

    ![alt text](image-2.png)

3. Click **Email Address** and provide your valid email address.

    ![alt text](image-11.png)

4. Click **Create Identity**.
5. AWS will send a verification email.

    ![alt text](image-12.png)

6. Open your email and click the verification link.
7. Once verified, refresh the SES console.

    ![alt text](image-13.png)





### **Step 5: Create an S3 Bucket**
1. Open the **AWS S3 Console**.
2. Click **Create Bucket**.
3. Name it **my-s3-event-bucket** (choose a unique name).
4. Leave all settings as default and click **Create Bucket**.

    ![alt text](image-6.png)

### **Step 6: Configure S3 Event Notification**
1. Open the **S3 bucket** you created.
2. Go to the **Properties** tab.
3. Scroll down to **Event Notifications**.

    ![alt text](image-7.png)

4. Click **Create event notification**.
5. Name it **S3EventTrigger**.
6. Select **All object create events** and **All object delete events**.

    ![alt text](image-8.png)

7. Scroll to **Destination**, choose **Lambda Function**.
8. Select **EmailNotifier** Lambda function.

    ![alt text](image-9.png)

9. Click **Save Changes**.



### **Step 7: Test the Setup**
1. Go to the **S3 bucket**.
2. Click **Upload**, select a random file, and upload it.
3. Open your email and check for the notification.

    ![alt text](image-10.png)



## **Conclusion**
In this lab, we set up an S3 event notification system where object creation or deletion triggers a Lambda function that sends an email via AWS SES. This setup can be extended for real-world applications requiring automated notifications.

Now, try modifying the Lambda function to customize email content or add support for multiple email recipients!

