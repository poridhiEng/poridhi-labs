#!/bin/bash

# Configuration
REGION="ap-southeast-1"
VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"
INSTANCE_TYPE="t2.micro"
AMI_ID="ami-0df7a207adb9748c7"  # Ubuntu 22.04 LTS in ap-southeast-1
KEY_NAME="MyKeyPair"            # Make sure this key pair exists
PROJECT_NAME="Poridhi"
STATE_FILE="infrastructure_state.json"

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is not installed. Please install jq first."
        exit 1
    fi
}

# Function to initialize state file
init_state_file() {
    if [ ! -f "$STATE_FILE" ]; then
        echo '{
            "project_name": "",
            "region": "",
            "resources": {
                "vpc": null,
                "internet_gateway": null,
                "subnet": null,
                "route_table": null,
                "security_group": null,
                "instance": null
            },
            "created_at": null,
            "status": "not_started"
        }' > "$STATE_FILE"
    fi
}

# Function to update state
update_state() {
    local resource_type=$1
    local resource_id=$2
    local temp_file="temp_$STATE_FILE"
    
    jq --arg type "$resource_type" \
       --arg id "$resource_id" \
       --arg time "$(date '+%Y-%m-%d %H:%M:%S')" \
       --arg project "$PROJECT_NAME" \
       --arg region "$REGION" \
       '.resources[$type] = $id | .created_at = $time | .project_name = $project | .region = $region | .status = "in_progress"' \
       "$STATE_FILE" > "$temp_file" && mv "$temp_file" "$STATE_FILE"
}

# Function to check if resource exists in state
check_resource() {
    local resource_type=$1
    local resource_id=$(jq -r ".resources.$resource_type" "$STATE_FILE")
    
    if [ "$resource_id" != "null" ]; then
        if aws ec2 describe-${resource_type}s --${resource_type}-ids "$resource_id" --region "$REGION" 2>/dev/null; then
            echo "Resource $resource_type ($resource_id) already exists."
            return 0
        else
            echo "Resource $resource_type ($resource_id) in state file not found in AWS. Will create new one."
            return 1
        fi
    fi
    return 1
}

# Create VPC if not exists
create_vpc() {
    if ! check_resource "vpc"; then
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

        aws ec2 modify-vpc-attribute \
            --vpc-id $VPC_ID \
            --enable-dns-hostnames "{\"Value\":true}" \
            --region $REGION

        update_state "vpc" "$VPC_ID"
        echo "VPC ID: $VPC_ID"
    fi
    VPC_ID=$(jq -r '.resources.vpc' "$STATE_FILE")
}

# Create Internet Gateway if not exists
create_internet_gateway() {
    if ! check_resource "internet_gateway"; then
        echo "Creating Internet Gateway..."
        IGW_ID=$(aws ec2 create-internet-gateway \
            --region $REGION \
            --query 'InternetGateway.InternetGatewayId' \
            --output text)

        aws ec2 create-tags \
            --resources $IGW_ID \
            --tags Key=Name,Value="$PROJECT_NAME-IGW" \
            --region $REGION

        aws ec2 attach-internet-gateway \
            --internet-gateway-id $IGW_ID \
            --vpc-id $VPC_ID \
            --region $REGION

        update_state "internet_gateway" "$IGW_ID"
        echo "Internet Gateway ID: $IGW_ID"
    fi
    IGW_ID=$(jq -r '.resources.internet_gateway' "$STATE_FILE")
}

# Create Subnet if not exists
create_subnet() {
    if ! check_resource "subnet"; then
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

        aws ec2 modify-subnet-attribute \
            --subnet-id $SUBNET_ID \
            --map-public-ip-on-launch \
            --region $REGION

        update_state "subnet" "$SUBNET_ID"
        echo "Subnet ID: $SUBNET_ID"
    fi
    SUBNET_ID=$(jq -r '.resources.subnet' "$STATE_FILE")
}

# Create Route Table if not exists
create_route_table() {
    if ! check_resource "route_table"; then
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

        aws ec2 create-route \
            --route-table-id $ROUTE_TABLE_ID \
            --destination-cidr-block 0.0.0.0/0 \
            --gateway-id $IGW_ID \
            --region $REGION

        aws ec2 associate-route-table \
            --route-table-id $ROUTE_TABLE_ID \
            --subnet-id $SUBNET_ID \
            --region $REGION

        update_state "route_table" "$ROUTE_TABLE_ID"
        echo "Route Table ID: $ROUTE_TABLE_ID"
    fi
    ROUTE_TABLE_ID=$(jq -r '.resources.route_table' "$STATE_FILE")
}

# Create Security Group if not exists
create_security_group() {
    if ! check_resource "security_group"; then
        echo "Creating Security Group..."
        SG_ID=$(aws ec2 create-security-group \
            --group-name "$PROJECT_NAME-SG-$(date +%s)" \
            --description "$PROJECT_NAME Security Group" \
            --vpc-id $VPC_ID \
            --region $REGION \
            --query 'GroupId' \
            --output text)

        aws ec2 create-tags \
            --resources $SG_ID \
            --tags Key=Name,Value="$PROJECT_NAME-SG" \
            --region $REGION

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

        update_state "security_group" "$SG_ID"
        echo "Security Group ID: $SG_ID"
    fi
    SG_ID=$(jq -r '.resources.security_group' "$STATE_FILE")
}

# Create EC2 Instance if not exists
create_ec2_instance() {
    if ! check_resource "instance"; then
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

        echo "Waiting for instance to be running..."
        aws ec2 wait instance-running \
            --instance-ids $INSTANCE_ID \
            --region $REGION

        update_state "instance" "$INSTANCE_ID"
        echo "Instance ID: $INSTANCE_ID"
    fi
    INSTANCE_ID=$(jq -r '.resources.instance' "$STATE_FILE")
}

# Function to get instance public IP
get_instance_ip() {
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --region $REGION \
        --output text)
    echo "Instance Public IP: $PUBLIC_IP"
}

# Main execution
echo "Checking prerequisites..."
check_jq
init_state_file

echo "Starting infrastructure creation..."
create_vpc
create_internet_gateway
create_subnet
create_route_table
create_security_group
create_ec2_instance
get_instance_ip

# Mark state as completed
jq '.status = "completed"' "$STATE_FILE" > "temp_$STATE_FILE" && mv "temp_$STATE_FILE" "$STATE_FILE"

echo ""
echo "Infrastructure creation completed!"
echo "State file updated: $STATE_FILE"
echo ""
echo "To connect to your instance:"
echo "ssh -i MyKeyPair.pem ubuntu@${PUBLIC_IP}"