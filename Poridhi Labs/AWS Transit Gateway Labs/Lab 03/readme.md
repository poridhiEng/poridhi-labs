# Optimizing Internet Access Costs with AWS Transit Gateway: A Practical Guide

## Introduction

When managing multiple VPCs in AWS, providing internet access to private subnets traditionally requires deploying NAT Gateways in each VPC. While this approach offers simplicity and independence, it can lead to significant costs as your infrastructure grows. This guide demonstrates how to optimize costs by centralizing internet access using AWS Transit Gateway.

## Prerequisites

Before starting this lab, you should have:
- An AWS account with administrative access
- Basic understanding of AWS VPC concepts
- Familiarity with AWS networking components

## Architecture Overview

![image](./images/tr-connect.drawio%20(2).svg)

In this lab, we'll create:
- Two VPCs: A WorkloadVPC for your applications and an EgressVPC for centralized internet access
- A Transit Gateway to connect the VPCs
- A NAT Gateway in the EgressVPC to handle internet traffic
- Appropriate subnets and routing tables to enable communication

![Architecture Overview showing Internet Gateway configuration](https://s3.brilliant.com.bd/blog-bucket/thumbnail/b61f3a31-0f43-490d-a05b-2acf3cdd4ad0.png)
*Figure 1: Architecture diagram showing the Internet Gateway attached to EgressVPC*

## Step-by-Step Implementation

### 1. Creating VPCs and Subnets

First, navigate to the VPC dashboard in the AWS console and create two VPCs:

**WorkloadVPC Configuration:**
- CIDR: 10.0.0.0/16
- Subnets:
  - WorkloadTransitSubnet (10.0.1.0/24)
  - WorkloadPrivateSubnet (10.0.2.0/24)

**EgressVPC Configuration:**
- CIDR: 172.32.0.0/16
- Subnets:
  - EgressPublicSubnet (172.32.1.0/24)
  - EgressTransitSubnet (172.32.2.0/24)

### 2. Setting Up Route Tables

Create and configure four route tables with the following associations:

| Route Table Name    | Primary Routes      | Associated Subnet    | Subnet CIDR    |
|--------------------|---------------------|---------------------|----------------|
| WorkLoadPrivateRT  | 172.32.0.0/16 → local | WorkLoadPrivateSubnet | 10.0.1.0/24    |
| WorkLoadTransitRT  | 10.0.0.0/16 → local  | WorkLoadTransitSubnet | 10.0.2.0/24    |
| EgressTransitRT    | 172.32.0.0/16 → local| EgressTransitSubnet   | 172.32.2.0/24  |
| EgressNATRT        | 172.32.0.0/16 → local| EgressPublicSubnet    | 172.32.1.0/24  |

### 3. Creating and Attaching Internet Gateway

1. Navigate to Internet Gateways in the AWS console
2. Create a new Internet Gateway
3. Attach it to the EgressVPC to enable internet access for EgressPublicSubnet

### 4. Setting Up Transit Gateway

1. Navigate to VPC > Transit Gateways
2. Create a new Transit Gateway with these settings:
   - Name: Transit-Gateway01
   - DNS Support: Enabled
   - VPN ECMP Support: Enabled
   - Default Route Table Association: Enabled
   - Default Route Table Propagation: Enabled
   - Auto Accept Shared Attachments: Disabled

![Transit Gateway Configuration](https://s3.brilliant.com.bd/blog-bucket/thumbnail/a5b5da42-2419-48a2-b3e9-345f50a646d7.png)
*Figure 2: Transit Gateway configuration settings*

### 5. Creating Transit Gateway Attachments

Create two Transit Gateway attachments:

**WorkloadVPC Attachment:**
- Name: WorkLoadVPC-TGW-Att
- Attachment Type: VPC
- Select WorkloadVPC

![WorkloadVPC Transit Gateway Attachment](https://s3.brilliant.com.bd/blog-bucket/thumbnail/ab263114-d058-48d6-8b9f-02f02da8658e.png)
*Figure 3: WorkloadVPC Transit Gateway attachment configuration*

**EgressVPC Attachment:**
- Name: EgressVPC-TGW-Att
- Attachment Type: VPC
- Select EgressVPC

![EgressVPC Transit Gateway Attachment](https://s3.brilliant.com.bd/blog-bucket/thumbnail/d0af3562-3857-4552-9d13-a6f24a84346e.png)
*Figure 4: EgressVPC Transit Gateway attachment configuration*

### 6. Deploying NAT Gateway

Create a NAT Gateway in the EgressPublicSubnet to handle internet traffic for private subnets.

![NAT Gateway Configuration](https://s3.brilliant.com.bd/blog-bucket/thumbnail/6388e991-6d13-4c86-bc34-18783e64d02f.png)
*Figure 5: NAT Gateway configuration in EgressPublicSubnet*

### 7. Configuring Final Route Tables

Update the route tables with the following routes:

**WorkLoadPrivateRT:**
- 0.0.0.0/0 → Transit Gateway
- 10.0.0.0/16 → local

**WorkLoadTransitRT:**
- 10.0.0.0/16 → local

**EgressTransitRT:**
- 0.0.0.0/0 → NAT Gateway
- 172.32.0.0/16 → local

**EgressNATRT:**
- 0.0.0.0/0 → Internet Gateway
- 10.0.0.0/16 → Transit Gateway
- 172.32.0.0/16 → local

To verify your route table configurations, you can view the Resource Maps for both VPCs:

![EgressVPC Resource Map](https://s3.brilliant.com.bd/blog-bucket/thumbnail/3d5bf8d3-74fa-4787-90ef-47f6d05453e1.png)
*Figure 6: EgressVPC Resource Map showing routing configuration*

![WorkloadVPC Resource Map](https://s3.brilliant.com.bd/blog-bucket/thumbnail/a0234eb7-2d3b-466d-bb17-88da1bc914c1.png)
*Figure 7: WorkloadVPC Resource Map showing routing configuration*

## Testing the Configuration

To verify your setup:

1. Launch a bastion host in EgressPublicSubnet
2. Launch a private instance in WorkloadPrivateSubnet
3. SSH into the bastion host:
   ```bash
   ssh -i "key.pem" ubuntu@<public-ip>
   ```
4. From the bastion host, SSH into the private instance:
   ```bash
   ssh -i "key.pem" ubuntu@<private-ip>
   ```
5. Test internet connectivity:
   ```bash
   curl https://poridhi.io
   ```
6. Verify NAT Gateway usage:
   ```bash
   curl ifconfig.me
   ```
   The returned IP should match your NAT Gateway's public IP address.

## Conclusion

By implementing this centralized architecture with AWS Transit Gateway, you can significantly reduce costs while maintaining secure internet access for your private subnets. This setup is particularly beneficial for organizations running multiple VPCs that require internet access.

Remember to monitor your Transit Gateway and NAT Gateway usage to ensure optimal performance and cost efficiency.