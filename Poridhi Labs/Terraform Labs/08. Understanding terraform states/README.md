# Understanding Terraform State

In this lab, we will delve into the concept of Terraform state and understand what happens under the hood when we run Terraform commands to provision infrastructure. By exploring the Terraform workflow, we will observe the creation and management of the state file and see how Terraform uses this state file to manage resources effectively.

Terraform state is a critical component in Terraform's architecture. It serves as a mapping of the real-world infrastructure to your configuration files. This state file ensures that Terraform knows what resources exist in your infrastructure, what configurations they have, and how they relate to one another.

## Initialize Terraform and Understand the Workflow

1. **Create the `main.tf` file:**

    ```python
    resource "local_file" "pet" {
      filename = var.filename
      content  = var.content
    }
    ```

2. **Create the `variables.tf` file:**

    ```python
    variable "filename" {
      description = "The name of the file to be created"
      type        = string
      default     = "/root/pet.txt"
    }

    variable "content" {
      description = "The content of the file"
      type        = string
      default     = "I love pets!"
    }
    ```

3. **Initialize Terraform:**

    ```sh
    terraform init
    ```

    The `terraform init` command initializes the directory, downloads necessary plugins, and sets up the backend.

## Plan and Apply the Terraform Configuration

1. **Generate an Execution Plan:**

    ```sh
    terraform plan
    ```

    The `terraform plan` command generates an execution plan, showing what actions Terraform will take to achieve the desired state as defined in the configuration files. It also refreshes the in-memory state prior to the plan.

2. **Apply the Terraform Configuration:**

    ```sh
    terraform apply
    ```

    The `terraform apply` command applies the changes required to reach the desired state of the configuration. It also refreshes the in-memory state, creates an execution plan, and then provisions the resources.

## Inspect the Terraform State File

1. **List the files in the directory:**

    ```sh
    ls
    ```

    
    After running `terraform apply`, a new file called `terraform.tfstate` is created in the directory. This file is the Terraform state file, which records the state of the infrastructure.

2. **Open the `terraform.tfstate` file:**

    ```sh
    cat terraform.tfstate
    ```

    
    The state file is a JSON data structure that maps the real-world infrastructure resources to the resource definition in the configuration files. It contains details such as the resource ID, provider information, and all resource attributes.

#### Step 4: Modify the Configuration and Observe State Changes

1. **Modify the content variable in `variables.tf`:**

    ```python
    # variables.tf
    variable "content" {
      description = "The content of the file"
      type        = string
      default     = "We love pets!"
    }
    ```

2. **Apply the Changes:**

    ```sh
    terraform apply
    ```

    
    When you rerun `terraform apply`, Terraform refreshes the state, compares it against the configuration file, and determines that the content of the file has changed. It then creates a new execution plan to update the resource and the state file accordingly.

#### Step 5: Understand State File Precedence

1. **Set Environment Variable and Create Variable Definition Files:**

    ```sh
    export TF_VAR_filename=/root/cats.txt
    ```

    **Create `terraform.tfvars` file:**

    ```python
    # terraform.tfvars
    filename = "/root/pets.txt"
    ```

    **Create `variable.auto.tfvars` file:**

    ```python
    # variable.auto.tfvars
    filename = "/root/mypet.txt"
    ```

2. **Apply Configuration with Command Line Flag:**

    ```sh
    terraform apply -var="filename=/root/best-pet.txt"
    ```

    
    Terraform follows a specific order to determine which value to use when the same variable is defined in multiple places:
    1. Environment variables.
    2. `terraform.tfvars` or `terraform.tfvars.json` files.
    3. Any file ending with `.auto.tfvars` or `.auto.tfvars.json` (alphabetical order).
    4. Command line flags (`-var` or `-var-file`).

    In this case, the value `/root/best-pet.txt` will be used for the `filename` variable, as command line flags take the highest precedence.

## Conclusion

In this lab, we covered the concept of Terraform state, observed the creation and management of the state file, and understood how Terraform uses this state file to manage resources. We also learned about the precedence of variable definitions and how Terraform ensures the infrastructure is in sync with the configuration files. This knowledge is crucial for effectively managing and provisioning infrastructure using Terraform.