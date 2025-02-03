# Conditional Statements in Bash Scripting

Conditional statements are the backbone of decision-making in Bash scripts. They allow your scripts to execute different commands based on specific conditions, enabling dynamic and responsive automation. In this lab, you'll learn the syntax of conditional statements and apply them to a real-world scenario: a **system health monitoring script**.

By the end of this lab, you will understand:
- Syntax of `if`, `elif`, and `else` statements
- Numeric, string, and file comparisons
- Logical operators (`AND`, `OR`, `NOT`)
- Real-world use case: System health monitoring

---

## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

---

## Syntax of Conditional Statements

### Basic Structure
```bash
if [ condition ]; then
  # Commands if condition is true
elif [ another_condition ]; then
  # Commands if another_condition is true
else
  # Commands if all conditions are false
fi
```

### Comparison Operators
| **Type**       | **Operator** | **Description**                     |
|----------------|--------------|-------------------------------------|
| **Numeric**    | `-eq`        | Equal to                            |
|                | `-ne`        | Not equal to                        |
|                | `-lt`        | Less than                           |
|                | `-gt`        | Greater than                        |
|                | `-le`        | Less than or equal to               |
|                | `-ge`        | Greater than or equal to            |
| **String**     | `=`          | Equal                               |
|                | `!=`         | Not equal                           |
|                | `-z`         | String is empty                     |
| **File Tests** | `-f`         | File exists                         |
|                | `-d`         | Directory exists                    |
|                | `-r`         | File is readable                    |

### Logical Operators
- `&&` (AND): `if [ condition1 ] && [ condition2 ]; then`
- `||` (OR): `if [ condition1 ] || [ condition2 ]; then`
- `!` (NOT): `if ! [ condition ]; then`

---

## Scenario: System Health Monitoring

### Problem Statement
You need to create a script that checks critical system resources (CPU, memory, and disk usage). If any resource exceeds a safe threshold, the script should alert the user.

### Solution Code
Create a file `system_health.sh`:
```bash
#!/bin/bash

# Thresholds (adjust as needed)
CPU_THRESHOLD=80    # 80% CPU usage
MEM_THRESHOLD=80    # 80% memory usage
DISK_THRESHOLD=80   # 80% disk usage

# Get current usage values (simulated for this example)
cpu_usage=85
mem_usage=75
disk_usage=90

# Check CPU usage
if [ "$cpu_usage" -gt "$CPU_THRESHOLD" ]; then
  echo "⚠️  CPU usage is HIGH: $cpu_usage% (Threshold: $CPU_THRESHOLD%)"
else
  echo "✅ CPU usage is OK: $cpu_usage%"
fi

# Check Memory usage
if [ "$mem_usage" -gt "$MEM_THRESHOLD" ]; then
  echo "⚠️  Memory usage is HIGH: $mem_usage% (Threshold: $MEM_THRESHOLD%)"
else
  echo "✅ Memory usage is OK: $mem_usage%"
fi

# Check Disk usage
if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
  echo "⚠️  Disk usage is HIGH: $disk_usage% (Threshold: $DISK_THRESHOLD%)"
else
  echo "✅ Disk usage is OK: $disk_usage%"
fi
```

### Explanation
1. **Thresholds**: Define safe limits for CPU, memory, and disk usage.
2. **Simulated Data**: For simplicity, hardcode usage values (`cpu_usage=85`, etc.). In a real script, you'd fetch these dynamically.
3. **Condition Checks**:
   - `if [ "$cpu_usage" -gt "$CPU_THRESHOLD" ]`: Checks if CPU usage exceeds the threshold using `-gt` (greater than).
   - Similar logic applies to memory and disk checks.

### Run the Script
```bash
chmod +x system_health.sh
./system_health.sh
```

---

## Advanced Examples

### 1. Combining Conditions with Logical Operators
Check if **both** CPU and memory are overloaded:
```bash
if [ "$cpu_usage" -gt "$CPU_THRESHOLD" ] && [ "$mem_usage" -gt "$MEM_THRESHOLD" ]; then
  echo "‼️  CRITICAL: Both CPU and memory are overloaded!"
fi
```

### 2. File Existence Check
Verify if a log file exists before processing:
```bash
LOG_FILE="/var/log/app.log"
if [ -f "$LOG_FILE" ]; then
  echo "Processing $LOG_FILE..."
else
  echo "Error: $LOG_FILE not found!"
fi
```

### 3. Case Statements for Multiple Conditions
Create a menu-driven script:
```bash
#!/bin/bash
echo "1) Start Service"
echo "2) Stop Service"
read -p "Choose an option: " choice

case "$choice" in
  1) echo "Starting service..." ;;
  2) echo "Stopping service..." ;;
  *) echo "Invalid option!" ;;
esac
```

---

## Best Practices
1. **Quote Variables**: Always use `"$variable"` to handle spaces in values.
   ```bash
   if [ "$cpu_usage" -gt 80 ]; then
   ```
2. **Prefer `[[ ]]` Over `[ ]`**:  
   `[[ ]]` supports advanced features like pattern matching:
   ```bash
   if [[ "$filename" == *.log ]]; then
   ```
3. **Indent Code**: Improve readability with indentation:
   ```bash
   if [ condition ]; then
       echo "Condition met"
   fi
   ```

---

## Conclusion

Conditional statements empower your scripts to make intelligent decisions, adapting to different scenarios dynamically. By mastering `if`/`else`, logical operators, and real-world use cases like system monitoring, you can build robust automation tools that respond effectively to changing conditions.