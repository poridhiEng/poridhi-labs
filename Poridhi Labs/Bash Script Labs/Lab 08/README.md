# Loops in Bash Scripting

Loops are essential for automating repetitive tasks in Bash scripts. They allow you to execute commands multiple times, process lists of data, and handle complex workflows efficiently. In this lab, you'll learn how to use different types of loops (`for`, `while`, `until`) and control statements (`break`, `continue`) to build dynamic scripts. We'll apply these concepts to a practical scenario: **automated directory backups with error handling**.

By the end of this lab, you will understand:
- `for` loops (basic, C-style, and iterating over arrays/files)
- `while` and `until` loops
- Nested loops and loop control statements (`break`, `continue`)
- Real-world use case: Automated backup system
- Infinite loops and how to handle them

---

## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

---

## Types of Loops in Bash

### 1. `for` Loops
Iterate over a list of items or ranges.

#### Syntax:
```bash
for item in list; do
  # Commands
done
```

#### Example 1: Basic `for` Loop
Create `for_basic.sh`:
```bash
#!/bin/bash

# Iterate over a list of fruits
for fruit in Apple Banana Orange; do
  echo "Processing $fruit..."
done
```

**Execute:**
```bash
chmod +x for_basic.sh
./for_basic.sh
```

#### Example 2: Iterate Over Files
Create `for_files.sh`:
```bash
#!/bin/bash

# Backup all .txt files in the current directory
for file in *.txt; do
  cp "$file" "backup_$file"
  echo "Backed up: $file → backup_$file"
done
```

---

### 2. `while` Loops
Execute commands **while** a condition is true.

#### Syntax:
```bash
while [ condition ]; do
  # Commands
done
```

#### Example: Countdown Timer
Create `while_countdown.sh`:
```bash
#!/bin/bash

count=5

while [ $count -gt 0 ]; do
  echo "Countdown: $count"
  sleep 1
  ((count--))
done

echo "Liftoff! 🚀"
```

**Execute:**
```bash
chmod +x while_countdown.sh
./while_countdown.sh
```

---

### 3. `until` Loops
Execute commands **until** a condition becomes true.

#### Syntax:
```bash
until [ condition ]; do
  # Commands
done
```

#### Example: Wait for File Creation
Create `until_file.sh`:
```bash
#!/bin/bash

file="important.log"

# Wait until the file is created
until [ -f "$file" ]; do
  echo "Waiting for $file..."
  sleep 2
done

echo "$file found! Proceeding..."
```

---

## Scenario: Automated Backup System

### Problem Statement
Create a script that:
1. Backs up specified directories using `tar`.
2. Checks for sufficient disk space before backing up.
3. Retries failed backups up to 3 times.

### Solution Code
Create `backup_system.sh`:
```bash
#!/bin/bash

# Directories to back up (modify as needed)
directories=("/home/user/docs" "/home/user/images")

# Backup destination
backup_dir="/backups"

# Minimum free space required (in MB)
min_space=500

# Retry failed backups up to 3 times
max_retries=3

# Loop through directories
for dir in "${directories[@]}"; do
  retry=0

  # Retry loop
  until [ $retry -ge $max_retries ]; do
    # Check disk space
    free_space=$(df -m "$backup_dir" | awk 'NR==2 {print $4}')
    if [ $free_space -lt $min_space ]; then
      echo "❌ Insufficient disk space ($free_space MB < $min_space MB). Aborting."
      exit 1
    fi

    # Create backup
    timestamp=$(date +%Y%m%d-%H%M%S)
    backup_file="$backup_dir/backup_${timestamp}_$(basename $dir).tar.gz"
    tar -czf "$backup_file" "$dir" 2>/dev/null

    # Check if backup succeeded
    if [ $? -eq 0 ]; then
      echo "✅ Backup successful: $backup_file"
      break
    else
      echo "⚠️  Backup failed (attempt $((retry+1))/$max_retries)"
      ((retry++))
      sleep 5
    fi
  done

  if [ $retry -eq $max_retries ]; then
    echo "❌ Critical: Backup failed after $max_retries attempts."
  fi
done
```

### Explanation
1. **`for` Loop**: Iterates over directories to back up.
2. **`until` Loop**: Retries failed backups up to 3 times.
3. **`while` Logic (Implicit)**: Checks disk space before each backup.
4. **Error Handling**: Uses exit codes (`$?`) to verify command success.

**Run the Script:**
```bash
chmod +x backup_system.sh
sudo mkdir /backups  # Create backup directory if needed
./backup_system.sh
```

---

## Loop Control Statements

### 1. `break`
Exit a loop immediately.

#### Example:
```bash
for num in {1..10}; do
  if [ $num -eq 5 ]; then
    break
  fi
  echo "Number: $num"
done
# Output: 1 2 3 4
```

### 2. `continue`
Skip the current iteration and proceed to the next.

#### Example:
```bash
for num in {1..5}; do
  if [ $num -eq 3 ]; then
    continue
  fi
  echo "Number: $num"
done
# Output: 1 2 4 5
```

---

## Handling Infinite Loops

Infinite loops occur when the loop's exit condition is never met, causing it to run indefinitely. While sometimes intentional (e.g., daemon processes), they are often accidental and can consume excessive system resources.

### Example 1: Accidental Infinite Loop
```bash
#!/bin/bash
count=1

# This loop will run forever because "count" is never updated
while [ $count -le 5 ]; do
  echo "Iteration: $count"
  # Forgot to increment count: count=$((count + 1))
done
```

**Fix**: Update the loop variable inside the loop:
```bash
count=1
while [ $count -le 5 ]; do
  echo "Iteration: $count"
  count=$((count + 1))  # Increment to eventually exit
done
```

### Example 2: Intentional Infinite Loop with Controlled Exit
```bash
#!/bin/bash

# Run until the user types "exit"
while true; do
  read -p "Enter a command (type 'exit' to quit): " cmd
  if [ "$cmd" = "exit" ]; then
    break
  else
    echo "Executing: $cmd"
    # Add command execution logic here
  fi
done
```

### Best Practices to Avoid/Handle Infinite Loops
1. **Test Exit Conditions**:  
   Ensure the loop variable or condition is updated within the loop.
   ```bash
   while [ $count -le 10 ]; do
     # ... logic ...
     ((count++))  # Update the variable
   done
   ```

2. **Use Timeouts**:  
   Limit loop execution time using the `timeout` command:
   ```bash
   timeout 10s ./infinite_script.sh  # Terminate after 10 seconds
   ```

3. **Add `sleep` Commands**:  
   For intentional infinite loops (e.g., monitoring), add delays to reduce CPU usage:
   ```bash
   while true; do
     echo "Monitoring..."
     sleep 5  # Pause for 5 seconds
   done
   ```

4. **Leverage `break` Statements**:  
   Provide clear exit conditions within the loop body.

---

## Best Practices

1. **Avoid Infinite Loops**:  
   - Always test exit conditions.
   - Use `break` or update loop variables to terminate loops.

2. **Use `$(command)` for Dynamic Lists**:  
   Generate lists dynamically for `for` loops.
   ```bash
   for user in $(cat users.txt); do
     echo "Processing $user"
   done
   ```

3. **Prefer `for` Over `while` for Known Iterations**:  
   Use `for` when iterating over a known list of items.

4. **Indent Code**:  
   Improve readability with consistent indentation.
   ```bash
   for item in list; do
       echo "Processing $item"
   done
   ```

---

## Conclusion

Loops are indispensable for automating repetitive tasks, processing data, and building resilient scripts. By mastering `for`, `while`, and `until` loops—along with control statements like `break` and `continue`—you can create efficient scripts for system administration, data processing, and more. Apply these techniques to streamline workflows and handle complex conditions with ease. Always test loops for exit conditions to prevent unintended infinite loops and ensure resource efficiency.