# Using Variables in Terraform

In this lab, we will explore different ways to use input variables in Terraform. We'll cover how to create variables, assign default values, use command-line flags, environment variables, and variable definition files. By the end of this lab, you'll understand the precedence of variable definitions in Terraform.


## Defining Variables in Terraform

### 1.1 Creating Variables with Default Values

1. **Create the `variables.tf` file:**

```python
# variables.tf
variable "filename" {
  description = "The name of the file to be created"
  type        = string
  default     = "/root/default.txt"
}
```


In this example, if no value is provided for `filename`, Terraform will use `/root/default.txt`.

### 1.2 Creating Variables Without Default Values

1. **Update the `variables.tf` file:**

```python
# variables.tf
variable "filename" {
  description = "The name of the file to be created"
  type        = string
}
```


Variables without default values require an input during runtime.

## Using Variables in Terraform Configurations

1. **Create the `main.tf` file:**

```python
# main.tf
resource "local_file" "example" {
  filename = var.filename
  content  = "This is an example file."
}
```


This configuration uses the `filename` variable to create a local file.

## Passing Variables in Different Ways

### 3.1 Interactive Input

1. **Run `terraform apply`:**

```sh
terraform apply
```


When you run `terraform apply`, Terraform will prompt you to enter a value for the variable `filename`.

![alt text](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/05.%20Using%20variables%20in%20terraform/images/image.png?raw=true)

### 3.2 Command Line Flags

1. **Pass variable values using the `-var` flag:**

```sh
terraform apply -var="filename=/root/pets.txt"
```


You can pass variable values directly through the command line using the `-var` flag.

### 3.3 Environment Variables

1. **Set environment variable and run `terraform apply`:**

```sh
export TF_VAR_filename=/root/animals.txt
terraform apply
```


You can set environment variables using the `TF_VAR_` prefix followed by the variable name.

### 3.4 Variable Definition Files

1. **Create a `terraform.tfvars` file:**

```python
# terraform.tfvars
filename = "/root/pets.txt"
```

2. **Create a `variable.auto.tfvars` file:**

```python
# variable.auto.tfvars
filename = "/root/mypet.txt"
```


Variables can be defined in files ending with `.tfvars` or `.tfvars.json`. Terraform automatically loads these files.

## Variable Definition Precedence

1. **Set environment variable:**

```sh
export TF_VAR_filename=/root/cats.txt
```

2. **Create `terraform.tfvars` file:**

```python
# terraform.tfvars
filename = "/root/pets.txt"
```

3. **Create `variable.auto.tfvars` file:**

```python
# variable.auto.tfvars
filename = "/root/mypet.txt"
```

4. **Run `terraform apply` with command line flag:**

```sh
terraform apply -var="filename=/root/best-pet.txt"
```

#### 
Terraform follows a specific order to determine which value to use when the same variable is defined in multiple places:


| Order | Option                                    |
|-------|-------------------------------------------|
| 1     | Environment Variables                     |
| 2     | terraform.tfvars                          |
| 3     | *.auto.tfvars (alphabetical order)        |
| 4     | -var or –var-file (command-line flags)    |
|       |                                           |


In this case, the value `/root/best-pet.txt` will be used for the `filename` variable, as command line flags take the highest precedence.

## Conclusion

In this lab, we covered various methods to assign values to input variables in Terraform. We saw how to define variables in `.tf` files, pass values through the command line, use environment variables, and variable definition files. Understanding the precedence of these methods will help you manage and organize your Terraform configurations more effectively.