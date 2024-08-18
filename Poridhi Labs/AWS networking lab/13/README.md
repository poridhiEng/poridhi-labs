# AWS VPC Peering Lab

In this lab, we will explore the process of setting up VPC peering in AWS, allowing seamless communication between two VPCs as if they were in the same network. VPC Peering is a vital networking capability that provides a secure and private connection between VPCs. 

![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image.png?raw=true)

This hands-on guide will walk you through the steps of creating two custom VPCs, setting up subnets, configuring route tables, and establishing a peering connection. By the end of this lab, you will have a solid understanding of VPC peering and its practical applications.

## VPC Peering

### What is VPC Peering?

Amazon Virtual Private Cloud (VPC) Peering is a networking service from Amazon Web Services (AWS) that lets you connect two VPCs, allowing them to communicate as if they were in the same network. VPC Peering provides a secure and private connection without needing a Virtual Private Network (VPN) or an internet gateway.


## Step 1: Create Two Custom VPCs with Subnets in the Same AWS Region (ap-southeast-1)

### Create the First Custom VPC

1. Navigate to the VPC console.
2. In the left-hand menu, select "Your VPCs", then click on "Create VPC".

    **Note**: Do not use the VPC Wizard to create your VPC; instead, configure your VPC from scratch and use the "VPC Only" option.

3. Create the first VPC with the following values:
    - **Name**: `App-VPC`
    - **CIDR block**: `10.0.0.0/16`
    - **Tenancy**: Default
    - **IPv6 CIDR Block**: Select "No IPv6 CIDR Block"

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-1.png?raw=true)

### Create a Public Subnet for App-VPC

1. In the left-hand menu, click on "Subnets", then click "Create subnet".
2. Select the VPC ID of `App-VPC`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-2.png?raw=true)

3. Configure the subnet with the following values:
    - **Name**: `App-Public-Subnet`
    - **Availability Zone**: `<ap-southeast-1a>`
    - **CIDR block**: `10.0.0 .0/24`

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-3.png?raw=true)

4. Click "Create" and make the subnet public by modifying the auto-assign IP settings.
    - From the Subnets page, select the subnet.
    - In the top right-hand corner of the page, click "Actions" > "Edit subnet settings".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-4.png?raw=true)

    - On the Edit subnet settings page, under "Auto-assign IP settings", check the box next to "Enable auto-assign public IPv4 address".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-5.png?raw=true)

### Create the Second Custom VPC

1. Create the second VPC with the following values:
    - **Name**: `DB-VPC`
    - **CIDR block**: `10.1.0.0/16`
    - **Tenancy**: Default
    - **IPv6 CIDR Block**: Select "No IPv6 CIDR Block"

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-6.png?raw=true)

### Create a Private Subnet for DB-VPC

1. In the left-hand menu, click on "Subnets", then click "Create subnet".
2. Select the VPC ID of `DB-VPC`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-7.png?raw=true)

3. Configure the subnet with the following values:
    - **Name**: `DB-Private-Subnet`
    - **Availability Zone**: `<ap-southeast-1a>`
    - **CIDR block**: `10.1.0.0/24`

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-8.png?raw=true)

## Step 2: Create and Attach an Internet Gateway for APP-VPC

1. From the Subnets page, select "Internet gateways" in the left-hand menu.
2. Click "Create internet gateway".
3. Name it `App-IGW` and click "Create internet gateway".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-9.png?raw=true)

4. Attach the Internet Gateway to APP-VPC:
    - Select the newly created Internet Gateway.
    - Click on "Actions" > "Attach to VPC".
    - Choose `App-VPC` and click "Attach Internet Gateway".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-10.png?raw=true)

## Step 3: Create and Configure Route Tables

### Create a Route Table for the Public Subnet in APP-VPC

1. In the VPC console, select "Route Tables" from the left-hand menu.
2. Click "Create route table".
3. Name it `public-RT` and select `App-VPC`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-11.png?raw=true)

4. Add a route to the Internet Gateway:
    - On the Routes tab, click "Edit routes".
    - Add a route with the destination `0.0.0.0/0` and target `App-IGW`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-12.png?raw=true)

### Associate the Route Table with the Public Subnet

1. From the route table’s page, click the "Subnet associations" tab.
2. Click "Edit subnet associations".
3. Select `App-Public-Subnet` and click "Save".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-13.png?raw=true)

### Create a Route Table for the Private Subnet in DB-VPC

1. Create a route table named `private-RT` under `DB-VPC`.

     ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-14.png?raw=true)

2. Associate it with `db-vpc-priv-subnet`.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-15.png?raw=true)

3. No need to edit routes at this point.

## Step 4: Launch EC2 Instances

### Launch an EC2 Instance in APP-VPC

1. Launch an EC2 instance:

    - Name: `App-instance`
    - Select `Ubuntu` AMI.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-16.png?raw=true)

    - Generate a key-pair. In our case, we named it `key`.
    - Save it in the local machine.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-17.png?raw=true)


2. Follow the following network settings:
    - **VPC**: `App-VPC`
    - **Subnet**: `App-Public-Subnet`
    - **Auto-assign Public IP**: Enabled

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-18.png?raw=true)

### Launch an EC2 Instance in DB-VPC

1. Launch another EC2 instance: 

    - **Name**: `DB-instance`
    - Select `Ubuntu` AMI.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-19.png?raw=true)

    - Select the previously generated key-pair:

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-20.png?raw=true)

    

2. Follow the following network settings:
    - **VPC**: `DB_VPC`
    - **Subnet**: `DB-Private-Subnet`
    - **Auto-assign Public IP**: Disabled
    - Setup Inbound security group rules according to the following image.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-21.png?raw=true)

## Step 5: Test SSH Access Between Instances

1. Open terminal. Go to the directory where you saved the key-pair file (key.pem).
2. Copy the key-pair of the DB instance to the `App-VPC` instance using the following command:
    ```bash
    scp -i key.pem key.pem ubuntu@<App-instance-public-IP>:/home/ubuntu/
    ```

3. SSH into the EC2 instance in `App-VPC` using the following command:
    ```bash
    ssh -i key.pem ubuntu@<App-instance-public-IP>
    ```
4. Go to `/home/ubuntu` directory and provide necessary permission for key.pem file in the instance using:
    ```bash
    chmod 400 key.pem
    ```

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-22.png?raw=true)



5. Attempt to SSH into the `DB-VPC` EC2 instance `DB-instance` using its `private IP` address from the `App-VPC` instance. You should not be able to SSH or ping the DB server at this point because two VPCs cannot communicate with each other without a VPC Peering Connection.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-23.png?raw=true)

    It doesn't work as expected.

## Step 6: Create a VPC Peering Connection

1. Go to VPC > Peering Connections from the VPC dashboard in the left-hand menu.
2. Click "Create Peering Connection".

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-24.png?raw=true)

3. Configure the peering connection with the following parameters:
    - **Peering connection name tag**: `my-peering-connection`
    - **VPC (Requester)**: `App-VPC`
    - **VPC (Accepter)**: `DB-VPC`
    - **Select My Account and the Same Region**

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-25.png?raw=true)

4. Click "Create peering connection".

### Accept the Peering Connection

1. The status of the connection will be “Pending Acceptance”.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-26.png?raw=true)

2. Select the peering connection, then click "Actions" > "Accept Request". Now it is active.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-27.png?raw=true)

## Step 7: Update Route Tables

### Add Routes to the App-VPC Route Table

1. Select the `public-RT` route table.
2. Click "Edit routes".
3. Add a route with the following entry:
    - **Destination**: `10.1.0.0/16`
    - **Target**: Select the Peering Connection

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-28.png?raw=true)

### Add Routes to the DB-VPC Route Table

1. Select the `private-RT` route table.
2. Click "Edit routes".
3. Add a route with the following entry:
    - **Destination**: `10.0.0.0/16`
    - **Target**: Select the Peering Connection

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-29.png?raw=true)

## Step 8: Verify the Peering Connection

1. SSH into the EC2 instance in `App-VPC` using the following command:
    ```bash
    ssh -i key.pem ubuntu@<App-instance-public-ip>
    ```

2. Try to SSH into the EC2 instance in `DB-VPC` using its private IP address.

    ![alt text](https://github.com/Konami33/poridhi.io.intern/blob/main/AWS%20networking%20lab/Lab%2013/images/image-30.png?raw=true)

3. If successful, the VPC peering has been set up correctly.

By following these detailed steps, you will have successfully set up VPC peering between two VPCs, enabling secure communication between them.