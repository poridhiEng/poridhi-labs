# Output Variables in Terraform 

In this lab, we will explore `output variables` in Terraform. Output variables allow we to store and display values from our Terraform configurations, which can be useful for sharing information between configurations and for debugging purposes. We will go through the concept, syntax, and practical examples of output variables, followed by tasks with solutions.

## Understanding Output Variables

Output variables in Terraform are used to extract information from our Terraform state file and display it to the user or pass it to other configurations. They can help we to view specific attributes of our resources once they are created.

### Syntax

The syntax to define an output variable is as follows:
```hcl
output "variable_name" {
  value       = expression
  description = "Optional description"
}
```
- `output`: The keyword to define an output variable.
- `variable_name`: The name of the output variable.
- `value`: The expression whose result will be stored in the output variable.
- `description`: (Optional) A description of what this output variable represents.

## Example Configuration with Output Variables

Let's use the configuration file from the previous lab and add output variables to it.

1. **Create a directory for our Terraform files**:
   ```sh
   mkdir -p /root/terraform-output-example
   cd /root/terraform-output-example
   ```

2. **Create a configuration file named `main.tf`**:
   ```sh
   touch main.tf
   ```

3. **Edit `main.tf` to include a resource and output variable**:
   ```python
   provider "random" {}

   resource "random_pet" "example" {
     length    = 2
     separator = "-"
   }

   resource "local_file" "example" {
     filename = "/root/${random_pet.example.id}.txt"
     content  = "This file is named after a random pet."
   }

   output "pet_name" {
     value       = random_pet.example.id
     description = "The name of the randomly generated pet"
   }

   output "file_path" {
     value       = local_file.example.filename
     description = "The path of the created file"
   }
   ```

4. **Initialize Terraform**:
   ```sh
   terraform init
   ```

5. **Apply the Configuration**:
   ```sh
   terraform apply
   ```
   Confirm the action by typing `yes` when prompted. After applying, we should see the output variables printed on the screen.

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/07.%20Output%20variables%20in%20terraform/images/image.png?raw=true)

6. **View Output Variables**:
   we can also view the output variables using the following command:
   ```sh
   terraform output
   ```
   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/07.%20Output%20variables%20in%20terraform/images/image-1.png?raw=true)

## Practice Tasks

### Task 1: Create an Output Variable for File Content

1. **Modify the `main.tf` file to include an output variable for the file content**:
   ```python
   provider "random" {}

   resource "random_pet" "example" {
     length    = 2
     separator = "-"
   }

   resource "local_file" "example" {
     filename = "/root/${random_pet.example.id}.txt"
     content  = "This file is named after a random pet."
   }

   output "pet_name" {
     value       = random_pet.example.id
     description = "The name of the randomly generated pet"
   }

   output "file_path" {
     value       = local_file.example.filename
     description = "The path of the created file"
   }

   output "file_content" {
     value       = local_file.example.content
     description = "The content of the created file"
   }
   ```

2. **Apply the Configuration**:
   ```sh
   terraform apply
   ```
   Confirm the action by typing `yes` when prompted.

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/07.%20Output%20variables%20in%20terraform/images/image-2.png?raw=true)

3. **Verify the Output**:
   Use the following command to view all output variables, including the new `file_content` variable:
   ```sh
   terraform output
   ```

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/07.%20Output%20variables%20in%20terraform/images/image-3.png?raw=true)

### Task 2: Create a Dynamic File with Date and Time

1. **Create a configuration file named `dynamic_file.tf`**:
   ```sh
   touch dynamic_file.tf
   ```

2. **Edit `dynamic_file.tf` to include a resource and output variable for a file with the current date and time**:
   ```python
   provider "local" {}

   resource "local_file" "dynamic" {
     filename = "/root/dynamic_file.txt"
     content  = "File created at: ${timestamp()}"
   }

   output "file_creation_time" {
     value       = local_file.dynamic.content
     description = "The creation time of the dynamic file"
   }
   ```

3. **Initialize Terraform**:
   ```sh
   terraform init
   ```

4. **Apply the Configuration**:
   ```sh
   terraform apply
   ```
   Confirm the action by typing `yes` when prompted.

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/07.%20Output%20variables%20in%20terraform/images/image-4.png?raw=true)

5. **Verify the Output**:
   Use the following command to view the output variable showing the creation time of the file:
   ```sh
   terraform output file_creation_time
   ```

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/07.%20Output%20variables%20in%20terraform/images/image-5.png?raw=true)

## Conclusion

In this lab, we explored how to use output variables in Terraform to extract and display information about our resources. Output variables are a powerful feature that can help we debug, share, and manage our Terraform configurations more effectively. By completing the tasks, we have gained hands-on experience with defining and using output variables in different scenarios.