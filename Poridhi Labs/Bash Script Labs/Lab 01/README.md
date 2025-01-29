# AWS VPC Infrastructure Creation using Bash Script

This lab walks through creating and managing AWS Virtual Private Clouds (VPCs) using Bash scripts, implementing state management to prevent duplicate resources, and following AWS networking best practices.

## Prerequisites

### Required Tools
- AWS CLI installed and configured with appropriate credentials
- Bash shell environment
- jq (JSON processor)

### Installing jq
Run the following commands to install jq on Ubuntu/Debian:

```bash
# Update package list
sudo apt-get update

# Install jq
sudo apt-get install -y jq

# Verify installation
jq --version
```

### Why We Need jq?

`jq` is a lightweight and powerful command-line JSON processor.

We need `jq` because:

1. **JSON Parsing**: Efficiently reads and writes JSON data
   
2. **Data Manipulation**: Makes it easy to:
   - Filter data
   - Transform structures
   - Update values
   - Extract specific fields

3. **Command Line Usage**: Works well in shell scripts and command line

4. **Data Validation**: Ensures proper JSON formatting

5. **Query Features**: 
   - Supports complex queries
   - Pattern matching
   - Data transformation

Without `jq`, handling JSON in shell scripts would be complex and error-prone.

## AWS Configuration

First, we need to configure our AWS CLI with the following command:

```bash
aws configure
``` 

## VPC Creation using Bash Script

Create a new file named `create-vpc.sh` and add the following script:

```bash
#!/bin/bash

# Configuration
REGION="ap-southeast-1"
VPC_NAME="MyBasicVPC"
VPC_CIDR="10.0.0.0/16"

# Create VPC
echo "Creating VPC..."
VPC_ID=$(aws ec2 create-vpc \
  --cidr-block $VPC_CIDR \
  --region $REGION \
  --query 'Vpc.VpcId' \
  --output text)

# Add name tag
aws ec2 create-tags \
  --resources $VPC_ID \
  --tags Key=Name,Value=$VPC_NAME \
  --region $REGION

echo "VPC created!"
echo "VPC Name: $VPC_NAME"
echo "VPC ID: $VPC_ID"
echo "Region: $REGION"
echo "CIDR: $VPC_CIDR"
```

This will create a VPC with the specified name and CIDR block in the specified region.

### Running the Bash Script

```bash
# Make script executable
chmod +x create-vpc.sh

# Run the script
./create-vpc.sh
```

## 4. Understanding CIDR Block Issues

### Testing Duplicate VPC Creation
Run the script again and check existing VPCs:

```bash
# List all VPCs
aws ec2 describe-vpcs --region ap-southeast-1 \
  --query 'Vpcs[*].{ID:VpcId,Name:Tags[?Key==`Name`].Value,CIDR:CidrBlock}' \
  --output table
```

### Identified Problems
- Multiple VPCs with same CIDR block (10.0.0.0/16) are created
- No built-in AWS prevention of duplicate CIDR blocks
- Potential networking complications

## Enhanced Solution with State Management

### Enhanced VPC Creation Script
Save the following script as create-vpc-with-state.sh:

```bash
#!/bin/bash

# Configuration
REGION="ap-southeast-1"
VPC_NAME="MyBasicVPC"
VPC_CIDR="10.0.0.0/16"
JSON_FILE="vpc_inventory.json"

# Function to check if jq is installed
check_jq() {
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is not installed. Please install jq first."
        exit 1
    fi
}

# Function to create or update JSON file if it doesn't exist
init_json_file() {
    if [ ! -f "$JSON_FILE" ]; then
        echo "[]" > "$JSON_FILE"
    fi
}

# Function to check for existing VPC with same name or CIDR
check_existing_vpc() {
    local name_exists=$(jq -r --arg name "$VPC_NAME" --arg cidr "$VPC_CIDR" \
        'map(select(.vpc_name == $name)) | length' "$JSON_FILE")
    
    local cidr_exists=$(jq -r --arg name "$VPC_NAME" --arg cidr "$VPC_CIDR" \
        'map(select(.cidr == $cidr)) | length' "$JSON_FILE")

    if [ "$name_exists" -gt 0 ]; then
        echo "Warning: VPC with name '$VPC_NAME' already exists!"
        jq -r --arg name "$VPC_NAME" \
            'map(select(.vpc_name == $name)) | .[]' "$JSON_FILE"
        return 1
    fi

    if [ "$cidr_exists" -gt 0 ]; then
        echo "Warning: VPC with CIDR '$VPC_CIDR' already exists!"
        jq -r --arg cidr "$VPC_CIDR" \
            'map(select(.cidr == $cidr)) | .[]' "$JSON_FILE"
        return 1
    fi

    return 0
}

# Function to add VPC details to JSON file
add_vpc_to_json() {
    local vpc_id=$1
    local temp_file="temp_$JSON_FILE"
    
    jq --arg id "$vpc_id" \
       --arg name "$VPC_NAME" \
       --arg cidr "$VPC_CIDR" \
       --arg region "$REGION" \
       '. += [{
           "vpc_id": $id,
           "vpc_name": $name,
           "cidr": $cidr,
           "region": $region,
           "created_at": (now | strftime("%Y-%m-%d %H:%M:%S"))
       }]' "$JSON_FILE" > "$temp_file" && mv "$temp_file" "$JSON_FILE"
}
```

## Conclusion
This guide provides a structured approach to creating and managing AWS VPCs using Bash scripts. By implementing state management with `jq`, we ensure that duplicate VPCs are not created, avoiding networking conflicts and maintaining resource efficiency. Following best practices and troubleshooting guidelines will help in managing AWS networking infrastructure effectively. Regular maintenance and monitoring of the state file further enhance the reliability of the setup.

