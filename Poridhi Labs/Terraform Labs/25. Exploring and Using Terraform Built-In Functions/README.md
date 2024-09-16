# Exploring and Using Terraform Built-In Functions

In this lab, you will explore various built-in functions in Terraform. These functions help you manipulate and transform data within your Terraform configurations, making your infrastructure code more flexible and dynamic. By using the Terraform console, you will test these functions and understand how they work in practice.

## Objectives

1. Understand and use common Terraform built-in functions, including numeric, string, collection, and map functions.
2. Use the Terraform console to experiment with functions in real-time.
3. Apply functions within a Terraform configuration to solve practical problems.

## Step 1: Setting Up Terraform

### Create a Terraform Project Directory

Start by creating a directory for your Terraform project:

```sh
mkdir terraform-functions-lab
cd terraform-functions-lab
```

### Create a Basic Terraform Configuration

Create a `main.tf` file with a basic Terraform configuration that includes some variables and resources:

```py
provider "local" {
  # No region or other configuration required for the local provider
}

variable "file_contents" {
  type = map(string)
  default = {
    "file1" = "This is content for file1."
    "file2" = "This is content for file2."
    "file3" = "This is content for file3."
  }
}

resource "local_file" "example1" {
  content  = lookup(var.file_contents, "file1", "Default content")
  filename = "${path.module}/example1.txt"
}

resource "local_file" "example2" {
  content  = lookup(var.file_contents, "file2", "Default content")
  filename = "${path.module}/example2.txt"
}

resource "local_file" "example3" {
  content  = lookup(var.file_contents, "file3", "Default content")
  filename = "${path.module}/example3.txt"
}
```

### Explanation:
- **Provider**: The `local` provider is initialized.
- **Variable `file_contents`**: Contains the content for each of the three files.
- **`lookup` function**: Retrieves content from the `file_contents` map by key, with a default value if the key isn't found.
- **Resources**: Three `local_file` resources are defined, each creating a different file (`example1.txt`, `example2.txt`, `example3.txt`) with the corresponding content from the `file_contents` map.

## Step 2: Exploring Numeric, String, and Collection Functions

### Start the Terraform Console

The Terraform console allows you to interactively test functions and expressions. Start the console by running:

```sh
terraform console
```

### Test Numeric Functions

- **ceil**: Rounds up to the nearest whole number.

  ```py
  > ceil(10.3)
  11
  ```

- **floor**: Rounds down to the nearest whole number.

  ```py
  > floor(10.9)
  10
  ```

- **max**: Returns the maximum value from a list of numbers.

  ```py
  > max(5, 10, 15)
  15
  ```

- **min**: Returns the minimum value from a list of numbers.

  ```py
  > min(5, 10, 15)
  5
  ```

  ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/25.%20Exploring%20and%20Using%20Terraform%20Built-In%20Functions/images/1.png?raw=true)


### Test String Functions

- **split**: Splits a string into a list based on a delimiter.

  ```py
  > split(",", "file1,file2,file3")
  [
    "file1",
    "file2",
    "file3",
  ]
  ```

- **join**: Joins a list of strings into a single string with a delimiter.

  ```py
  > join("-", ["example", "files", "created"])
  "example-files-created"
  ```

- **lower**: Converts a string to lowercase.

  ```py
  > lower("HELLO")
  "hello"
  ```

- **upper**: Converts a string to uppercase.

  ```py
  > upper("hello")
  "HELLO"
  ```

  ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/25.%20Exploring%20and%20Using%20Terraform%20Built-In%20Functions/images/2.png?raw=true)

### Test Collection Functions

- **length**: Returns the length of a list, map, or string.

  ```py
  > length([1, 2, 3, 4])
  4
  ```

- **contains**: Checks if a list contains a specific element.

  ```py
  > contains(["a", "b", "c"], "b")
  true
  ```

- **keys**: Returns the keys of a map as a list.

  ```py
  > keys(var.file_contents)
  [
    "file1",
    "file2",
    "file3",
  ]
  ```

- **values**: Returns the values of a map as a list.

  ```py
  > values(var.file_contents)
  [
    "This is content for file1.",
    "This is content for file2.",
    "This is content for file3.",
  ]
  ```

- **lookup**: Looks up a value in a map based on a key.

  ```py
  > lookup(var.file_contents, "file1", "Default content")
  "This is content for file1."
  ```

  ![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/25.%20Exploring%20and%20Using%20Terraform%20Built-In%20Functions/images/3.png?raw=true)

### Test Map Functions

- **merge**: Merges two or more maps into one.

  ```py
  > merge({"a" = 1}, {"b" = 2})
  {
    "a" = 1,
    "b" = 2,
  }
  ```

- **zipmap**: Creates a map from two lists: one for keys and one for values.

  ```py
  > zipmap(["a", "b", "c"], [1, 2, 3])
  {
    "a" = 1,
    "b" = 2,
    "c" = 3,
  }
  ```

## Step 3: Applying Functions in Terraform Configuration

### Update the Terraform Configuration

Add more examples to the `main.tf` file to demonstrate the use of various functions:

```py
resource "local_file" "example" {
  content  = join(", ", keys(var.file_contents))
  filename = "file_keys.txt"
}

resource "local_file" "lowercase_example" {
  content  = lower("HELLO TERRAFORM")
  filename = "lowercase.txt"
}
```

### Apply the Terraform Configuration

Apply the Terraform configuration to create the resources:

```sh
terraform apply
```

Type `yes` when prompted to confirm the creation of resources.

### Verify the Results

Check the contents of the generated files (`file_keys.txt` and `lowercase.txt`) to verify that the functions worked as expected.

![](https://github.com/Minhaz00/Terraform-Labs/blob/main/Terraform%20Labs/25.%20Exploring%20and%20Using%20Terraform%20Built-In%20Functions/images/4.png?raw=true)

## Conclusion

In this lab, you explored and used various built-in Terraform functions, including numeric, string, collection, and map functions. By experimenting with these functions in the Terraform console, you gained a deeper understanding of how they work and how they can be applied within your Terraform configurations. These functions enhance your ability to manipulate and transform data, making your Terraform configurations more dynamic and powerful.