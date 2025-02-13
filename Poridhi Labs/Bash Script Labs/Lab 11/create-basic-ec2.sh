#!/bin/bash

# Configuration
REGION="ap-southeast-1"
VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"
INSTANCE_TYPE="t2.micro"
AMI_ID="ami-0df7a207adb9748c7"  # Ubuntu 22.04 LTS in ap-southeast-1
KEY_NAME="MyKeyPair"
PROJECT_NAME="Poridhi"

# Create VPC
echo "Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
    --cidr-block $VPC_CIDR \
    --region $REGION \
    --query 'Vpc.VpcId' \
    --output text)

aws ec2 create-tags \
    --resources $VPC_ID \
    --tags Key=Name,Value="$PROJECT_NAME-VPC" \
    --region $REGION

# Enable DNS hostnames
aws ec2 modify-vpc-attribute \
    --vpc-id $VPC_ID \
    --enable-dns-hostnames "{\"Value\":true}" \
    --region $REGION

echo "VPC ID: $VPC_ID"

# Create Internet Gateway
echo "Creating Internet Gateway..."
IGW_ID=$(aws ec2 create-internet-gateway \
    --region $REGION \
    --query 'InternetGateway.InternetGatewayId' \
    --output text)

aws ec2 create-tags \
    --resources $IGW_ID \
    --tags Key=Name,Value="$PROJECT_NAME-IGW" \
    --region $REGION

# Attach to VPC
aws ec2 attach-internet-gateway \
    --internet-gateway-id $IGW_ID \
    --vpc-id $VPC_ID \
    --region $REGION

echo "Internet Gateway ID: $IGW_ID"

# Create Subnet
echo "Creating Subnet..."
SUBNET_ID=$(aws ec2 create-subnet \
    --vpc-id $VPC_ID \
    --cidr-block $SUBNET_CIDR \
    --region $REGION \
    --query 'Subnet.SubnetId' \
    --output text)

aws ec2 create-tags \
    --resources $SUBNET_ID \
    --tags Key=Name,Value="$PROJECT_NAME-Public-Subnet" \
    --region $REGION

# Enable auto-assign public IP
aws ec2 modify-subnet-attribute \
    --subnet-id $SUBNET_ID \
    --map-public-ip-on-launch \
    --region $REGION

echo "Subnet ID: $SUBNET_ID"

# Create Route Table
echo "Creating Route Table..."
ROUTE_TABLE_ID=$(aws ec2 create-route-table \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'RouteTable.RouteTableId' \
    --output text)

aws ec2 create-tags \
    --resources $ROUTE_TABLE_ID \
    --tags Key=Name,Value="$PROJECT_NAME-Public-RT" \
    --region $REGION

# Add route to Internet Gateway
aws ec2 create-route \
    --route-table-id $ROUTE_TABLE_ID \
    --destination-cidr-block 0.0.0.0/0 \
    --gateway-id $IGW_ID \
    --region $REGION

# Associate with subnet
aws ec2 associate-route-table \
    --route-table-id $ROUTE_TABLE_ID \
    --subnet-id $SUBNET_ID \
    --region $REGION

echo "Route Table ID: $ROUTE_TABLE_ID"

# Create Security Group
echo "Creating Security Group..."
SG_ID=$(aws ec2 create-security-group \
    --group-name "$PROJECT_NAME-SG" \
    --description "$PROJECT_NAME Security Group" \
    --vpc-id $VPC_ID \
    --region $REGION \
    --query 'GroupId' \
    --output text)

aws ec2 create-tags \
    --resources $SG_ID \
    --tags Key=Name,Value="$PROJECT_NAME-SG" \
    --region $REGION

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region $REGION

aws ec2 authorize-security-group-ingress \
    --group-id $SG_ID \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0 \
    --region $REGION

echo "Security Group ID: $SG_ID"

# Launch EC2 Instance
echo "Creating EC2 Instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --subnet-id $SUBNET_ID \
    --security-group-ids $SG_ID \
    --region $REGION \
    --query 'Instances[0].InstanceId' \
    --output text)

aws ec2 create-tags \
    --resources $INSTANCE_ID \
    --tags Key=Name,Value="$PROJECT_NAME-Server" \
    --region $REGION

echo "Instance ID: $INSTANCE_ID"

# Wait for instance to be running
echo "Waiting for instance to be running..."
aws ec2 wait instance-running \
    --instance-ids $INSTANCE_ID \
    --region $REGION

# Get public IP address
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --region $REGION \
    --output text)

echo ""
echo "Infrastructure creation completed!"
echo "Instance Public IP: $PUBLIC_IP"
echo ""
echo "To connect to your instance:"
echo "ssh -i MyKeyPair.pem ubuntu@${PUBLIC_IP}"