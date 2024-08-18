# Building a Three-Tier Network VPC from Scratch in AWS

The goal of setting up a three-tier AWS network Virtual Private Cloud (VPC) is to create an environment that can scale to meet the needs of the application while maintaining high levels of security, uptime, and performance. The three tiers typically include:

1. **Presentation Tier (Web Tier)**: The user interface and access point for the application, which may include web servers, load balancers, and content delivery networks (CDNs).
2. **Application Tier (Middle Tier)**: Where the application code resides, potentially including application servers and APIs.
3. **Data Tier (Back-End Tier)**: Where data is stored and processed, including databases and data warehouses.

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-32.png?raw=true)

In this guide, you will set up a three-tier VPC in AWS, create subnets in different availability zones, and configure necessary routing and internet access.




## Prerequisites

1. Log in to the live AWS environment using the lab account.
2. Ensure you are in the `Singapore (ap-southeast-1)` region.

## Step 1: Create the VPC

### Open the VPC Dashboard
1. In the AWS Management Console, search for "VPC" and select it from the "Services" dropdown.
2. In the VPC dashboard, select "VPCs" and click "Create VPC".

### Configure the VPC
1. **Name**: Enter a name for the VPC (e.g., `poridhi`).
2. **IPv4 CIDR Block**: Choose "IPv4 CIDR manual input" and enter `10.0.0.0/16`.
3. Leave other settings as default.
4. Click `Create VPC`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image.png?raw=true)

### Enable DNS Hostnames
1. Select the newly created VPC.
2. Click on **Actions** > **Edit VPC settings**.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-1.png?raw=true)

3. Check the box to enable DNS Hostnames.
4. Click "Save Changes".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-2.png?raw=true)



## Step 2: Create and Attach an Internet Gateway

### Create the Internet Gateway
1. In the VPC dashboard, select "Internet Gateways" from the left-hand menu.
2. Click "Create Internet Gateway".
3. **Name**: Enter a name (e.g., `poridhi-IGW`).
4. Click "Create Internet Gateway".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-3.png?raw=true)

### Attach the Internet Gateway to the VPC
1. Select the newly created Internet Gateway.
2. Click on **Actions** > **Attach to VPC**.
3. Choose the VPC (e.g., `poridhi`) and click "Attach Internet Gateway".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-4.png?raw=true)

## Step 3: Create Public Subnets



### Create the First Public Subnet
1. Select "Subnets" from the VPC dashboard menu.
2. Click "Create Subnet".
3. **VPC**: Select "Poridhi VPC".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-5.png?raw=true)

4. **Name**: Enter `Public-subnet-AZ1`.
5. **Availability Zone**: Choose `ap-southeast-1a`.
6. **IPv4 CIDR Block**: Enter `10.0.0.0/24`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-6.png?raw=true)

### Create the Second Public Subnet

1. Click on "Add new subnet" and repeat the above steps. 
2. **Name**: `Public-subnet-AZ2`.
3. **Availability Zone**: Choose `ap-southeast-1b`.
4. **IPv4 CIDR Block**: Enter `10.0.1.0/24`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-7.png?raw=true)

    

### Enable Auto-Assign Public IP
For `both` public subnets:
- Select the subnet.
- Click on **Actions** > **Edit Subnet settings**.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-8.png?raw=true)

- Check the box to enable auto-assign public IPv4 addresses.
- Click "Save Changes".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-9.png?raw=true)

Here we showed the steps for the first subnet, repeat the steps for `public-subnet-AZ2`.

## Step 4: Create and Configure Route Table for Public Subnets

### Create the Public Route Table
1. In the VPC dashboard, select "Route Tables" from the left-hand menu.
2. Click "Create route table".
3. **Name**: Enter `public-RT`.
4. **VPC**: Select `poridhi`.
5. Click "Create Route Table".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-10.png?raw=true)

### Add Route to Internet Gateway
1. Select the Public Route Table.
2. Go to the "Routes" tab and click "Edit routes".
3. Click "Add route".
   - **Destination**: `0.0.0.0/0`.
   - **Target**: Select the Internet Gateway (e.g., `poridhi-IGW`).
4. Click "Save changes".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-11.png?raw=true)

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-12.png?raw=true)

### Associate Route Table with Public Subnets
1. Select the Public Route Table.
2. Go to the **Subnet associations** tab and click **Edit subnet associations**.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-13.png?raw=true)
    
3. Select both `public-subnet-AZ1` and `public-subnet-AZ2`.
4. Click "Save associations".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-14.png?raw=true)

    

## Step 5: Create Private Subnets

### Create the First Private Subnet
1. In the VPC dashboard, select "Subnets" from the left-hand menu.
2. Click "Create Subnet".
3. **VPC**: Select `Poridhi`.

#### Private Subnets 1

- **Name**: Enter `Private-app-subnet-AZ1`.
- **Availability Zone**: Choose `ap-southeast-1a`.
- **IPv4 CIDR Block**: Enter `10.0.2.0/24`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-15.png?raw=true)

### Create Additional Private Subnets

#### Private Subnets 2

- **Name**: Enter `Private-app-subnet-AZ2`.
- **Availability Zone**: Choose `ap-southeast-1b`.
- **IPv4 CIDR Block**: Enter `10.0.3.0/24`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-16.png?raw=true)

#### Private Subnets 3

- **Name**: Enter `Private-data-subnet-AZ1`.
- **Availability Zone**: Choose `ap-southeast-1a`.
- **IPv4 CIDR Block**: Enter `10.0.4.0/24`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-17.png?raw=true)

#### Private Subnets 4

- **Name**: Enter `Private-data-subnet-AZ2`.
- **Availability Zone**: Choose `ap-southeast-1b`.
- **IPv4 CIDR Block**: Enter `10.0.5.0/24`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-18.png?raw=true)


Finally, we can see the private subnets that were created:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-19.png?raw=true)


## Step 6: Create and Configure NAT Gateways

### Create the First NAT Gateway
1. In the VPC dashboard, select "NAT Gateways" from the left-hand menu.
2. Click "Create NAT Gateway".
3. **Name**: Enter `NAT-GW-AZ1`.
4. **Subnet**: Select `Public-subnet-AZ1`.
5. **Elastic IP Allocation ID**: Click `Allocate Elastic IP` and allocate an Elastic IP.
6. Click "Create NAT Gateway".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-20.png?raw=true)

### Create the Second NAT Gateway
Repeat the above steps with the following changes:

- Name: Enter `NAT-GW-AZ2`.
- Subnet: Select `Public-subnet-AZ2`.
- Elastic IP Allocation ID: Click `Allocate Elastic IP` and allocate an Elastic IP.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-21.png?raw=true)

## Step 7: Create and Configure Route Tables for Private Subnets

### Create and configure the first private route table
1. In the VPC dashboard, select "Route Tables" from the left-hand menu.
2. Click "Create route table".
3. **Name**: Enter `Private-RT-AZ1`.
4. **VPC**: Select `poridhi`.
5. Click "Create Route Table".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-22.png?raw=true)

#### Add Route to NAT Gateway
1. Select the `Private-RT-AZ1`.
2. Go to the "Routes" tab and click "Edit routes".
3. Click "Add route".
   - **Destination**: `0.0.0.0/0`.
   - **Target**: Select `NAT-GW-AZ1`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-23.png?raw=true)
   
4. Click "Save changes".

#### Associate Route Table with Private Subnets
1. Select the `Private-RT-AZ1`.
2. Go to the "Subnet associations" tab and click "Edit subnet associations".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-25.png?raw=true)

3. Select `Private-app-subnet-AZ1` and `Private-data-subnet-AZ1`.
4. Click "Save associations".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-24.png?raw=true)



### Create and configure the second private route table
1. In the VPC dashboard, select "Route Tables" from the left-hand menu.
2. Click "Create route table".
3. **Name**: Enter `Private-RT-AZ2`.
4. **VPC**: Select `poridhi`.
5. Click "Create Route Table".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-26.png?raw=true)

#### Add Route to NAT Gateway
1. Select the `Private-RT-AZ2`.
2. Go to the "Routes" tab and click "Edit routes".
3. Click "Add route".
   - **Destination**: `0.0.0.0/0`.
   - **Target**: Select `NAT-GW-AZ2`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-27.png?raw=true)
   
4. Click "Save changes".

#### Associate Route Table with Private Subnets
1. Select the `Private-RT-AZ2`.
2. Go to the "Subnet associations" tab and click "Edit subnet associations".
3. Select `Private-app-subnet-AZ2` and `Private-data-subnet-AZ2`.
4. Click "Save associations".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-28.png?raw=true)


We can see these subnet associations in the `subnet-associations` tab of Route table:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-29.png?raw=true)


## Conclusion
By following these detailed steps, you will have successfully set up a three-tier network VPC from scratch in AWS, ensuring high availability and secure internet access for your application.

Here is the final `Resource Map` of our VPC `poridhi`:

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2012/images/image-30.png?raw=true)