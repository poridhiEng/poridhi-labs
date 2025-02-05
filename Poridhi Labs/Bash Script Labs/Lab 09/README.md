# Functions in Bash Scripting

Functions in Bash scripting allow you to encapsulate reusable blocks of code, making your scripts modular, organized, and easier to debug. In this lab, you'll learn how to define and use functions, pass arguments to them, and handle return values. We'll apply these concepts to a real-world scenario: **automated log file processing**.

By the end of this lab, you will understand:
- What functions are and why they are useful
- How to create and call functions
- Passing arguments to functions
- Returning values from functions
- Variable scope in functions
- Real-world use case: Log file processor

---

## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

---

## What Are Functions?

A **function** is a named block of code that performs a specific task. It can be reused multiple times within a script, eliminating code duplication and improving readability. Functions in Bash:
- Are defined before they are called.
- Can accept arguments (inputs).
- Can return values (exit statuses or output).

---

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
  echo "Hello, $1! Today is $(date)."
}

# Call the function with an argument
greet_user "Alice"
```

**Execute:**
```bash
chmod +x function_basic.sh
./function_basic.sh
# Output: Hello, Alice! Today is [current date].
```

---

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

# Call the function and capture the result
result=$(sum 10 20)
echo "Sum: $result"  # Output: Sum: 30
```

**Key Points:**
- `$1` and `$2` represent the first and second arguments passed to the function.
- Use `local` to declare variables inside functions (avoids global scope side effects).

---

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

# Call the function and check the exit status
check_file "/etc/passwd"
if [ $? -eq 0 ]; then
  echo "File check passed!"
fi
```

**Explanation:**
- `return 0` indicates success.
- `$?` captures the exit status of the last command (the function call).

---

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

echo "Outside function: $local_var"  # Output: [Empty]
echo "Outside function: $global_var" # Output: I am global
```

---

## Scenario: Log File Processor

### Problem Statement
Create a script that:
1. Checks if a log file exists.
2. Processes the log file (counts errors).
3. Archives the log file after processing.

### Solution Code
Create `log_processor.sh`:
```bash
#!/bin/bash

LOG_FILE="app.log"
ARCHIVE_DIR="logs_archive"

# Check if log file exists
check_log() {
  if [ ! -f "$LOG_FILE" ]; then
    echo "Error: $LOG_FILE not found!"
    exit 1
  fi
}

# Count errors in the log
process_log() {
  local error_count=$(grep -c "ERROR" "$LOG_FILE")
  echo "Number of errors: $error_count"
}

# Archive the log
archive_log() {
  mkdir -p "$ARCHIVE_DIR"
  local timestamp=$(date +%Y%m%d-%H%M%S)
  mv "$LOG_FILE" "$ARCHIVE_DIR/app_${timestamp}.log"
  echo "Log archived to: $ARCHIVE_DIR/app_${timestamp}.log"
}

# Main workflow
check_log
process_log
archive_log
```

### Explanation
1. **`check_log`**: Validates the existence of the log file.
2. **`process_log`**: Uses `grep` to count "ERROR" entries.
3. **`archive_log`**: Moves the log file to an archive directory with a timestamp.

**Run the Script:**
```bash
# Create a sample log file
echo "INFO: System started
ERROR: Disk full
INFO: Backup completed
ERROR: Network timeout" > app.log

chmod +x log_processor.sh
./log_processor.sh
```

**Expected Output:**
```
Number of errors: 2
Log archived to: logs_archive/app_20231015-1420.log
```

---

## Best Practices

1. **Keep Functions Small**:  
   Each function should perform a single task (e.g., `check_log`, `process_log`).

2. **Use Descriptive Names**:  
   Name functions based on their purpose (e.g., `calculate_sum`, `validate_input`).

3. **Comment Your Functions**:  
   Add comments to explain complex logic or parameters.

4. **Handle Errors**:  
   Use `return` codes to signal success/failure and validate inputs.

5. **Local Variables**:  
   Always use `local` for variables inside functions unless global scope is intentional.

---

## Conclusion

Functions are a cornerstone of efficient Bash scripting. They promote code reuse, improve readability, and simplify debugging. By mastering argument handling, return values, and variable scope, you can build modular scripts for tasks like log processing, system monitoring, or data analysis. Apply these techniques to streamline your workflows and create maintainable automation solutions.