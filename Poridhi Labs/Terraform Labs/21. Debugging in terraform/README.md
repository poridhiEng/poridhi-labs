# Debugging in Terraform

This lab is designed to give you hands-on experience with the debugging Terraform configurations using logs. By the end of this lab, you will be able to debug Terraform issues effectively.

## Enabling and Using Debugging in Terraform

Terraform allows detailed logging to help debug issues. The `TF_LOG` environment variable controls the verbosity of logs, with levels ranging from `ERROR` to `TRACE`. Logs can also be saved to a file using the `TF_LOG_PATH` environment variable.

- **Log Levels:**
  - `ERROR`: Logs only errors.
  - `WARN`: Logs warnings and errors.
  - `INFO`: Logs informational messages.
  - `DEBUG`: Logs detailed debug information.
  - `TRACE`: Logs the most detailed trace of operations.

- **Storing Logs:** Use `TF_LOG_PATH` to save logs to a file for persistent storage.

## Debugging a Terraform Configuration

### **Scenario Overview:**
We will introduce an error in a Terraform configuration and use Terraform's logging capabilities to identify and fix the issue.

### **Prerequisites:**
- Create a VPC. 
- Create a subnet within that VPC
- Copy the subnet ID for EC2
- Configure AWS using `aws configure` command


### Step 1: Create a Terraform Configuration with an Error
- Create a `main.tf` file with an invalid AMI ID:
    ```hcl
    provider "aws" {
      region = "ap-southeast-1"
    }
    resource "aws_instance" "web_server" {
      ami           = "invalid-ami-id"
      instance_type = "t2.micro"
      subnet_id = "subnet-0c5bbf26b42210759"  # Use your subnet ID
    }
    ```

### Step 2: Set the Logging Level to TRACE
   - Before running Terraform, set the `TF_LOG` environment variable:
     ```bash
     export TF_LOG=TRACE
     ```
   - Initialize terraform:
        ```bash
        terraform init
        ```
      
   - Apply the configuration to trigger the error:
     ```bash
     terraform apply
     ```
   - Observe the detailed logs in your terminal. These logs will provide insights into where the error occurred.

        ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/21.%20Debugging%20in%20terraform/images/image.png?raw=true)

### Step 3: Store Logs in a File
   - Set the `TF_LOG_PATH` environment variable to store the logs:
     ```bash
     export TF_LOG_PATH=terraform-debug.log
     ```
   - Run `terraform apply` again. This time, the logs will be saved to `terraform-debug.log`.

        ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/21.%20Debugging%20in%20terraform/images/image-1.png?raw=true)

### Step 4: Identify and Fix the Issue
   - Open the `terraform-debug.log` file and search for clues regarding the error.
   - Identify that the issue is due to the invalid AMI ID.
   - Correct the AMI ID in `main.tf`:

     ```hcl
     ami = "ami-060e277c0d4cce553"
     ```
### Step 5: Disable Logging
   - After resolving the issue, unset the logging environment variables:

     ```bash
     unset TF_LOG
     unset TF_LOG_PATH
     ```
   - Apply the corrected configuration:

     ```bash
     terraform apply
     ```
   - Verify that the instance is created successfully.

        ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/21.%20Debugging%20in%20terraform/images/image-2.png?raw=true)



## Debugging Local File Creation

### **Scenario Overview:**
In this scenario, you will create a local file using Terraform’s `local_file` resource. You will introduce an issue with the file path and use logging to debug and correct the problem.


### **Step 1: Create a Terraform Configuration to Create a Local File**
   - Create a `main.tf` file to generate a simple text file on your local machine:
     ```hcl
     resource "local_file" "example_file" {
       filename = "output/example.txt"
       content  = "This is a sample file created by Terraform."
     }
     ```

### **Step 2: Run Terraform Init and Apply**
   - Run the following command to initialize the configuration:
        ```bash
        terraform init
        ```

   - Run the following command to apply the configuration:
     ```bash
     terraform apply
     ```
   - You might encounter an error if the `output` directory does not exist.
### **Step 3: Identify the Issue Using DEBUG Logging**
   - Set the `TF_LOG` environment variable to `DEBUG` to capture detailed logs:
     ```bash
     export TF_LOG=DEBUG
     ```
   - Run `terraform apply` again and observe the logs. The error message should indicate that the specified path does not exist.

### **Step 4: Fix the File Path Issue**
   - Update the configuration by either:
     - Creating the `output` directory manually before applying the configuration, or
     - Changing the `filename` to a path that exists, such as `"example.txt"` in the current directory:

     ```hcl
     resource "local_file" "example_file" {
       filename = "example.txt"  # Corrected path
       content  = "This is a sample file created by Terraform."
     }
     ```

### **Step 5: Apply the Corrected Configuration**
   - Unset the logging environment variable:

     ```bash
     unset TF_LOG
     ```
   - Apply the corrected configuration:

     ```bash
     terraform apply
     ```
   - Verify that the `example.txt` file is successfully created in the specified location.

### **Summary**

In this lab, you learned how to effectively debug issues using Terraform's logging features. These skills are essential for managing infrastructure as code, ensuring that resources are provisioned correctly, and quickly resolving any issues that arise.