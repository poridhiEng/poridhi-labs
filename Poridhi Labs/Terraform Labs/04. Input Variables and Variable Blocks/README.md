# Input Variables and Variable Blocks in Terraform

In this lab, we will explore how to use input variables and variable blocks in Terraform. Input variables enhance the flexibility and reusability of Terraform configurations by allowing values to be set dynamically rather than being hardcoded. We will also learn about different types of variables that Terraform supports.

## Understanding Input Variables

Input variables in Terraform enable you to parameterize your configurations. They allow you to pass values dynamically when executing Terraform commands, making your configurations more flexible and reusable.

## Creating Input Variables

To create input variables, we use a separate configuration file called `variables.tf`. The syntax to define an input variable is as follows:

```python
variable "variable_name" {
  default     = "default_value"
  description = "Description of the variable"
  type        = string
}
```
- `variable`: The keyword to define an input variable.
- `variable_name`: The name of the variable.
- `default`: (Optional) The default value for the variable.
- `description`: (Optional) A description of what the variable is used for.
- `type`: (Optional) The type of the variable (e.g., string, number, boolean).

### Example Configuration with Input Variables

Let's create a configuration that uses input variables.

1. **Create a directory for your Terraform files**:
   ```sh
   mkdir -p /root/terraform-input-variables
   cd /root/terraform-input-variables
   ```

2. **Create a configuration file named `variables.tf`**:
   ```sh
   touch variables.tf
   ```

3. **Edit `variables.tf` to define input variables**:
   ```python
   variable "file_name" {
     description = "The name of the file to create"
     type        = string
     default     = "example.txt"
   }

   variable "file_content" {
     description = "The content of the file to create"
     type        = string
     default     = "Hello, Terraform!"
   }

   variable "pet_name_prefix" {
     description = "The prefix for the random pet name"
     type        = string
     default     = "pet"
   }

   variable "pet_name_length" {
     description = "The length of the random pet name"
     type        = number
     default     = 2
   }
   ```

4. **Create the main configuration file named `main.tf`**:
   ```sh
   touch main.tf
   ```

5. **Edit `main.tf` to use the defined variables**:
   ```python
   provider "random" {}

   resource "random_pet" "example" {
     length    = var.pet_name_length
     separator = "-"
   }

   resource "local_file" "example" {
     filename = "/root/${var.file_name}"
     content  = var.file_content
   }
   ```

6. **Initialize Terraform**:
   ```sh
   terraform init
   ```

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/04.%20Input%20Variables%20and%20Variable%20Blocks/images/image.png?raw=true)

7. **Apply the Configuration**:
   ```sh
   terraform apply
   ```
   Confirm the action by typing `yes` when prompted. After applying, you should see the output variables printed on the screen.

8. **View Created file**:
   Go to root directory and use:
   ```
   ls
   ``` 

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/04.%20Input%20Variables%20and%20Variable%20Blocks/images/image-7.png?raw=true)

## Variable Types

Terraform supports various variable types to handle different data structures. Let's explore the basic and complex variable types available in Terraform.

### Basic Variable Types

1. **String**: A single value that is alphanumeric.
   ```python
   variable "example_string" {
     type        = string
     default     = "Hello, World!"
   }
   ```

2. **Number**: A single numeric value, positive or negative.
   ```python
   variable "example_number" {
     type        = number
     default     = 42
   }
   ```

3. **Boolean**: A value that is either true or false.
   ```python
   variable "example_boolean" {
     type        = boolean
     default     = true
   }
   ```

### Complex Variable Types

1. **List**: A collection of values, referenced by their index.
   ```python
   variable "example_list" {
     type        = list(string)
     default     = ["value1", "value2", "value3"]
   }
   ```

2. **Map**: A collection of key-value pairs.
   ```python
   variable "example_map" {
     type        = map(string)
     default     = {
       key1 = "value1"
       key2 = "value2"
     }
   }
   ```

3. **Set**: Similar to a list but cannot contain duplicate values.
   ```python
   variable "example_set" {
     type        = set(string)
     default     = ["value1", "value2", "value3"]
   }
   ```

4. **Object**: A collection of named attributes that can each be a different type.
   ```python
   variable "example_object" {
     type = object({
       name   = string
       age    = number
       active = boolean
     })
     default = {
       name   = "Terraform"
       age    = 5
       active = true
     }
   }
   ```

5. **Tuple**: A sequence of elements with specified types.
   ```python
   variable "example_tuple" {
     type = tuple([string, number, boolean])
     default = ["Terraform", 5, true]
   }
   ```

## Tasks with Solutions

### Task 1: Update Variable Values

1. **Update the `variables.tf` file to include new default values**:
   ```python
   variable "file_name" {
     description = "The name of the file to create"
     type        = string
     default     = "updated_example.txt"
   }

   variable "file_content" {
     description = "The content of the file to create"
     type        = string
     default     = "My favorite pet is Mrs. Whiskers"
   }

   variable "pet_name_prefix" {
     description = "The prefix for the random pet name"
     type        = string
     default     = "pet"
   }

   variable "pet_name_length" {
     description = "The length of the random pet name"
     type        = number
     default     = 2
   }
   ```

2. **Apply the Configuration**:
   ```sh
   terraform apply
   ```
   Confirm the action by typing `yes` when prompted.

3. **Verify the changes**:
   
   Go to the root directory and use:

    ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/04.%20Input%20Variables%20and%20Variable%20Blocks/images/image-9.png?raw=true)

### Task 2: Use Complex Variable Types

1. **Update the `variables.tf` file to include a list and map variable**:
   ```python
   variable "prefix_list" {
     description = "A list of prefixes for the random pet names"
     type        = list(string)
     default     = ["Mr", "Mrs", "Sir"]
   }

   variable "file_content_map" {
     description = "A map of file contents"
     type        = map(string)
     default     = {
       statement1 = "Hello, Terraform!"
       statement2 = "Goodbye, Terraform!"
     }
   }
   ```

2. **Edit `main.tf` to use the new variables**:
   ```python
   provider "random" {}

   resource "random_pet" "example" {
     length    = var.pet_name_length
     separator = "-"
   }

   resource "local_file" "example" {
     filename = "/root/${var.file_name}"
     content  = var.file_content_map["statement2"]
   }
   ```

3. **Apply the Configuration**:
   ```sh
   terraform apply
   ```
   Confirm the action by typing `yes` when prompted.


4. **Verify the Result**:
   Go to the root directory and varify the result:

   ![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/04.%20Input%20Variables%20and%20Variable%20Blocks/images/image-8.png?raw=true)

## Conclusion

In this lab, we explored how to use input variables and variable blocks in Terraform. We defined variables in a separate `variables.tf` file and used them in our main configuration file. By completing the tasks, you have gained hands-on experience with creating and using input variables, including complex variable types like lists, maps, sets, objects, and tuples. This knowledge will help you write more flexible and reusable Terraform configurations.