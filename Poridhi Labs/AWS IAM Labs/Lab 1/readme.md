# Create and Assume Roles in AWS 

AWS Identity and Access Management (IAM) is a service that allows AWS customers to manage user access and permissions for the accounts and available APIs/services within AWS. IAM can manage users, security credentials (such as API access keys), and allow users to access AWS resources.

In this lab, we discover how security policies affect IAM users and groups, and we go further by implementing our own policies while also learning what a role is, how to create a role, and how to assume a role as a different user.

By the end of this lab, you will understand IAM policies and roles, and how assuming roles can assist in restricting users to specific AWS resources.



![images](./images/1.svg)

## **Create 4 S3 Buckets**

Navigate to the S3 dashboard and click **Create Bucket**. Create the following buckets:

- `poridhiprod1`
- `poridhiprod2`
- `poridhistageconfig3`
- `poridhistageconfig4`

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/1f82c79e-9920-460f-b7ff-9f4d23c6fb6b.png)



## **Create IAM Users with Email Tag**

This Section instruct you  to create two IAM users in AWS without assigning any AWS managed policies. Each user will be tagged with an email tag (`Email:poridhistudent@gmail.com`).



### **Steps to Create IAM Users**

#### **Method 1: Using AWS Management Console**

1. **Sign in to the AWS Management Console**  
   Navigate to IAM by using the AWS console.

2. **Create the First IAM User**  
   - Navigate to **Users** in the left-hand menu and click **Add users**.
   - Enter a username for the first user (e.g., `User1`).
   - Click **Next: Permissions**.

3. **Set Permissions**  
   - Select `Attach Policies Directly` but do not attach any policies. Click **Next: Tags**.

![iam-permission](https://s3.brilliant.com.bd/blog-bucket/thumbnail/d184d67c-2575-41a2-ba49-6327dfcf2d8b.png)

4. **Add Tags**  
   - Click **Add tag**.
   - Enter `Email` as the key and `poridhistudent@gmail.com` as the value.
   - Click **Next: Review**.

![tag](https://s3.brilliant.com.bd/blog-bucket/thumbnail/579226c4-ca27-40f2-81b3-eb8c95762d3d.png)

5. **Review and Create**  
   - Review the details and click **Create user**.
   - Save the credentials (Access Key ID and Secret Access Key) securely.

6. **Enable Console Access**  
   - Select `User1` and go to the user details page.
   - Then, select the **Security Credentials** tab and click **Enable console access**.

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/58eed050-2da6-4f16-a92f-d08005a31369.png)

7. **Repeat for the Second User**  
   - Follow the same steps to create the second user (e.g., `User2`).



#### **Method 2: Using AWS CLI**

1. **Install and Configure AWS CLI**  
   If not already installed, follow the [AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).  
   Configure the CLI with your credentials using:  
   ```bash
   aws configure
   ```

2. **Create the First IAM User**  
   Run the following command to create the first user:  
   ```bash
   aws iam create-user --user-name User1
   ```

3. **Tag the First User**  
   Add the email tag to the first user:  
   ```bash
   aws iam tag-user --user-name User1 --tags Key=Email,Value=poridhistudent@gmail.com
   ```

4. **Create the Second IAM User**  
   Run the following command to create the second user:  
   ```bash
   aws iam create-user --user-name User2
   ```

5. **Tag the Second User**  
   Add the email tag to the second user:  
   ```bash
   aws iam tag-user --user-name User2 --tags Key=Email,Value=poridhistudent@gmail.com
   ```

6. **Verify the Users**  
   To verify the users and their tags, run:  
   ```bash
   aws iam list-users
   aws iam get-user --user-name User1
   aws iam get-user --user-name User2
   ```



## **Create and Attach the S3RestrictedPolicy IAM Policy**

This guide provides instructions to create an IAM policy named `S3RestrictedPolicy` that restricts access to specific S3 buckets (`poridhiprod1` and `poridhiprod2`). The policy will then be attached to an IAM user (`User1`).



### **Steps to Create and Attach the S3RestrictedPolicy**

1. **Navigate to S3 and Review Buckets**  
   - Go to the [S3 Console](https://s3.console.aws.amazon.com/).
   - Review the four provisioned buckets:
     - `poridhiprod1`
     - `poridhiprod2`
     - `poridhistageconfig3`
     - `poridhistageconfig4`

2. **Open IAM in a New Tab**  
   - In the top search bar, search for **IAM**.
   - Right-click on IAM and open it in a new tab.

3. **Review IAM Users**  
   - In the IAM console, under **Access Management**, click **Users**.
   - Ensure `User1` exists.

4. **Create the S3RestrictedPolicy**  
   - In the IAM console, under **Access Management**, click **Policies**.
   - Click **Create Policy**.
   - Under **Select a service**, click **S3**.
   - Under **Actions allowed**, select **All S3 actions**.
   - Under **Resources**, configure the following:

![policy](https://s3.brilliant.com.bd/blog-bucket/thumbnail/992780b2-f356-4f06-846c-4cb8444e502c.png)

   - For **bucket**:
       - Uncheck **Any in this account**.
       - Click **Add ARNs**.
       - Copy the bucket name for `poridhiprod1` from the S3 console and paste it into the **Resource bucket name** field.
       - Click **Add ARNs**.

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/bb3b7e73-f948-4296-bbab-582f325969bb.png)

  - Repeat the process for `poridhiprod2`.
  - For **object**:
     - Select the **Any** checkbox.
     - Click **Next**.



5. **Name and Create the Policy**  
   - On the **Review and create** page, enter `S3RestrictedPolicy` as the policy name.
   - Click **Create policy**.

6. **Attach the Policy to `User1`**  
   - In the `S3RestrictedPolicy` policy details, click the **Entities attached** tab.
   - Under **Attached as a permissions policy**, click **Attach**.
   - Select the checkbox next to `User1`.
   - Click **Attach policy**.



## **Create the IAM Role and Allow `User2` to Assume It**

This guide provides instructions to create an IAM role named `S3RestrictedRole`, attach the `S3RestrictedPolicy` to it, and configure the role's trust relationship to allow `User2` to assume it.



### **Steps to Create the IAM Role**

1. **Navigate to IAM Roles**  
   - Go to the [IAM Console](https://console.aws.amazon.com/iam/).
   - In the left navigation menu, click **Roles**.

2. **Create the Role**  
   - Click **Create role**.
   - Under **Trusted entity type**, select **AWS account**.
   - Under **An AWS account**, select **This account**.
   - Copy the account ID displayed in parentheses and save it to a text file for later use.
   - Click **Next**.

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/d285de8d-6311-48ca-87a0-e0a4766bc6d9.png)

3. **Attach the S3RestrictedPolicy**  
   - Use the search bar to look for the `S3RestrictedPolicy`.
   - Click the checkbox next to the `S3RestrictedPolicy`.
   - Click **Next**.

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/561ecd7d-4e6f-4f7f-b88a-4c0b23273ccb.png)

4. **Name and Create the Role**  
   - In the **Role name** field, enter `S3RestrictedRole`.
   - Review the trusted entity (your account number) to confirm that any entity in this account can assume this role.
   - Click **Create role**.



### **Steps to Allow `User2` to Assume the Role**

1. **Copy `User2` ARN**  
   - In the IAM console, click **Users** in the left navigation menu.
   - Click on `User2`.
   - Under the **Summary** section, copy the **ARN** of `User2`.

2. **Modify the Trust Relationship**  
   - In the IAM console, click **Roles** in the left navigation menu.
   - In the search bar, enter `S3` and select the `S3RestrictedRole`.
   - Click the **Trust relationships** tab.
   - Click **Edit trust policy**.
   - In line 7 of the trust policy, delete the existing ARN and paste the ARN you copied for `User2`. Ensure the ARN is enclosed in quotation marks.
   - Click **Update policy**.

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/0f8a5386-a9e3-4a91-8c8f-396da6bf6b5f.png)



## **Test IAM Policy and Role Configuration**

This guide provides instructions to test the IAM policy and role configuration for `User1` and `User2`. It verifies that:
- `User1` has access only to the `poridhiprod1` and `poridhiprod2` buckets.
- `User2` can assume the `S3RestrictedRole` and access the `poridhiprod1` and `poridhiprod2` buckets.



### **Steps to Test `User1` Configuration**

1. **Log in as `User1`**  
   - Navigate to the [AWS Management Console](https://aws.amazon.com/console/).
   - Sign in using the credentials for `User1`.

2. **Verify S3 Access**  
   - Navigate to the **S3** service.
   - Attempt to access `poridhistageconfig3` or `poridhistageconfig4`. You should see an **Access Denied** message.
   - Access `poridhiprod1` and `poridhiprod2`. You should have full access.



### **Steps to Test `User2` Configuration**

1. **Log in as `User2`**  
   - Sign out of the AWS Management Console.
   - Log back in using the credentials for `User2`.

2. **Verify S3 Access**  
   - Navigate to the **S3** service.
   - Attempt to access any of the buckets. You should see an **Access Denied** message for all buckets.

3. **Assume the `S3RestrictedRole`**  
   - In the upper right corner, copy the **Account ID** to your clipboard.
   - Click **Switch role**.
   - For **Account**, paste the account ID you copied.
   - For **Role**, enter `S3RestrictedRole` (ensure it is spelled correctly).
   - Select a color of your choice and click **Switch Role**.

4. **Verify S3 Access with the Role**  
   - In the **S3** console, confirm that you can now see the `poridhiprod1` and `poridhiprod2` buckets.
   - Attempt to access `poridhistageconfig3` or `poridhistageconfig4`. You should see an **Access Denied** message.



## **Notes**
- Ensure the bucket names and ARNs are correctly specified in the policies and roles.
- Always test the configuration to verify that access restrictions are working as intended.


