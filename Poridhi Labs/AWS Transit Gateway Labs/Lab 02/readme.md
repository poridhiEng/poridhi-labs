# Connect Multiple VPCs with Transit Gateway 

In this guide, we will connect two VPCs using an AWS Transit Gateway and configure route tables to establish private connectivity. This setup ensures that communication between VPCs flows through your private network without traversing the public internet, which is crucial for secure and efficient production environments.

![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/dbb6fdc7-9396-4756-800e-c916d595a525.png)

## **Objectives**
1. Create VPCs.
2. Create a Transit Gateway.
3. Attach the Transit Gateway to both VPCs.
4. Edit Route Tables for proper routing.

## **What is a Transit Gateway?**

AWS Transit Gateway is a **networking service** that connects thousands of Amazon VPCs and on-premises networks using a **single gateway**. It uses a **hub-and-spoke model** to route all traffic between VPCs or VPNs, providing a centralized point for managing and monitoring your network.

In simpler terms, AWS Transit Gateway acts as a **central hub** that connects your Amazon Virtual Private Clouds (VPCs) and on-premises networks. It simplifies your network architecture by eliminating complex peering relationships and functions as a **cloud router**, establishing connections efficiently.

## **Step 1: Create VPCs**

1. Navigate to the **AWS Management Console**.
2. Go to **VPC > Your VPCs**.
3. Click **Create VPC** and configure as follows:

   - **VPC-A**:
     - **Name Tag**: `VPC-A`
     - **IPv4 CIDR Block**: `10.0.0.0/16`

   - **VPC-B**:
     - **Name Tag**: `VPC-B`
     - **IPv4 CIDR Block**: `172.32.0.0/16`

   ![vpc](https://s3.brilliant.com.bd/blog-bucket/thumbnail/fde668c7-e0ec-44ca-9ae1-98e255c923ed.png)

## **Step 2: Create Subnets**

1. Navigate to **Subnets** and click **Create Subnet**.
2. Create the following subnets:

   - **VPC-A**:
     - **Subnet Name**: `Public-Subnet-A`
     - **VPC**: `VPC-A`
     - **CIDR Block**: `10.0.1.0/24`

   - **VPC-B**:
     - **Subnet Name**: `Private-Subnet-B`
     - **VPC**: `VPC-B`
     - **CIDR Block**: `172.32.1.0/24`

   ![subnet](https://s3.brilliant.com.bd/blog-bucket/thumbnail/8db23e25-4251-4290-927c-d96a93e1285d.png)

3. **Attach an Internet Gateway to VPC-A** for public internet access:
   - Navigate to **Internet Gateways** and click **Create Internet Gateway**.
   - Name it `IGW-1` and attach it to `VPC-A`.

   ![igw](https://s3.brilliant.com.bd/blog-bucket/thumbnail/3178f588-1fc1-449c-ab63-4b9bd82627e2.png)

## **Step 3: Create Route Tables**

1. **VPC-A**:
   - **Public Subnet (10.0.1.0/24)**:
     - **Route Table-1**:
       - `0.0.0.0/0` → Internet Gateway (IGW-1)

2. **VPC-B**:
   - **Private Subnet (172.32.1.0/24)**:
     - **Route Table-2**:
       - `Local route` → VPC-B

   ![routetable](https://s3.brilliant.com.bd/blog-bucket/thumbnail/c3ee76fc-9059-49db-94ad-07eab5e91959.png)

## **Step 4: Create a Transit Gateway**

1. Go to the **AWS Management Console**.
2. Navigate to **VPC > Transit Gateways**.
3. Click **Create Transit Gateway**.
4. Configure the following:

   - **Name Tag**: `Transit-Gateway01`
   - **Description**: (Optional)
   - **Amazon Side ASN**: Leave as default or specify a private ASN.
   - **DNS Support**: Enable.
   - **VPN ECMP Support**: Enable.
   - **Default Route Table Association**: Enable.
   - **Default Route Table Propagation**: Enable.
   - **Auto Accept Shared Attachments**: Disable (unless using Resource Access Manager).

5. Click **Create Transit Gateway**.

   ![Create Transit Gateway](https://s3.brilliant.com.bd/blog-bucket/thumbnail/a5b5da42-2419-48a2-b3e9-345f50a646d7.png)

## **Step 5: Attach Transit Gateway to Each VPC**

1. Navigate to **VPC > Transit Gateway Attachments**.
2. Click **Create Transit Gateway Attachment**.
3. Configure the attachment for each VPC as follows:

   - **VPC-A**:
     - **Name**: `VPC-A-TGW-Att`
     - **Transit Gateway ID**: `Transit-Gateway01`
     - **Attachment Type**: `VPC`
     - **VPC ID**: `VPC-A`
     - **Subnet ID**: `Public-Subnet-A`

     ![transit gateway](https://s3.brilliant.com.bd/blog-bucket/thumbnail/98fccb47-a316-4ade-b933-8f20230a371e.png)

   - **VPC-B**:
     - **Name**: `VPC-B-TGW-Att`
     - **Transit Gateway ID**: `Transit-Gateway01`
     - **Attachment Type**: `VPC`
     - **VPC ID**: `VPC-B`
     - **Subnet ID**: `Private-Subnet-B`

## **Step 6: Edit Route Tables**

1. **For VPC-A**:
   - Navigate to **Route Tables** and select the route table associated with `Public-Subnet-A`.
   - Click **Edit Routes**.
   - Add a new route:
     - **Destination**: `172.32.0.0/16` (VPC-B's CIDR block)
     - **Target**: Select the Transit Gateway (`Transit-Gateway01`).
   - Click **Save Changes**.

   ![public-rt](https://s3.brilliant.com.bd/blog-bucket/thumbnail/7f7ebb74-5d52-46a4-852d-f6d53f1964c5.png)

2. **For VPC-B**:
   - Navigate to **Route Tables** and select the route table associated with `Private-Subnet-B`.
   - Click **Edit Routes**.
   - Add a new route:
     - **Destination**: `10.0.0.0/16` (VPC-A's CIDR block)
     - **Target**: Select the Transit Gateway (`Transit-Gateway01`).
   - Click **Save Changes**.

   ![rt](https://s3.brilliant.com.bd/blog-bucket/thumbnail/62c44090-e5c6-4cc1-8197-e222d2f44d1a.png)

## **Verification**

1. **Ping Test**:
   - Launch an EC2 instance in `Public-Subnet-A` and another in `Private-Subnet-B`.
   - Ensure that security groups allow ICMP traffic.
   - From the instance in `Public-Subnet-A`, try to ping the private IP of the instance in `Private-Subnet-B`.

2. **Traceroute**:
   - Use `traceroute` to verify that traffic is routed through the Transit Gateway.


By following this guide, you can securely and efficiently connect multiple VPCs using AWS Transit Gateway, ensuring a robust and scalable network architecture for your production environment.