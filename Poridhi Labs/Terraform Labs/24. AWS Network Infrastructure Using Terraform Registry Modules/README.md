# AWS Network Infrastructure Using Terraform Registry Modules

In this lab, you will learn how to use Terraform modules from the Terraform Registry to create network infrastructure on AWS. This includes setting up a Virtual Private Cloud (VPC), public and private subnets, route tables, and an internet gateway. Terraform modules help you abstract and reuse infrastructure code, making it easier to manage and scale your deployments.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/24.%20AWS%20Network%20Infrastructure%20Using%20Terraform%20Registry%20Modules/images/logo.png?raw=true)

## Scenario Description

You need to set up a networking environment in AWS, including a VPC, public and private subnets, route tables, and an internet gateway. Rather than writing all the configuration from scratch, you will use a module from the Terraform Registry, which simplifies the setup process and ensures that best practices are followed.

## Objectives

1. Explore and select a suitable network module from the Terraform Registry.
2. Use the selected module to create a VPC with public and private subnets, route tables, and an internet gateway.
3. Customize the module inputs to fit your project requirements.
4. Apply the Terraform configuration to deploy the network infrastructure.
5. Verify that the network infrastructure is correctly deployed in AWS.

## Step 1: Exploring the Terraform Registry

### Visit the Terraform Registry

1. Open your web browser and navigate to the [Terraform Registry](https://registry.terraform.io/).
2. In the search bar, type "vpc" to search for VPC-related modules.
3. Look for the `terraform-aws-modules/vpc/aws` module, which is a well-maintained and widely used module for creating VPCs and related networking resources.

### Review the Module Documentation

1. Click on the `terraform-aws-modules/vpc/aws` module to open its detailed documentation.
2. Review the examples, input variables, and outputs provided in the documentation to understand how the module works and what configurations are required.


## Step 2: Setting Up the Project Structure

### Install AWS CLI

Before proceeding, ensure that the AWS CLI is installed on your local machine. Follow the instructions below based on your operating system:

- **Windows**:
  1. Download the AWS CLI MSI installer from the [official AWS website](https://aws.amazon.com/cli/).
  2. Run the downloaded MSI installer and follow the instructions.

- **Linux**:
  ```sh
  curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
  unzip awscliv2.zip
  sudo ./aws/install
  ```

#### Configure AWS CLI

After installing the AWS CLI, configure it with the necessary credentials. Run the following command and follow the prompts to configure it:

```sh
aws configure
```

- **Explanation**: This command sets up your AWS CLI with the necessary credentials, region, and output format.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/24.%20AWS%20Network%20Infrastructure%20Using%20Terraform%20Registry%20Modules/images/5.png?raw=true)

You will find the `AWS Access key` and `AWS Seceret Access key` on Lab description page,where you generated the credentials

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/24.%20AWS%20Network%20Infrastructure%20Using%20Terraform%20Registry%20Modules/images/6.png?raw=true)

### Create the Project Directory

Create a new directory for your Terraform project:

```sh
mkdir terraform-aws-network
cd terraform-aws-network
```

### Create the Main Configuration File

Create a `main.tf` file where you will define the Terraform configuration to use the VPC module from the Terraform Registry:

```py
# main.tf

provider "aws" {
  region = "ap-southeast-1"
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "4.0.0"  # Specify the version of the module

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-southeast-1a"]
  private_subnets = ["10.0.1.0/24"]
  public_subnets  = ["10.0.101.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  enable_dns_hostnames = true
  enable_dns_support   = true

  # Explicitly enable auto-assign public IPv4 address on public subnets
  map_public_ip_on_launch = true

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}
```

### Explanation

- **`provider "aws"`**: Specifies the AWS provider and the region where resources will be created.
- **`module "vpc"`**: Uses the VPC module from the Terraform Registry to create a VPC along with public and private subnets, NAT gateways, and route tables.
- **`cidr`**: Specifies the CIDR block for the VPC.
- **`azs`**: Specifies the availability zones in which the subnets will be created.
- **`private_subnets` and `public_subnets`**: Define the CIDR blocks for the private and public subnets, respectively.
- **`enable_nat_gateway`**: Enables the creation of NAT gateways for private subnets.
- **`single_nat_gateway`**: Configures the module to create only one NAT gateway.

## Step 3: Initializing and Applying Terraform

### Initialize Terraform

Initialize your Terraform workspace to download the required provider plugins and the VPC module:

```sh
terraform init
```

- This command will download the AWS provider and the `terraform-aws-modules/vpc/aws` module from the Terraform Registry.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/24.%20AWS%20Network%20Infrastructure%20Using%20Terraform%20Registry%20Modules/images/1.png?raw=true)

### Apply the Configuration

Apply the Terraform configuration to create the network infrastructure:

```sh
terraform apply
```

- Terraform will show a plan of the changes it will make. Review the plan to ensure it matches your expectations.
- Type `yes` when prompted to confirm the creation of resources.

### Monitor the Progress

As Terraform applies the configuration, it will create the VPC, subnets, route tables, and internet gateway in AWS. This process might take a few minutes, especially if NAT gateways are being created.

## Step 4: Verifying the Infrastructure

### Verify the VPC and Subnets

1. Log in to the [AWS Management Console](https://aws.amazon.com/console/).
2. Navigate to the VPC service under the "Networking & Content Delivery" section.
3. Verify that the VPC named `my-vpc` has been created with the correct CIDR block.
4. Check that the public and private subnets have been created within the VPC across the specified availability zones.

### Verify the Route Tables and Internet Gateway

1. In the VPC Dashboard, go to "Route Tables" and verify that route tables have been created for both public and private subnets.
2. Ensure that the public route table has a route to the internet gateway, and the private route table has a route through the NAT gateway.
3. Navigate to the "Internet Gateways" section and verify that an internet gateway has been created and attached to the VPC.

### Verify the Resource Map

In the VPC Dashboard, click on `my-vpc` we just created,here you will find resource map

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/24.%20AWS%20Network%20Infrastructure%20Using%20Terraform%20Registry%20Modules/images/2.png?raw=true)

## Step 5: Cleaning Up

### Destroy the Infrastructure (Optional)

If you want to clean up the resources created by this lab, you can destroy them using Terraform:

```sh
terraform destroy
```

- Terraform will show a plan of the resources it will destroy. Review the plan, and if it looks good, type `yes` to confirm.

### Remove Local Files (Optional)

After destroying the infrastructure, you can remove the local Terraform files if you no longer need them:

```sh
rm -rf .terraform terraform.tfstate terraform.tfstate.backup
```

## Conclusion

In this lab, you learned how to use a module from the Terraform Registry to create a complete network infrastructure in AWS, including a VPC, subnets, route tables, and an internet gateway. By leveraging the power of Terraform modules, you were able to quickly and efficiently set up a complex networking environment with minimal manual configuration.