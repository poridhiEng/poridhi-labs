# **Utilizing S3 Data Using Lambda and API Gateway**

 
In this guide, we will build a serverless data retrieval system using AWS services. The system will store data in an Amazon S3 bucket, process and fetch the data using an AWS Lambda function, and expose it through an API Gateway for easy access via a browser. By following a step-by-step approach, we will configure each AWS component, integrate them seamlessly, and deploy a fully functional serverless architecture. This setup ensures scalability, cost-efficiency, and minimal infrastructure management while providing a solid foundation for further enhancements such as authentication and database integration.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/1.svg)




## **Task Description**
We aim to build a system that:
- Stores data in an **Amazon S3 bucket**.
- Retrieves data using an **AWS Lambda function**.
- Exposes the data via **AWS API Gateway**.
- Displays the data on **browser**.



## **Step-by-Step Solution**

### **Step 1: Create an S3 Bucket and Upload Data**
1. Navigate to the [AWS S3 Console](https://s3.console.aws.amazon.com/s3/home).
2. Click **Create Bucket**.
3. Provide a unique bucket name (e.g., `my-data-bucket`).
4. Disable **Block all public access** (since Lambda will access it internally).

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-3.png)

5. Click **Create bucket**.

6. Now create a sample json file `data.json` with a message:
    ```json
    {
        "user": "Poridhi.io",
        "message": "Hello poridhian! This message is from S3!"
    }
    ```


6. Open the newly created bucket, click **Upload**, and upload a JSON file named `data.json`.   


### **Step 2: Create an IAM Role for Lambda**
1. Navigate to the [AWS IAM Console](https://console.aws.amazon.com/iam/home).
2. Click **Roles** → **Create Role**.
3. Choose **AWS Service** → Select **Lambda**.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-5.png)

4. Attach the **AmazonS3ReadOnlyAccess** policy.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-4.png)

5. Name the role **LambdaS3AccessRole**.
6. Click **Create Role**.



### **Step 3: Create an AWS Lambda Function**
1. Navigate to the [AWS Lambda Console](https://console.aws.amazon.com/lambda/home).
2. Click **Create function**.
3. Choose **Author from scratch**.
4. Provide a function name: `s3-data-fetcher`.
5. Select **Python 3.x** as the runtime.
6. Choose the existing IAM role: **LambdaS3AccessRole**.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-6.png)

7. Click **Create function**.
8. Replace the default code with the following:
    ```python
    import boto3
    import json

    def lambda_handler(event, context):
        s3 = boto3.client("s3")
        bucket = "your-bucket-name"
        key = "your-json-file-name.json"
        response = s3.get_object(Bucket=bucket, Key=key)
        json_data = response["Body"].read().decode("utf-8")
        json_content = json.loads(json_data)
        
        return {
            'statusCode': 200,
            'body': json_content
        }
    ```
    Replace `your-bucket-name` and `your-json-file.json` with appropriate values.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-7.png)

9. Click **Deploy**.


### Step 4: Create a Test Event and Execute the Lambda Function
1. Click **Test**, then select **Configure test event**.
2. Enter `test` in the **Event name** field.
3. Replace the sample empty event JSON with the following:

    ```json
    {}
    ```

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image.png)

4. Click **Format JSON** to validate the JSON.
5. Click **Save**.
6. Click **Test** to execute the function.
7. Review the execution results displayed on the screen.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-1.png)



### **Step 5: Deploy an API Gateway**
1. Navigate to the [API Gateway Console](https://console.aws.amazon.com/apigateway/home).
2. Click **Create API** → Choose **REST API**.
3. Name it **my-api-gateway**.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-2.png)

4. Click **Create**.

5. Create a **Resource** and name it as **get-data**. Leave Configure as proxy resource unchecked. Leave Enable API Gateway CORS unchecked. Click on Create Resource.

6. Create a **GET method** for the `get-data` resource.
7. Set **Integration type**: Lambda Function.

9. Select the **s3-data-fetcher** function.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-8.png)

10. Deploy the API to a **new stage** called `prod`.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-9.png)

8. Click **Create** and copy the **Invoke URL** (e.g., `https://xyz.execute-api.region.amazonaws.com`). Add the `/get-data` route with the invoke URL. 

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/AWS%20Lambda%20Labs/Lab%2004/images/image-10.png)



## **Conclusion**
- We successfully created a serverless system using AWS Lambda, S3, and API Gateway.
- This setup enables efficient retrieval and display of data on browser.
- The system can be further enhanced with authentication, data filtering, and database integration.


