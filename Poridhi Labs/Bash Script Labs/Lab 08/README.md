# Loops in Bash Scripting

Loops are essential for automating repetitive tasks in Bash scripts. They allow you to execute commands multiple times, process lists of data, and handle complex workflows efficiently. In this lab, you'll learn how to use different types of loops (`for`, `while`, `until`) and control statements (`break`, `continue`) to build dynamic scripts. We'll apply these concepts to a practical scenario: **Simulated Backup System with Controlled Failures**.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/ca1bf8bba5b1d4868ffbbe51d7ca7d1638bb12fd/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/Basic-loop.svg)

By the end of this lab, you will understand:
- `for` loops (basic and iterating over arrays)
- `while` and `until` loops
- Nested loops and loop control statements (`break`, `continue`)
- Real-world use case: `Simulated Backup System with Controlled Failures`
- Infinite loops and how to handle them

## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

## Types of Loops in Bash

### 1. `for` Loops
Iterate over a list of items or ranges.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/ca1bf8bba5b1d4868ffbbe51d7ca7d1638bb12fd/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/For-loop.svg)

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

This script will iterate over the list of fruits and print the fruit name.

**Execute and run the script:**
```bash
chmod +x for_basic.sh
./for_basic.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image.png)

#### Example 2: Iterate Over Array

Create `for_array.sh`:

```bash
#!/bin/bash

# Define an array
names=("Nabil" "Minhaz" "Fazlul" "Yasin")

# Loop through the array
for name in "${names[@]}"; do
  echo "Hello, $name!"
done

echo "Loop completed."
```

This script will iterate over the array of names and print the name.

**Execute and run the script:**
```bash
chmod +x for_array.sh
./for_array.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-1.png)

### 2. `while` Loops

Execute commands **while** a condition is true.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/ca1bf8bba5b1d4868ffbbe51d7ca7d1638bb12fd/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/While-loop.svg)


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

This script will count down from 5 to 1 and then print "`Liftoff! 🚀`".

**Execute and run the script:**
```bash
chmod +x while_countdown.sh
./while_countdown.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-2.png)

### 3. `until` Loops
Execute commands `until` a condition becomes true.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/ca1bf8bba5b1d4868ffbbe51d7ca7d1638bb12fd/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/Until-loop.svg)


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

#### **How It Works**
1. The script runs and starts **checking if `important.log` exists**.
2. If the file **does not exist**, it prints `"Waiting for important.log..."` and waits **2 seconds** before checking again.
3. The loop **repeats until** the file is created.
4. Once the file is found, the script prints `"important.log found! Proceeding..."` and exits.

#### **How to Test It**

1. **Run the script in one terminal:**

   ```bash
   chmod +x until_file.sh
   ./until_file.sh
   ```
2. **In another terminal, create the file after a few seconds:**

   ```bash
   touch important.log
   ```

3. **Expected Output:**

   ```bash
   Waiting for important.log...
   Waiting for important.log...
   important.log found! Proceeding...
   ```

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-3.png)

## Loop Control Statements

### `break`
Exit a loop immediately.

#### Example: `break_statement.sh`

```bash
for num in {1..10}; do
  if [ $num -eq 5 ]; then
    break
  fi
  echo "Number: $num"
done
```

This script was supposed to print the numbers from 1 to 10, but because of `break` statement, when it reaches 5, it will break the loop and exit.

**Execute and run the script:**
```bash
chmod +x break_statement.sh
./break_statement.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-4.png)

### `continue`
Skip the current iteration and proceed to the next.

#### Example: `continue_statement.sh`

```bash
for num in {1..5}; do
  if [ $num -eq 3 ]; then
    continue
  fi
  echo "Number: $num"
done
```

This script was supposed to print the numbers from 1 to 5, but because of `continue` statement, when it reaches 3, it will skip the current iteration and proceed to the next iteration.

**Execute and run the script:**
```bash
chmod +x continue_statement.sh
./continue_statement.sh
```  

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-5.png)

## Scenario: Simulated Backup System with Controlled Failures

This script describes a **simulated automated backup system** that demonstrates different failure scenarios. The system:

- **Backs up multiple directories (`docs`, `images`, `videos`).**
- **Checks available disk space before performing a backup.**
- **Retries failed backups up to 3 times before marking them as critical failures.**
- **Uses randomized conditions to simulate real-world backup challenges.**

This setup is useful for **testing and debugging** backup scripts without requiring actual large files or real disk space constraints.

### Expected Outcomes

The script is designed to **demonstrate all possible outcomes**, ensuring robust testing:

1. **Successful Backup** ✅ – The backup completes on the first attempt.
2. **Backup Fails, Then Succeeds** ⚠️✅ – The backup initially fails but succeeds after retries.
3. **Backup Fails Completely** ❌ – The backup fails after all retries.
4. **Insufficient Disk Space** 🚫 – The script detects low disk space and aborts.

### Script: `backup_system.sh`

```bash
#!/bin/bash

# Directories to back up
directories=("docs" "images" "videos")

# Backup destination
backup_dir="backups"

# Minimum free space required (in MB) - Simulated
min_space=500

# Retry failed backups up to 3 times
max_retries=3

# Create directories if they don't exist
echo "📂 Ensuring backup source directories exist..."
for dir in "${directories[@]}"; do
  mkdir -p "$dir"
  touch "$dir/sample_file.txt"  # Add a sample file to simulate content
done

echo "📁 Ensuring backup destination exists..."
mkdir -p "$backup_dir"

# Loop through directories
for dir in "${directories[@]}"; do
  retry=0

  # Simulate disk space (randomly set to low or high)
  free_space=$(( RANDOM % 1000 )) # Generates a value between 0 and 999
  echo "📦 Available disk space: $free_space MB"

  # Retry loop
  until [ $retry -ge $max_retries ]; do
    # Check disk space
    if [ $free_space -lt $min_space ]; then
      echo "❌ Insufficient disk space ($free_space MB < $min_space MB). Aborting."
      exit 1
    fi

    # Simulate backup success/failure (50% chance of failure)
    backup_success=$(( RANDOM % 2 ))

    # Generate backup filename
    timestamp=$(date +%Y%m%d-%H%M%S)
    backup_file="$backup_dir/backup_${timestamp}_${dir}.tar.gz"

    if [ $backup_success -eq 0 ]; then
      # Create an actual tar backup
      tar -czf "$backup_file" "$dir"

      echo "✅ Backup successful: $backup_file"
      break
    else
      echo "⚠️  Backup failed (attempt $((retry+1))/$max_retries)"
      ((retry++))
      sleep 2
    fi
  done

  if [ $retry -eq $max_retries ]; then
    echo "❌ Critical: Backup failed after $max_retries attempts."
  fi
done
```

### How the Script Works

### 1️⃣ **Setup Phase**
- Creates the **source directories** (`docs`, `images`, `videos`) if they do not exist.
- Adds a **sample file (`sample_file.txt`)** in each directory to simulate real content.
- Creates the **backup destination (`backups`)** if it does not exist.

### 2️⃣ **Simulating Disk Space Availability**
- A random value **between 0 and 999 MB** is assigned to **simulate available disk space**.
- If the space is **below 500 MB**, the script **aborts immediately** with an error.

### 3️⃣ **Performing Backups with Failure Simulation**
- Each directory is processed one by one.
- A **random success/failure condition** (`backup_success=$(( RANDOM % 2 ))`) determines if the backup works.
- If a failure occurs, the script **retries up to 3 times**.
- If all retries fail, it logs a **critical failure message**.
- If the backup is successful, the directory is compressed into a `.tar.gz` archive and stored in the `backups` directory. 

### Running the Script

```bash
chmod +x backup_system.sh
./backup_system.sh
```

### Expected Behaviors

**Run the script multiple times** to observe different outcomes due to the randomized conditions:

- If **disk space is insufficient**, the script exits immediately. 🚫

  ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-6.png)

- If **backup succeeds on the first attempt**, it moves to the next directory. ✅

  ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-8.png)

- If **backup fails**, it retries up to **3 times** before giving up. ⚠️❌

  ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-7.png)

## Handling Infinite Loops

Infinite loops occur when the loop's exit condition is never met, causing it to run indefinitely. While sometimes intentional (e.g., daemon processes), they are often accidental and can consume excessive system resources.

### Example 1: Accidental Infinite Loop

#### Script: `infinite_loop.sh`

```bash
#!/bin/bash
count=1

while [ $count -le 5 ]; do
  echo "Iteration: $count"
done
```

This script will run indefinitely because the loop variable `count` is never updated.

**Run the script and check:**
```bash
chmod +x infinite_loop.sh
./infinite_loop.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-9.png)

**Fix**: Update the loop variable inside the loop in the script and run again:

```bash
#!/bin/bash
count=1

while [ $count -le 5 ]; do
  echo "Iteration: $count"
  count=$((count + 1))  # Increment to eventually exit
done
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-10.png)

### Example 2: Intentional Infinite Loop with Controlled Exit

#### Script: `infinite_with_exit.sh`

```bash
#!/bin/bash

# Run until the user types "exit"
while true; do
  read -p "Enter a command (type 'exit' to quit): " cmd
  if [ "$cmd" = "exit" ]; then
    break
  else
    echo "Executing: $cmd"
  fi
done
```

This Bash script continuously prompts the user to enter a command until they type `"exit"`. Here's how it works:  

1. It runs an infinite loop (`while true`).  
2. It prompts the user to enter a command using `read -p`.  
3. If the user inputs `"exit"`, the script breaks out of the loop and stops.  
4. Otherwise, it prints `"Executing: <command>"`. Currently, the script only echoes the command instead of running it.

**Run the script and check:**

```bash
chmod +x infinite_with_exit.sh
./infinite_with_exit.sh
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2008/images/image-11.png)

## Conclusion

Loops are indispensable for automating repetitive tasks, processing data, and building resilient scripts. By mastering `for`, `while`, and `until` loops—along with control statements like `break` and `continue`—you can create efficient scripts for system administration, data processing, and more. Always test loops for exit conditions to prevent unintended infinite loops and ensure resource efficiency.