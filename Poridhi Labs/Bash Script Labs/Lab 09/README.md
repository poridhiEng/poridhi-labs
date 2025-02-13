# Functions in Bash Scripting

Functions in Bash scripting allow you to encapsulate reusable blocks of code, making your scripts modular, organized, and easier to debug. In this lab, you'll learn how to define and use functions, pass arguments to them, and handle return values. We'll apply these concepts to a real-world scenario: **automated log file processing**.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/9081abec298d6513b8502ac29f8f557d8ea8e4c0/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/Functions.svg)

By the end of this lab, you will understand:
- What functions are and why they are useful
- How to create and call functions
- Passing arguments to functions
- Returning values from functions
- Variable scope in functions
- Real-world use case: `Log file processor`

## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

## What Are Functions?

A **function** is a named block of code that performs a specific task. It can be reused multiple times within a script, eliminating code duplication and improving readability. Functions in Bash:
- Are defined before they are called.
- Can accept arguments (inputs).
- Can return values (exit statuses or output).

## How to Create Functions

### Syntax

There are two ways to define a function in Bash:

#### Method 1: Explicit `function` Keyword

```bash
function function_name {
  # Commands
}
```

#### Method 2: Compact Syntax

```bash
function_name() {
  # Commands
}
```

### Example 1: Basic Function

Create `function_basic.sh`:
```bash
#!/bin/bash

# Define a function
greet_user() {
  echo "Hello, User! Today is $(date)."
}

greet_user
```

**Explanation:**
- Defines a function `greet_user` that prints a greeting message.  
- Calls the function `greet_user`.

**Execute and run the script:**
```bash
chmod +x function_basic.sh
./function_basic.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image.png)

## How to Use Arguments in Functions

Functions accept arguments using positional parameters (`$1`, `$2`, etc.), similar to command-line arguments.

### Example 2: Function with Arguments
Create `function_args.sh`:
```bash
#!/bin/bash

# Function to calculate the sum of two numbers
sum() {
  local num1=$1  # First argument
  local num2=$2  # Second argument
  echo $((num1 + num2))
}

result=$(sum 10 20)
echo "Sum: $result"
```

**Key Points:**
- `$1` and `$2` represent the first and second arguments passed to the function.
- Use `local` to declare variables inside functions (avoids global scope side effects).

**Execute and run the script:**
```bash
chmod +x function_args.sh
./function_args.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-1.png)

## Returning Values from Functions

Bash functions return an **exit status** (0 for success, non-zero for failure) using `return`. However, you can "return" data by printing it and capturing it with command substitution.

### Example 3: Return Status and Output

Create `function_return.sh`:
```bash
#!/bin/bash

# Check if a file exists
check_file() {
  if [ -f "$1" ]; then
    echo "File exists: $1"
    return 0  # Success
  else
    echo "File not found: $1"
    return 1  # Failure
  fi
}

check_file "/etc/passwd"
if [ $? -eq 0 ]; then
  echo "File check passed!"
fi
```

**Explanation:**
- Defines a function `check_file` to check if a file exists.  
- Uses `-f` to verify the file and prints a message.  
- Returns `0` if the file exists, `1` otherwise.  
- Calls `check_file` on `/etc/passwd`.  
- If the file exists, prints `"File check passed!"`.

**Execute and run the script:**
```bash
chmod +x function_return.sh
./function_return.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-2.png)

Here we can see that the file exists and file check passed! `etc/passwd` already exists on a typical Linux system. It is a system file that stores user account information. That's why the file check passed!

You can check the file by running `ls -l /etc/passwd`

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-3.png)

## Variable Scope in Functions

By default, variables in Bash are **global**. Use `local` to restrict them to the function's scope.


### Example 4: Local vs Global Variables
Create `variable_scope.sh`:
```bash
#!/bin/bash

global_var="I am global"

test_scope() {
  local local_var="I am local"
  echo "Inside function: $local_var"
  echo "Inside function: $global_var"
}

test_scope

echo "Outside function: $local_var"
echo "Outside function: $global_var"
```

**Explanation:**

- Defines a **global variable** `global_var`.  
- Function `test_scope` declares a **local variable** `local_var`.  
- Inside the function, both variables are accessible.  
- Outside the function, `global_var` is accessible, but `local_var` is not.  

**Execute and run the script:**
```bash
chmod +x variable_scope.sh
./variable_scope.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-4.png)

## Scenario: Log File Processor

Managing log files is essential for maintaining system health, debugging issues, and tracking errors. This script automates log file processing by:

1. Checking if a log file exists.
2. Counting the number of errors in the log file.
3. Archiving the log file after processing.

### Script Implementation
We create a Bash script named `log_processor.sh` to perform these tasks efficiently.

### Script: `log_processor.sh`

```bash
#!/bin/bash

LOG_FILE="app.log"
ARCHIVE_DIR="logs_archive"

# Function to check if the log file exists
check_log() {
  if [ ! -f "$LOG_FILE" ]; then
    echo "Error: $LOG_FILE not found!"
    exit 1
  fi
}

# Function to count errors in the log file
process_log() {
  local error_count=$(grep -c "ERROR" "$LOG_FILE")
  echo "Number of errors: $error_count"
}

# Function to archive the log file
archive_log() {
  mkdir -p "$ARCHIVE_DIR" # Create archive directory if it doesn't exist
  local timestamp=$(date +%Y%m%d-%H%M%S)
  mv "$LOG_FILE" "$ARCHIVE_DIR/app_${timestamp}.log"
  echo "Log archived to: $ARCHIVE_DIR/app_${timestamp}.log"
}

# Main script workflow
check_log   # Step 1: Validate log file existence
process_log # Step 2: Count errors in the log file
archive_log # Step 3: Archive the log file
```

### Explanation

#### 1️⃣ Checking If the Log File Exists
**Function: `check_log`**
- Verifies if the log file (`app.log`) exists.
- If the file is missing, an error message is displayed, and the script exits.

#### 2️⃣ Processing the Log File
**Function: `process_log`**
- Uses `grep -c "ERROR"` to count occurrences of the word "ERROR" in `app.log`.
- Displays the total number of errors found.

#### 3️⃣ Archiving the Log File
**Function: `archive_log`**
- Creates an archive directory (`logs_archive`) if it does not already exist.
- Renames and moves `app.log` to `logs_archive/` with a timestamp.

### How to Use the Script

#### 1️⃣ Create a Sample Log File

Before running the script, create a sample `app.log` file with some log entries using the following command:

```bash
echo "INFO: System started
ERROR: Disk full
INFO: Backup completed
ERROR: Network timeout" > app.log
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-5.png)

#### 2️⃣ Grant Execute Permission
Make the script executable:
```bash
chmod +x log_processor.sh
```

#### 3️⃣ Run the Script
Execute the script:
```bash
./log_processor.sh
```

### Expected Output

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-6.png)

📌 **Note:** The timestamp in the archived filename will match the exact date and time the script runs.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2009/images/image-7.png)

Here we can see that the log file `app.log` has been archived to the `logs_archive` directory with a timestamp.

## Conclusion

Functions are a cornerstone of efficient Bash scripting. They promote code reuse, improve readability, and simplify debugging. By mastering argument handling, return values, and variable scope, you can build modular scripts for tasks like log processing, system monitoring, or data analysis.