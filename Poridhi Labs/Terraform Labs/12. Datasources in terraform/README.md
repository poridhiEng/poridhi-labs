# Understanding Data Sources in Terraform

In this lab, we will explore data sources in Terraform. We know that Terraform uses configuration files along with a state file to provision infrastructure resources. However, infrastructure can also be provisioned using other tools like Puppet, CloudFormation, SaltStack, Ansible, and even ad-hoc scripts. Data sources allow Terraform to read attributes from resources provisioned outside its control and use these attributes within its managed infrastructure. This lab will walk you through the process of using data sources to read information from an external resource and incorporate it into Terraform-managed resources.

## Task 1: Using Local File Data Source to Update Terraform Managed Resource

Let's assume that we have a local file resource called `petstore.txt` created with the content "We love pets" and stored in the `/root` directory. We also have another file called `dogs.txt`, created outside of Terraform's control, which contains the line "Dogs are awesome." We want to use the contents of `dogs.txt` as a data source and update the content of our `petstore.txt` file managed by Terraform.

## Lab Steps

### Step 1: Create Initial Configuration

1. **Create the `main.tf` file:**

    ```hcl
    resource "local_file" "pet" {
      filename = "/root/petstore.txt"
      content  = "We love pets!"
    }
    ```

2. **Initialize Terraform:**

    ```sh
    terraform init
    ```

    
    The `terraform init` command initializes the directory, downloads necessary plugins, and sets up the backend.

### Step 2: Provision the Initial Resource

1. **Apply the Terraform Configuration:**

    ```sh
    terraform apply
    ```

    
    The `terraform apply` command provisions the local file resource `petstore.txt` with the specified content.

### Step 3: Create an External File

1. **Create a Shell Script to Generate an External File:**

    ```sh
    echo "Dogs are awesome!" > /root/dogs.txt
    ```

    
    This command creates a file `dogs.txt` in the `/root` directory with the content "Dogs are awesome!" This resource is provisioned outside terraforms control. Now We want to use this resource as data source.

### Step 4: Define a Data Source in Terraform

1. **Update the `main.tf` file to include a data source:**

    ```hcl
    resource "local_file" "pet" {
      filename = "/root/petstore.txt"
      content  = data.local_file.dog.content
    }

    data "local_file" "dog" {
      filename = "/root/dogs.txt"
    }
    ```

    
    The `data "local_file" "dog"` block defines a data source for the external file `dogs.txt`. The `content` attribute of this data source is then used in the `content` argument of the `local_file` resource `pet`.

### Step 5: Apply the Updated Configuration

1. **Apply the Updated Configuration:**

    ```sh
    terraform apply
    ```

    
    Terraform will read the content of `dogs.txt` using the data source and update `petstore.txt` with this content.

### Step 6: Verify the Changes

1. **Check the Content of `petstore.txt`:**

    ```sh
    cat /root/petstore.txt
    ```

    **Expected Output:**

    ```
    Dogs are awesome!
    ```

    
    The content of `petstore.txt` should now be "Dogs are awesome!" as it has been updated using the data from the external `dogs.txt` file.





## Task 2: Using a JSON File as a Data Source
In this scenario, we'll use a JSON file as a data source to read data in Terraform. We'll then use the content of this JSON file to provision another local file that reflects this data.


## Lab steps

### Step 1: Create a JSON File

Create a JSON file named `data.json` with the following content:

```json
{
  "message": "Hello from the JSON file!"
}
```

### Step 2: Define the Data Source in Terraform

Next, define a data source in Terraform to read data from the JSON file. Create a Terraform configuration file named `main.tf` with the following content:

```hcl
provider "local" {}

data "local_file" "json_file" {
  filename = "${path.module}/data.json"
}

locals {
  json_content = jsondecode(data.local_file.json_file.content)
}

resource "local_file" "output_file" {
  content  = local.json_content["message"]
  filename = "${path.module}/output.txt"
}
```

- **Data Source Definition:** 
  - The `local_file` data source reads the contents of `data.json`.
  
- **Local Value:**
  - `locals` block is used to decode the JSON content into a map using `jsondecode()`. 

- **Resource Definition:** 
  - The `local_file` resource uses the `message` attribute from the decoded JSON content to create `output.txt`.

<!-- ### Step 3: Use Data Source Attributes in Resource Provisioning

In the example:
- The `data.local_file.json_file.content` reads the JSON file as a string.
- The `jsondecode()` function converts this string into a map.
- The `message` key from this map is used as the content for the `output_file` resource. -->

### Step 3: Run Terraform Commands

1. **Initialize Terraform:**

   ```sh
   terraform init
   ```

2. **Generate and Review the Execution Plan:**

   ```sh
   terraform plan
   ```

3. **Apply the Execution Plan:**

   ```sh
   terraform apply
   ```

### Step 4: Verify the Changes 

After running these commands, Terraform will create a file named `output.txt` with the content:

```
Hello from the JSON file!
```

This scenario shows how Terraform can use a JSON file as a data source, read and decode its content, and then use that data in other resources




## Resource vs Data Source

### **Resources**
- **Purpose:** Resources are used to create, update, or destroy infrastructure components.
- **Block Type:** Defined with the `resource` keyword.
- **Examples:** EC2 instances, S3 buckets, local files.
- **Lifecycle Management:** Terraform manages the lifecycle of resources. It creates, updates, and deletes them as specified in the configuration.

### **Data Sources**
- **Purpose:** Data sources allow Terraform to read information from existing infrastructure that is managed outside of Terraform or from other configurations.
- **Block Type:** Defined with the `data` keyword.
- **Examples:** Reading a value from a local file, querying information about existing AWS resources.
- **No Lifecycle Management:** Data sources are read-only and do not manage the lifecycle of the infrastructure. They provide information to be used in resource configurations.

**In Summary:**
- **Resources** manage and control infrastructure components.
- **Data Sources** retrieve information from existing resources without altering their state.




## Conclusion

In this lab, we explored the concept of data sources in Terraform. We learned how to read attributes from resources provisioned outside of Terraform's control and use these attributes within Terraform-managed resources. By defining a data source and incorporating its data into our configuration, we can effectively manage and integrate external resources into our Terraform infrastructure. This capability enhances Terraform's flexibility and interoperability with other tools and manually provisioned resources.








