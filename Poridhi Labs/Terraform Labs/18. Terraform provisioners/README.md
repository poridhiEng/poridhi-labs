
# Understanding Terraform Provisioners

Provisioners in Terraform are used to execute scripts or commands on a local or remote machine after a resource has been created or before it is destroyed. They provide a way to perform additional configuration steps or to initiate tasks that aren’t natively supported by Terraform. However, provisioners should be used cautiously and as a last resort when necessary tasks cannot be achieved through native resource arguments or modules.

There are two primary types of provisioners:
1. **`remote-exec` Provisioner:** Executes commands on a remote resource, typically after it has been provisioned.
2. **`local-exec` Provisioner:** Executes commands on the local machine where Terraform is being run.

## **Detailed Description**

### **Remote-Exec Provisioner**
- **Purpose:** To run commands on a remote resource, typically after it has been created. This could include updating the system, installing software, or performing other post-deployment tasks.
- **Key Attributes:**
  - **`connection` block:** Defines how Terraform connects to the remote resource, usually via SSH for Linux instances.
  - **`inline` or `script`:** Specifies the commands or scripts to be executed on the remote machine.

### **Local-Exec Provisioner**
- **Purpose:** To run commands locally on the machine where Terraform is executed. This is useful for tasks like logging, sending notifications, or performing local file operations after a remote resource is created.
- **Key Attributes:**
  - **`command:`** Specifies the command to be executed locally.



## **Scenario Overview**
In this scenario, you will create an EC2 instance in AWS, set up an NGINX web server on it, and manage this process using both `remote-exec` and `local-exec` provisioners. The Terraform code provided will walk you through each step of this process.




## **Prerequisites**
Before starting with the Terraform configuration, ensure that the following prerequisites are met:

### **1. AWS Configuration**
- Ensure that you have the AWS CLI installed and configured with your credentials.
- Run the following command to configure your AWS CLI:
  ```bash
  aws configure
  ```
  You will be prompted to enter your AWS Access Key ID, Secret Access Key, region, and output format.

  ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/18.%20Terraform%20provisioners/images/image.png?raw=true)

### **2. VPC and Public Subnet**
- Ensure that you have an existing VPC and a public subnet. You can create them manually through the AWS Management Console.
- Note the VPC ID and Subnet ID, as they will be required in the Terraform configuration.

  ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/18.%20Terraform%20provisioners/images/image-1.png?raw=true)

### **3. SSH Key Generation**
- Generate an SSH key pair if you don’t have one already. This key will be used to SSH into the EC2 instance.
  ```bash
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
  ```
  The public key will be saved in `~/.ssh/id_rsa.pub` by default.






## **Step-by-Step Solution**

### **Step 1: Set Up the Terraform Configuration**
Start by creating a new directory for the lab and navigate to it. Inside the directory, create a file named `main.tf`. This file will contain the Terraform configuration.

```bash
mkdir terraform-provisioners-lab
cd terraform-provisioners-lab
touch main.tf
```


### **Step 2: Provider Configuration**
Begin by specifying the AWS provider, setting the region where your resources will be deployed.

```hcl
provider "aws" {
  region = "ap-southeast-1"
}
```
This code configures the AWS provider to use the `ap-southeast-1` region. Terraform will interact with AWS services in this specified region.

### **Step 3: Create an SSH Key Pair**
Create a new SSH key pair, or use an existing one, to authenticate access to the EC2 instance.

```hcl
resource "aws_key_pair" "example" {
  key_name   = "example-key"
  public_key = file("~/.ssh/id_rsa.pub")
}
```
The `aws_key_pair` resource creates a new key pair using an existing public key (`~/.ssh/id_rsa.pub`). The key pair will be used for SSH access to the EC2 instance.

### **Step 4: Define a Security Group**
Create a security group that allows SSH and HTTP traffic to the EC2 instance.

```hcl
resource "aws_security_group" "example" {
  name_prefix = "example-sg"
  vpc_id      = "vpc-049c7ce9e354b1684"  # Use your VPC ID

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```
This `aws_security_group` resource defines a security group allowing inbound SSH (port 22) and HTTP (port 80) traffic from any IP address. The egress rule allows all outbound traffic. Use your own VPC ID.

### **Step 5: Provision an EC2 Instance**
Deploy an EC2 instance with the specified security group, subnet, and key pair, and use provisioners to manage the server.

```hcl
resource "aws_instance" "example" {
  ami               = "ami-060e277c0d4cce553"    # valid AMI for ubuntu
  instance_type     = "t2.micro"
  key_name          = aws_key_pair.example.key_name
  subnet_id         = "subnet-0eff5dfa5368470f9"    # Use your subnet ID
  vpc_security_group_ids = [aws_security_group.example.id]
  associate_public_ip_address = true 
```
This `aws_instance` resource creates an EC2 instance using a specific AMI and instance type (`t2.micro`). The instance is launched in a specified subnet with the security group created earlier. The `associate_public_ip_address = true` ensures that the instance gets a public IP address.

### **Step 6: Execute Commands with Remote-Exec Provisioner**
Use the `remote-exec` provisioner to update the server, install NGINX, and start the service.

```hcl
provisioner "remote-exec" {
  connection {
    type        = "ssh"
    user        = "ubuntu"
    private_key = file("~/.ssh/id_rsa")
    host        = self.public_ip
  }

  inline = [
    "sudo apt update -y",
    "sudo apt install -y nginx",
    "sudo systemctl enable nginx",
    "sudo systemctl start nginx"
  ]
}
```
The `remote-exec` provisioner connects to the EC2 instance via SSH using the `ubuntu` user and the private key. It then runs a series of commands to update the server, install NGINX, and start the web server.

### **Step 7: Log Output with Local-Exec Provisioner**
Use the `local-exec` provisioner to log the public IP of the instance locally.

```hcl
  provisioner "local-exec" {
    command = "echo Instance ${self.public_ip} created! > instance_ip.txt"
  }
```
The `local-exec` provisioner runs a command on your local machine that logs the public IP of the EC2 instance into a file called `instance_ip.txt`.

### **Step 8: Clean Up with Destroy Provisioners**
Use `remote-exec` and `local-exec` provisioners to stop and remove NGINX when the instance is destroyed.

```hcl
  provisioner "remote-exec" {
    when    = "destroy"
    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")
      host        = self.public_ip
    }

    inline = [
      "sudo systemctl stop nginx",
      "sudo apt remove -y nginx"
    ]
  }

  provisioner "local-exec" {
    when    = "destroy"
    command = "echo Instance ${self.public_ip} destroyed! > instance_ip.txt"
  }
}
```
The `when = "destroy"` argument in both `remote-exec` and `local-exec` provisioners ensures that these commands are executed before the resource is destroyed. The remote commands stop and remove NGINX, while the local command logs that the instance has been destroyed.

### **Step 9: Applying the Configuration**
To apply the Terraform configuration, follow these steps:

1. **Initialize the Terraform working directory:**
   ```bash
   terraform init
   ```

2. **Validate the configuration to check for errors:**
   ```bash
   terraform validate
   ```

3. **Apply the configuration to create the resources:**
   ```bash
   terraform apply
   ```
   Review the plan output and confirm the apply by typing `yes`.

4. **Check the output to ensure the provisioners have run successfully and that the EC2 instance is set up with NGINX.**


  - **`local-exec` Provisioner result:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/18.%20Terraform%20provisioners/images/image-5.png?raw=true)

  - **`remote-exec` Provisioner result:**

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/18.%20Terraform%20provisioners/images/image-3.png?raw=true)

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/18.%20Terraform%20provisioners/images/image-4.png?raw=true)




5. **Destroy the resources when they are no longer needed:**
   ```bash
   terraform destroy
   ```
   Confirm the destruction by typing `yes`. This will trigger the destroy provisioners to run before the resources are removed.

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/18.%20Terraform%20provisioners/images/image-2.png?raw=true)

## **Conclusion**
Provisioners in Terraform provide a flexible way to execute scripts or commands both locally and remotely, adding additional configuration steps to your infrastructure as code process. In this lab, we demonstrated how to use both `remote-exec` and `local-exec` provisioners to automate the setup and teardown of an NGINX.


