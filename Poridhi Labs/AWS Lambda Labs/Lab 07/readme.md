# Deploying a Serverless Application Using AWS Lambda, API Gateway, and DynamoDB

In this hands-on lab, you will learn how to build and deploy a fully serverless application using key AWS services. The lab will guide you through setting up an architecture that integrates **Amazon API Gateway**, **AWS Lambda**, and **Amazon DynamoDB** to create a scalable and cost-effective solution. By the end of the session, you will have hands-on experience in deploying a cloud-based application without managing any servers.


![image](./images/dynamo.drawio%20.png)
 

---

## **Step 1: Create a DynamoDB Table**  

### **1. Open the DynamoDB Console**  
- Sign in to your **AWS Management Console**.  
- Navigate to **Amazon DynamoDB** from the AWS services menu.  

### **2. Create a New Table**  
- Click on **Tables** from the left-hand menu.  
- Select **Create Table** to start the setup.  

### **3. Configure Table Details**  
- **Table Name** → Enter **`Quotes`**.  
- **Partition Key** → Enter **`quote`**, set the type to **String**.  
- **Sort Key** → Enter **`author`**, set the type to **String**.  

### **4. Customize Table Settings**  
- Scroll down to **Table settings** and select **Customize settings**.  
- **Table Class** → Choose **DynamoDB Standard**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/ae00ae8e-3495-4b78-af64-a5a54e3c4966.png)

### **5. Configure Read/Write Capacity**  
- Under **Read/write capacity settings**:  
  - **Capacity mode** → Select **Provisioned**.  
  - **Read Capacity Auto Scaling** → Turn **ON**.  
    - **Minimum capacity**: **1**  
    - **Maximum capacity**: **5**  
    - **Target utilization**: **20%**  
  - **Write Capacity Auto Scaling** → Turn **ON**.  
    - **Minimum capacity**: **1**  
    - **Maximum capacity**: **5**  
    - **Target utilization**: **20%**  
    
![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/1d0863a3-f900-484a-bdaa-120ad9035dbc.png)

### **6. Configure Encryption**  
- Under **Encryption at rest settings**, select **AWS managed key** (default).  




### **7. Create the Table**  
- Scroll to the bottom and click **Create table**.  
- Wait until the table is successfully created before proceeding to the next step.  


Here’s a **simplified and structured guide** to creating AWS Lambda functions for handling quotes.  

---

## **Step 2: Create Lambda Functions**  
We will create two Lambda functions:  
1. **PutQuotes** – Stores quotes in DynamoDB.  
2. **GetQuotes** – Retrieves quotes from DynamoDB.  

---

### **🔹 Create the PutQuotes Function**  

#### **1. Open the AWS Lambda Console**  
- Sign in to **AWS Management Console**.  
- Navigate to **AWS Lambda**.  

#### **2. Create a New Lambda Function**  
- Click on **Functions** in the left menu.  
- Click **Create function**.  
- Select **Author from scratch**.  

#### **3. Configure Function Details**  
- **Function name** → Enter **`PutQuotes`**.  
- **Runtime** → Choose **Python 3.12**.  
- **Architecture** → Ensure **x86_64** is selected.  

#### **4. Set Execution Role**  
- Expand **Change default execution role**.  
- Under **Execution role**, select **Create a new role from AWS policy templates**.  
- **Role name** → Enter **`PutQuotesRole`**.  
- Expand **Policy templates - optional** and select **Simple microservice permissions**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/ea3ac0b2-8521-43a7-b65d-b42ccb1f722b.png)

#### **5. Create the Function**  
- Scroll to the bottom and click **Create function**.  

#### **6. Update Configuration Settings**  
- Click on the **Configuration** tab.  
- Under **General Configuration**, click **Edit**.  
- **Timeout** → Set to **1 min 0 sec**, then click **Save**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/8eeee0f9-5c38-462f-9c16-331e944ed0db.png)


#### **7. Add Code to PutQuotes Function**  
- Navigate to the **Code** tab.  
- Copy and paste the **PutQuotes Lambda function code** 

```python
import boto3
from botocore.exceptions import ClientError
import http.client
import json
import os

TABLE_NAME = "Quotes"


def get_quote():
    # Get a random quote from the internet
    conn = http.client.HTTPSConnection("zenquotes.io")
    conn.request("GET", "/api/random")
    response = conn.getresponse()

    if response.status == 200:
        data = json.loads(response.read().decode())
        quote = data[0]["q"]
        author = data[0]["a"]

        # Return the quote in the response
        return {"quote": quote, "author": author}
    else:
        # Handle any potential errors
        return {"body": f"Failed to fetch a quote. Error code: {response.status}"}


def put_quote(quote):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)

    item = {
        "quote": quote["quote"],
        "author": quote["author"],
    }

    try:
        response = table.put_item(Item=item)
        return "Quote successfully written to DynamoDB."
    except ClientError as e:
        print(e)
        return "Error writing item to DynamoDB."


def lambda_handler(event, context):
    return put_quote(get_quote())

```
- Click **Deploy**.  

---

### **🔹 Create the GetQuotes Function**  

#### **1. Create a New Lambda Function**  
- Go back to the **Lambda console** → Click **Functions** → **Create function**.  
- Select **Author from scratch**.  

#### **2. Configure Function Details**  
- **Function name** → Enter **`GetQuotes`**.  
- **Runtime** → Choose **Python 3.12**.  
- **Architecture** → Ensure **x86_64** is selected.  

#### **3. Set Execution Role**  
- Expand **Change default execution role**.  
- Under **Execution role**, select **Create a new role from AWS policy templates**.  
- **Role name** → Enter **`GetQuotesRole`**.  
- Expand **Policy templates - optional** and select **Simple microservice permissions**.  

#### **4. Create the Function**  
- Scroll to the bottom and click **Create function**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/b8871b38-0427-4289-a3cc-17056c56f771.png)


#### **5. Update Configuration Settings**  
- Click on the **Configuration** tab.  
- Under **General Configuration**, click **Edit**.  
- **Timeout** → Set to **1 min 0 sec**, then click **Save**.  



#### **6. Add Code to GetQuotes Function**  
- Navigate to the **Code** tab.  
- Copy and paste the **GetQuotes Lambda function code** from the GitHub repository. 

```python
import boto3
from botocore.exceptions import ClientError
import random
import os

TABLE_NAME ="Quotes"


def lambda_handler(event, context):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)  # Replace with your DynamoDB table name

    try:
        # Perform the scan operation on the table
        response = table.scan()
        items = response["Items"]

        # Check if the table has items
        if not items:
            return {"statusCode": 404, "body": "No items found in the table."}

        # Select a random item
        random_item = random.choice(items)
        print(random_item)
        return {"statusCode": 200, "body": f'{random_item["quote"]} -- {random_item["author"]}'}

    except ClientError as e:
        print(e)
        return {"statusCode": 500, "body": "Error scanning the DynamoDB table."}


```
- Click **Deploy**.  

---

✅ **Next Step:** Move on to creating the **Amazon API Gateway REST API!** 🚀




## **Step 3: Create a Regional REST API in API Gateway**
We will:
1. Create a **Regional REST API**.
2. Add two resources:  
   - **PutQuotes** (for storing quotes).  
   - **GetQuotes** (for retrieving quotes).  
3. Integrate them with their respective **Lambda functions**.

---

### **🔹 Step 1: Create a Regional REST API**
#### **1. Open the API Gateway Console**
- Sign in to **AWS Management Console**.  
- Navigate to **API Gateway**.  

#### **2. Create a New REST API**
- On the **landing page**, find the **REST API** section and click **Build**.  
- Under **API details**, choose **New API**.  
- **API Name** → Enter **`Quotes`**.  
- (Optional) **Description** → Provide a brief description.  
- **Endpoint type** → Select **Regional**.  
- Click **Create API**.  



✅ Now, your API Gateway is set up! Let’s add resources and methods.

---

### **🔹 Step 2: Create the PutQuotes Resource**
We will create a resource named **PutQuotes**, which will store quotes in DynamoDB.

#### **1. Navigate to Resources**
- In your newly created API, find and select **Resources** in the left menu.  

#### **2. Create the PutQuotes Resource**
- Click **Create Resource**.  
- **Resource Path** → Leave it as **`/`**.  
- **Resource Name** → Enter **`PutQuotes`**.  
- Click **Create Resource**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/653e9ba5-52f1-4697-b331-c42bec53e754.png)

#### **3. Create the ANY Method**

- Select the **PutQuotes** resource.  
- Click **Create Method**.  
- **Method type** → Select **ANY** from the dropdown.  
- **Integration type** → Select **Lambda Function**.  
- **Lambda Proxy Integration** → Ensure **this is disabled**.  
- **Lambda Function** → Choose **us-east-1**, then select **`PutQuotes`** from the dropdown.  
- Leave **Default timeout enabled**.  
- Click **Create Method**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/441cc601-6f90-43ab-bd2d-da781bf058a7.png)

✅ The **PutQuotes** resource is now linked to your Lambda function!

---

### **🔹 Step 3: Create the GetQuotes Resource**
Now, we will create the **GetQuotes** resource to retrieve quotes.

#### **1. Create the GetQuotes Resource**
- In the **Resources** section, click **Create Resource**.  
- **Resource Path** → Leave it as **`/`**.  
- **Resource Name** → Enter **`GetQuotes`**.  
- Click **Create Resource**.  

#### **2. Create the ANY Method**
- Select the **GetQuotes** resource.  
- Click **Create Method**.  
- **Method type** → Select **ANY** from the dropdown.  
- **Integration type** → Select **Lambda Function**.  
- **Lambda Proxy Integration** → **Enable this option**.  
- **Lambda Function** → Choose **us-east-1**, then select **`GetQuotes`** from the dropdown.  
- Leave **Default timeout enabled**.  
- Click **Create Method**.  

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/de1ab777-f68b-41a2-8383-393c92c49b5b.png)

✅ Your **GetQuotes** resource is now linked to the Lambda function!

---

### **Next Steps**
1. **Deploy the API** and generate an invoke URL.  
2. **Test the API** using **Postman** or **AWS Console**.  

🚀 **Now move on to deploying your API!** 🎯




## **Step 4: Deploy, Log, and Test Your API**
### **✅ Step 1: Deploy the API**
1. **Open the API Gateway Console**  
   - Navigate to **Amazon API Gateway**.  
   - Select your **Quotes REST API**.  

2. **Deploy the API**
   - Find and click **Deploy API**.  
   - In the popup, for **Stage**, select **New Stage**.  
   - **Stage Name** → Enter **`prod`** (or any other preferred name).  
   - *(Optional)* Add a **description**.  
   - Click **Deploy**.  


![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/5006b84b-ce4c-49c3-b474-8173b8cdcd99.png)

3. **Find Your Invoke URL**
   - After deployment, you will be redirected to the **stage settings**.  
   - In the **left menu**, click **Settings**.  
   - Copy the **Invoke URL** provided.  

---

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/125eae2a-10d0-4a6e-ab10-1deead3f2c54.png)


### **✅ Step 2: Test the API**
1. **Open a Private/Incognito Browser Tab**
   - Paste the **Invoke URL** into the address bar.  
   - You should see an error message—this is expected because no resource is specified.  

2. **Test the `PutQuotes` Function**
   - Append `/PutQuotes` to the **Invoke URL**.  
     ```
     https://your-api-id.execute-api.us-east-1.amazonaws.com/development/PutQuotes
     ```
   - Press **Enter**.  
   - If everything is set up correctly, you should see:  
     ```
     Item successfully written to DynamoDB
     ```
   - Refresh the page multiple times to insert more quotes into the database.  

3. **Verify in DynamoDB**
   - Navigate to the **DynamoDB console**.  
   - Find the **Quotes table**.  
   - Click **Explore table items** to check if new quotes were added.  

4. **Test the `GetQuotes` Function**
   - Replace `/PutQuotes` with `/GetQuotes` in the **Invoke URL**.  
     ```
     https://your-api-id.execute-api.us-east-1.amazonaws.com/development/GetQuotes
     ```
   - Press **Enter**.  
   - You should see a **random quote** from your database.  
   - Refresh to get different quotes.  



## **🎯 Conclusion**
🎉 **Congratulations!** You have successfully deployed and tested a **fully serverless API** using **API Gateway, Lambda, and DynamoDB**. 🚀  


