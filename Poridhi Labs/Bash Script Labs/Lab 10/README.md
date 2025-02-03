# Redirection, Logging, and Debugging in Bash Scripting

Redirection, logging, and debugging are essential skills for creating robust and maintainable Bash scripts. In this lab, you'll learn how to control input/output streams, log script activities, and debug errors efficiently. We'll apply these concepts to a practical scenario: **automated system cleanup with error handling and logging**.

By the end of this lab, you will understand:
- **Input/output redirection** (`>`, `>>`, `2>`, `&>`, `<`, `<<`)
- Using `/dev/null` to suppress output
- Logging messages with `logger`
- Debugging scripts using `set -x` and `set -e`
- Printing script metadata (e.g., script name)

---

## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

---

## Redirection in Bash

Redirection allows you to control where the input comes from and where the output/errors go. Below are the key operators:

### 1. **Standard Output (stdout) Redirection**
- **`>`**: Overwrites a file with stdout.
- **`>>`**: Appends stdout to a file.

#### Example:
```bash
# Overwrite a file
echo "Hello World" > output.txt

# Append to a file
echo "New line" >> output.txt
```

---

### 2. **Standard Error (stderr) Redirection**
- **`2>`**: Overwrites a file with stderr.
- **`2>>`**: Appends stderr to a file.

#### Example:
```bash
# Redirect errors to a file
ls /non-existent-directory 2> error.log

# Append errors to a file
ls /another-fake-dir 2>> error.log
```

---

### 3. **Redirect Both stdout and stderr**
- **`&>`** or **`2>&1`**: Redirects both stdout and stderr to a file.
- **`&>>`** or **`2>&1 >>`**: Appends both to a file.

#### Example:
```bash
# Redirect all output to a file
ls /tmp /non-existent &> combined.log

# Append all output
echo "Test" &>> combined.log
```

---

### 4. **Input Redirection**
- **`<`**: Uses a file as input for a command.
- **`<<`** (Here Document): Passes multiline input to a command.

#### Example:
```bash
# Read input from a file
sort < input.txt

# Here Document
cat << EOF
This is a multi-line
text block.
EOF
```

---

### 5. **Redirect to `/dev/null`**
- **`/dev/null`** discards all data written to it. Use it to suppress unwanted output.

#### Example:
```bash
# Suppress stdout
echo "Secret Message" > /dev/null

# Suppress stderr
rm non-existent-file 2> /dev/null

# Suppress all output
ls /root &> /dev/null
```

---

## Printing Script Metadata

### Get the Script Name with `$0`
The variable `$0` holds the name of the script being executed.

#### Example: Print Script Name
Create `script_name.sh`:
```bash
#!/bin/bash
echo "The name of the script is: ${0}"
```

**Execute:**
```bash
chmod +x script_name.sh
./script_name.sh
# Output: The name of the script is: ./script_name.sh
```

---

## Logging with `logger`

The `logger` command writes messages to the system log (typically `/var/log/syslog` or `/var/log/messages`), making it ideal for tracking script activity.

### Example: Log Script Events
Create `logging.sh`:
```bash
#!/bin/bash

logger "Script started: ${0}"

# Simulate a task
echo "Processing data..."
sleep 2

logger "Script completed: ${0}"
```

**View Logs:**
```bash
# Check logs (Ubuntu/Debian)
tail /var/log/syslog

# Check logs (RHEL/CentOS)
tail /var/log/messages
```

---

## Debugging Scripts

### 1. **`set -x`: Enable Debug Mode**
Prints each command before execution, showing variable expansions.

#### Example: Debugging with `set -x`
Create `debug_mode.sh`:
```bash
#!/bin/bash
set -x  # Enable debugging

name="Alice"
echo "Hello, $name"

set +x  # Disable debugging
```

**Execute:**
```bash
chmod +x debug_mode.sh
./debug_mode.sh
```

---

### 2. **`set -e`: Exit on Error**
Terminates the script immediately if any command exits with a non-zero status.

#### Example: Error Handling with `set -e`
Create `exit_on_error.sh`:
```bash
#!/bin/bash
set -e  # Exit on error

# This command will fail
ls /non-existent-directory

# This line will never execute
echo "Script completed"
```

**Execute:**
```bash
chmod +x exit_on_error.sh
./exit_on_error.sh
# Output: ls: /non-existent-directory: No such file or directory
```

---

## Scenario: Automated System Cleanup

### Problem Statement
Create a script that:
1. Cleans up temporary files.
2. Logs activities to `/var/log/syslog`.
3. Ignores non-critical errors.
4. Exits on critical failures.

### Solution Code
Create `system_cleanup.sh`:
```bash
#!/bin/bash
set -e  # Exit on critical errors
set -x  # Enable debugging

LOG_FILE="cleanup.log"
TEMP_DIRS=("/tmp/*" "/var/tmp/*")

# Redirect all output to LOG_FILE and suppress non-critical errors
exec &> >(tee -a "$LOG_FILE")

logger "Starting system cleanup..."

# Delete temporary files (ignore minor errors)
for dir in "${TEMP_DIRS[@]}"; do
  rm -rf $dir || echo "Failed to clean $dir" >&2
done

logger "Cleanup completed. Log saved to: $LOG_FILE"
```

**Execute:**
```bash
chmod +x system_cleanup.sh
sudo ./system_cleanup.sh  # Requires root for /var/tmp cleanup
tail /var/log/syslog
```

---

## Best Practices

1. **Use `&>` for Combined Redirection**  
   Redirect both stdout and stderr:
   ```bash
   command &> output.log
   ```

2. **Log Strategically**  
   Use `logger` for system-level monitoring and file logging for script-specific details.

3. **Debug Conditionally**  
   Enable `set -x` only in development or for troubleshooting.

4. **Handle Errors Gracefully**  
   Use `||` to handle non-critical errors without exiting:
   ```bash
   rm file.txt || echo "File not found"
   ```

---

## Conclusion

Mastering redirection, logging, and debugging transforms your scripts into reliable, maintainable tools. By suppressing noise with `/dev/null`, tracking activities via `logger`, and enforcing error handling with `set -e`, you can automate complex tasks confidently. Apply these techniques to build resilient scripts for system administration, data processing, and beyond.