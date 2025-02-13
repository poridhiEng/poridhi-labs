# Automating AWS EC2 Infrastructure with Bash Script

This lab provides a hands-on guide to automating AWS EC2 infrastructure creation using the AWS CLI. It first explores the challenges of stateless infrastructure automation, then introduces a state-managed approach using JSON tracking to enhance reliability and prevent resource duplication.

## Objectives
By the end of this lab, you will:
- Understand how to create a VPC, subnet, and EC2 instances using AWS CLI.
- Recognize the issues associated with stateless automation.
- Implement state management to track created resources.
- Develop idempotent scripts to ensure reliable execution.

## Prerequisites
Before starting, ensure you have:
- An AWS account with CLI access.
- AWS CLI v2 installed and configured.
- Basic networking knowledge.
- A terminal with bash/zsh support.

---

# Part 1: Basic Infrastructure Creation (Without State Management)

## Step 1: Create an SSH Key Pair
Generate a key pair for instance access:

```bash
aws ec2 create-key-pair \
    --key-name MyKeyPair \
    --query 'KeyMaterial' \
    --output text > MyKeyPair.pem
chmod 400 MyKeyPair.pem
```

## Step 2: Create the Infrastructure Script
Create a script file named `create-basic-ec2.sh`:

```bash
nano create-basic-ec2.sh
# Paste the provided script content and save
chmod +x create-basic-ec2.sh
```

## Step 3: Execute the Script
Run the script to create AWS resources:

```bash
./create-basic-ec2.sh
```

**Expected Output:**
```
Creating VPC...
VPC ID: vpc-0123456789abcdef0
Creating Internet Gateway...
Internet Gateway ID: igw-0123456789abcdef0
...
Instance Public IP: 54.255.129.21
```

## Step 4: Observe Issues
Run the script again without cleaning up resources:

```bash
./create-basic-ec2.sh
```

**Problems:**
1. Duplicate VPCs are created.
2. Security group name conflicts occur.
3. Multiple instances are launched unnecessarily.
4. No straightforward way to track created resources.

---

# Part 2: State-Managed Infrastructure Creation

## Step 1: Install `jq` for JSON Processing
Ensure `jq` is installed for handling JSON files:

```bash
sudo apt-get install jq  # Ubuntu/Debian
# OR
brew install jq          # macOS
```

## Step 2: Create a State-Managed Script
Create a new script file named `create-managed-ec2.sh`:

```bash
nano create-managed-ec2.sh
# Paste the provided script content and save
chmod +x create-managed-ec2.sh
```

## Step 3: Execute the Script
Run the state-managed script:

```bash
./create-managed-ec2.sh
```

**First Run Output:**
```
Checking prerequisites...
Starting infrastructure creation...
Creating VPC...
VPC ID: vpc-0123456789abcdef1
Creating Internet Gateway...
Internet Gateway ID: igw-0123456789abcdef1
...
State file updated: infrastructure_state.json
```

## Step 4: Verify the State File
Check the stored state information:

```bash
cat infrastructure_state.json
```

**Sample Output:**
```json
{
  "project_name": "Poridhi",
  "region": "ap-southeast-1",
  "resources": {
    "vpc": "vpc-0123456789abcdef1",
    "internet_gateway": "igw-0123456789abcdef1",
    "subnet": "subnet-0123456789abcdef1",
    "route_table": "rtb-0123456789abcdef1",
    "security_group": "sg-0123456789abcdef1",
    "instance": "i-0123456789abcdef1"
  },
  "created_at": "2023-10-15 14:30:45",
  "status": "completed"
}
```

## Step 5: Re-run the Script
Run the script again:

```bash
./create-managed-ec2.sh
```

**Improvements:**
- Existing resources are reused instead of duplicated.
- The script checks if resources already exist before creating them.
- A structured state file provides easy tracking.

---

# Infrastructure Management Features

## Key Features
1. **State Tracking:**
   - Keeps an `infrastructure_state.json` file.
   - Prevents duplicate resource creation.
   
2. **Idempotent Operations:**
   - Checks if resources exist before creating them.
   - Uses dynamic security group naming to avoid conflicts.
   
3. **Dependency Management:**
   - Ensures a logical creation order:
     ```
     VPC → Internet Gateway → Subnet → Route Table → Security Group → EC2
     ```

4. **Clean Output:**
   - Provides clear progress messages and final connection details.

---

# Infrastructure Cleanup

## Step 1: Create a Destroy Script (`destroy-infra.sh`)

```bash
#!/bin/bash

STATE_FILE="infrastructure_state.json"

# Load resources from state
VPC_ID=$(jq -r '.resources.vpc' $STATE_FILE)
IGW_ID=$(jq -r '.resources.internet_gateway' $STATE_FILE)
INSTANCE_ID=$(jq -r '.resources.instance' $STATE_FILE)
SG_ID=$(jq -r '.resources.security_group' $STATE_FILE)
SUBNET_ID=$(jq -r '.resources.subnet' $STATE_FILE)
RT_ID=$(jq -r '.resources.route_table' $STATE_FILE)

# Terminate EC2 instance
aws ec2 terminate-instances --instance-ids $INSTANCE_ID
aws ec2 wait instance-terminated --instance-ids $INSTANCE_ID

# Delete security group
aws ec2 delete-security-group --group-id $SG_ID

# Disassociate and delete route table
aws ec2 disassociate-route-table --association-id $(aws ec2 describe-route-tables --route-table-ids $RT_ID --query 'RouteTables[0].Associations[0].RouteTableAssociationId' --output text)
aws ec2 delete-route-table --route-table-id $RT_ID

# Delete subnet
aws ec2 delete-subnet --subnet-id $SUBNET_ID

# Detach and delete internet gateway
aws ec2 detach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
aws ec2 delete-internet-gateway --internet-gateway-id $IGW_ID

# Delete VPC
aws ec2 delete-vpc --vpc-id $VPC_ID

# Remove state file
rm $STATE_FILE

echo "Cleanup completed!"
```

## Step 2: Execute Cleanup

```bash
chmod +x destroy-infra.sh
./destroy-infra.sh
```

---

# Conclusion
By completing this lab, you have:
1. Created basic EC2 infrastructure with AWS CLI.
2. Identified issues with stateless automation.
3. Implemented JSON-based state management.
4. Developed idempotent scripts for reliable execution.
5. Managed infrastructure lifecycle effectively.

This foundational approach can be extended using tools like Terraform or AWS CloudFormation for even more advanced automation.