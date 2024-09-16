# Terraform Taints

This lab is designed to give you hands-on experience with the `terraform taint` and `terraform untaint` commands. By the end of this lab, you will be able to identify and manage tainted resources.

## Understanding Tainted Resources

Terraform taints mark a resource for recreation in the next `terraform apply` operation. This can happen automatically if Terraform fails to provision a resource, marking it as "tainted" due to the failure. Tainted resources are then scheduled for destruction and recreation to fix any issues. 

You can also manually taint a resource using the `terraform taint` command, forcing it to be recreated in the next apply. If you decide that a resource shouldn't be recreated, you can reverse the tainted status with the `terraform untaint` command, preventing it from being destroyed and recreated.

## Prerequisites

1. configure AWS using `aws configure` command in the AWS CLI.
2. Create a VPC in the AWS `ap-southeast-1` region.  
3. Create a subnet in the VPC and copy the subnet ID.

## Automatic Tainting due to Provisioner Failure

### **Scenario Overview**
You will simulate a scenario where an EC2 instance's creation fails due to an incorrect local provisioner configuration, resulting in Terraform automatically marking the resource as tainted.

### **Step 1: Create the Terraform Configuration**
   - Create a new directory for this lab and navigate into it.
   - Create a `main.tf` file with the following content:

     ```hcl
     provider "aws" {
       region = "ap-southeast-1"
     }

     resource "aws_instance" "web_server" {
       ami           = "ami-060e277c0d4cce553"  # This should be a valid AMI for your region.
       instance_type = "t2.micro"
       subnet_id     = "subnet-0c5bbf26b42210759" 

       provisioner "local-exec" {
         command = "echo ${self.public_ip} > /invalid_path/web_server_ip.txt"
       }
     }
     ```
   - This configuration attempts to create an EC2 instance and store its public IP in a file. The path `/invalid_path/` is intentionally incorrect.

### **Step 2: Initialize and Apply the Configuration**
   - Initialize Terraform in your directory:

     ```bash
     terraform init
     ```
   - Apply the configuration:
     ```bash
     terraform apply
     ```
   - Observe the failure caused by the incorrect file path.

      ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image.png?raw=true)

### **Step 3: Inspect the Tainted Resource**
   - After the failure, run:

     ```bash
     terraform plan
     ```
   - Notice that Terraform marks the `aws_instance.web_server` resource as tainted and plans to recreate it.

      ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-1.png?raw=true)

### **Step 4: Correct the Configuration and Apply**
   - Correct the file path in `main.tf`:

     ```hcl
     command = "echo ${self.public_ip} > /tmp/web_server_ip.txt"
     ```
   - Apply the changes:

     ```bash
     terraform apply
     ```
   - Verify that the instance is recreated successfully, and the file is written to the correct path.

      ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-2.png?raw=true)



## Manually Tainting and Untainting Resources

### **Scenario Overview**
In this scenario, you will manually taint a resource to force its recreation and then untaint it to prevent unnecessary recreation.

### **Steps**

### **Step 1: Create a New Terraform Configuration**
   - Modify your `main.tf` to remove the provisioner and just create an EC2 instance:

     ```hcl
     provider "aws" {
        region = "ap-southeast-1"
     } 
     resource "aws_instance" "web_server" {
       ami           = "ami-060e277c0d4cce553"
       instance_type = "t2.micro"
       subnet_id     = "subnet-0c5bbf26b42210759"  # Replace with your subnet ID
     }
     ```

### **Step 2: Init and Apply the Configuration**

   - Init the terraform:

     ```bash
     terraform init
     ```

   - Apply the changes:

     ```bash
     terraform apply
     ```
   - Verify that the instance is created successfully.

### **Step 3: Manually Taint the Resource**
   - Use the `terraform taint` command to mark the instance as tainted:

     ```bash
     terraform taint aws_instance.web_server
     ```

      ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-3.png?raw=true)

   - Run the command:
      ```
      terraform plan
      ```
      to see that Terraform plans to recreate the instance.

        ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-4.png?raw=true)

### **Step 4: Untaint the Resource**
   - Use the `terraform untaint` command to remove the taint:

     ```bash
     terraform untaint aws_instance.web_server
     ```

      ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-5.png?raw=true)

   - Run the command: 
      ```
      terraform plan
      ``` 
      This will confirm that the instance will not be recreated.

        ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-6.png?raw=true)

### **Step 5: Apply the Final Configuration**
   - Apply the final configuration:

     ```bash
     terraform apply
     ```
   - Verify that no changes are made to the existing instance.

      ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/20.%20Terraform%20taints/images/image-7.png?raw=true)

## **Summary**

In this lab, you practiced handling tainted resources in Terraform, both automatically and manually. These skills are essential for managing infrastructure as code, ensuring that resources are provisioned correctly.