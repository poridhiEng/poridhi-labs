# **Configuring AWS Transit Gateway: A Step-by-Step Guide**

In this lab, we will create an **AWS Transit Gateway** and connect **three VPCs** to enable seamless communication between them. By the end of this guide, you will have a fully functional Transit Gateway setup, allowing EC2 instances in different VPCs to communicate with each other.

---
![image](./images/transit-gw.drawio%20(4).svg)

## **Objectives**

1. Create a **Transit Gateway Subnet** in each VPC using a `/28` address space.
2. Create and attach a **Transit Gateway** to the new subnet in each VPC.
3. Modify **Route Tables** in each VPC to enable routing through the Transit Gateway.
4. Confirm connectivity by performing a **ping test** between EC2 instances in different VPCs.

---

## **What is AWS Transit Gateway?**

AWS Transit Gateway is a **networking service** that connects thousands of Amazon VPCs and on-premises networks using a **single gateway**. It uses a **hub-and-spoke model** to route all traffic between VPCs or VPNs, providing a centralized point for managing and monitoring your network. 

In simpler terms, AWS Transit Gateway acts as a **central hub** that connects your Amazon Virtual Private Clouds (VPCs) and on-premises networks. It simplifies your network architecture by eliminating complex peering relationships and functions as a **cloud router**, establishing connections efficiently.

---

## **How AWS Transit Gateway Works**

Think of AWS Transit Gateway as the **central station** in a city’s transportation system. Just as you’d use a central station to travel across the city, Transit Gateway allows you to connect all parts of your network (VPCs, on-premises networks, etc.) in a similar manner.

Instead of creating separate connections between each network (which can quickly become complex), you connect all networks to the Transit Gateway. When data needs to move from one network to another, it passes through the Transit Gateway, making your network architecture **easier to manage and monitor**. Essentially, it acts as the **central hub** for your data traffic.

---

## **Prerequisites**

Before starting, ensure you have the following:

1. **VPCs**: Create three VPCs with non-overlapping CIDR blocks:
   - **VPC-A**: `10.0.0.0/16`
   - **VPC-B**: `10.1.0.0/16`
   - **VPC-C**: `10.2.0.0/16`

2. **Subnets**:
   - Create **one public subnet** for a bastion server and **two private subnets** for EC2 instances in each VPC.

3. **EC2 Instances**:
   - Launch EC2 instances in the private subnets of each VPC to test connectivity.

4. **Route Tables**:
   - Create **three route tables** for the EC2 instances as follows:

---

### **VPC and Subnet Configuration**

Here’s how the setup will look:

1. **VPC-A**  
   - **Public Subnet (10.0.1.0/24)**: Contains the **Bastion Server**.  
   - **Route Table-1**:  
     - `0.0.0.0/0` → Internet Gateway (IGW-1)  

2. **VPC-B**  
   - **Private Subnet (10.1.1.0/24)**: Contains **EC2-B**.  
   - **Route Table-2**:  
     - `Local route` → VPC-B  

3. **VPC-C**  
   - **Private Subnet (10.2.1.0/24)**: Contains **EC2-C**.  
   - **Route Table-3**:  
     - `Local route` → VPC-C  

---

## **Step 1: Create Transit Gateway Subnets in Each VPC**

Create a `/28` subnet in each VPC for the Transit Gateway attachment:

1. **VPC-A**:
   - **Subnet Name**: `VPC-A-TransitGateway`
   - **Availability Zone**: `ap-southeast-1a`
   - **IPv4 CIDR Block**: `10.0.2.0/28`

2. **VPC-B**:
   - **Subnet Name**: `VPC-B-TransitGateway`
   - **Availability Zone**: `ap-southeast-1a`
   - **IPv4 CIDR Block**: `10.1.2.0/28`

3. **VPC-C**:
   - **Subnet Name**: `VPC-C-TransitGateway`
   - **Availability Zone**: `ap-southeast-1a`
   - **IPv4 CIDR Block**: `10.2.2.0/28`

---

## **Step 2: Create a Transit Gateway**

1. Go to the **AWS Management Console**.
2. Navigate to **VPC > Transit Gateways**.
3. Click **Create Transit Gateway**.
4. Configure the following:

   ![Create Transit Gateway](https://s3.brilliant.com.bd/blog-bucket/thumbnail/a5b5da42-2419-48a2-b3e9-345f50a646d7.png)

   - **Name Tag**: `Transit-Gateway01`
   - **Description**: (Optional)
   - **Amazon Side ASN**: Leave as default or specify a private ASN.
   - **DNS Support**: Enable.
   - **VPN ECMP Support**: Enable.
   - **Default Route Table Association**: Enable.
   - **Default Route Table Propagation**: Enable.
   - **Auto Accept Shared Attachments**: Disable (unless using Resource Access Manager).

5. Click **Create Transit Gateway**.

---

## **Step 3: Attach Transit Gateway to Each VPC**

1. Navigate to **VPC > Transit Gateway Attachments**.
2. Click **Create Transit Gateway Attachment**.
3. Configure the attachment for each VPC as follows:

   ![Create Transit Gateway Attachment](https://s3.brilliant.com.bd/blog-bucket/thumbnail/8fdae5d5-806f-40a7-8a2f-8b412c3c8051.png)

   - **VPC-A**:
     - **Name**: `VPC-A-TGW-Att`
     - **Transit Gateway ID**: `Transit-Gateway01`
     - **Attachment Type**: `VPC`
     - **VPC ID**: `VPC-A`
     - **Subnet ID**: `VPC-A-TransitGateway`

   - **VPC-B**:
     - **Name**: `VPC-B-TGW-Att`
     - **Transit Gateway ID**: `Transit-Gateway01`
     - **Attachment Type**: `VPC`
     - **VPC ID**: `VPC-B`
     - **Subnet ID**: `VPC-B-TransitGateway`

   - **VPC-C**:
     - **Name**: `VPC-C-TGW-Att`
     - **Transit Gateway ID**: `Transit-Gateway01`
     - **Attachment Type**: `VPC`
     - **VPC ID**: `VPC-C`
     - **Subnet ID**: `VPC-C-TransitGateway`

4. Verify the attachments in the **Transit Gateway Route Table Associations** tab.

   ![Transit Gateway Route Table Associations](https://s3.brilliant.com.bd/blog-bucket/thumbnail/97220623-2e69-4dfe-806b-fe23548d4669.png)

---

## **Step 4: Modify Route Tables in Each VPC**

Update the route tables in each VPC to route traffic through the Transit Gateway:

1. **VPC-A**:
   - **Public Route Table-A**:
     - `0.0.0.0/0` → Internet Gateway (IGW-1)
     - `10.1.0.0/16` → Transit Gateway (`tgw-0`)
     - `10.2.0.0/16` → Transit Gateway (`tgw-0`)

2. **VPC-B**:
   - **Private Route Table-B**:
     - `Local route` → VPC-B
     - `10.0.0.0/16` → Transit Gateway (`tgw-0`)
     - `10.2.0.0/16` → Transit Gateway (`tgw-0`)

3. **VPC-C**:
   - **Private Route Table-C**:
     - `Local route` → VPC-C
     - `10.0.0.0/16` → Transit Gateway (`tgw-0`)
     - `10.1.0.0/16` → Transit Gateway (`tgw-0`)

   ![Modify Route Table](https://s3.brilliant.com.bd/blog-bucket/thumbnail/ab7f46b5-051e-4fbc-ba8e-919f400deb09.png)

---

## **Step 5: Confirm Connectivity with Ping Test**

1. **SSH into the Bastion Server**:
   - Use the following command to SSH into the bastion server from your local machine:
     ```bash
     ssh -i "key.pem" ubuntu@<public-ip>
     ```

2. **Ping EC2 Instances**:
   - From the bastion server, ping the private IP addresses of the EC2 instances in **VPC-B** and **VPC-C**:
     ```bash
     ping <Private-IP-of-EC2-B>
     ping <Private-IP-of-EC2-C>
     ```

3. **Troubleshooting**:
   - If the ping test fails, ensure that:
     - The **security groups** for the EC2 instances allow inbound ICMP (ping) traffic from the CIDR blocks of the other VPCs.

       ![image](https://s3.brilliant.com.bd/blog-bucket/thumbnail/fee71a69-952f-4e07-a89f-52c0ab101693.png)

     - The **route tables** are correctly configured to route traffic through the Transit Gateway.

   ![Ping Test](https://s3.brilliant.com.bd/blog-bucket/thumbnail/762dc564-2864-4bda-90ea-0b7212059910.png)

---

## **Conclusion**

By following this guide, you’ve successfully configured an **AWS Transit Gateway** to connect three VPCs and enabled communication between them. This setup simplifies network management and provides a scalable solution for multi-VPC architectures. 

