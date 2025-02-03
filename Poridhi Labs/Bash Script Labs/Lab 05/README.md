# Arrays in Bash Scripting

Arrays in Bash scripting allow you to store multiple values in a single variable, making it easier to manage lists and collections of data. In this lab, you'll learn how to declare, manipulate, and iterate over arrays, as well as explore practical use cases to enhance your scripting skills.

By the end of this lab, you will understand:
- Declaring and initializing arrays
- Accessing array elements
- Modifying arrays (adding, removing, updating)
- Iterating through arrays
- Using associative arrays (Bash 4+)
- Practical use cases for arrays

## Prerequisites

- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell (v4+ for associative arrays)

---

## Declaring and Initializing Arrays

Arrays can store multiple values under a single variable name. Here’s how to declare them:

### Example: Basic Array Declaration
Create a script `array_basics.sh`:
```bash
#!/bin/bash

# Declare an array of fruits
fruits=("Apple" "Banana" "Orange" "Grape")

# Print all elements
echo "All fruits: ${fruits[@]}"

# Declare an array with spaces/newlines
books=(
  "1984"
  "Brave New World"
  "Fahrenheit 451"
)
echo "Books: ${books[@]}"
```

**Execute the script:**
```bash
chmod +x array_basics.sh
./array_basics.sh
```

---

## Accessing Array Elements

Access elements using indices (starting at 0):

### Example: Indexing and Properties
Create `access_elements.sh`:
```bash
#!/bin/bash

colors=("Red" "Green" "Blue")

echo "First color: ${colors[0]}"        # Output: Red
echo "All elements: ${colors[@]}"       # Output: Red Green Blue
echo "Indices: ${!colors[@]}"           # Output: 0 1 2
echo "Number of elements: ${#colors[@]}" # Output: 3
```

**Key Syntax:**
- **`${array[index]}`** → Access element at `index`.
- **`${!array[@]}`** → List all indices.
- **`${#array[@]}`** → Count elements.

---

## Modifying Arrays

Add, update, or remove elements dynamically:

### Example: Appending and Removing Elements
Create `modify_array.sh`:
```bash
#!/bin/bash

languages=("Bash" "Python")

# Append elements
languages+=("JavaScript" "Java")

# Update an element
languages[2]="Ruby"

# Remove the third element (index 2)
unset languages[2]

echo "Updated languages: ${languages[@]}"
# Output: Bash Python Java
```

**Note:** `unset` removes elements, which may create gaps (sparse arrays).

---

## Iterating Over Arrays

Loop through arrays using `for` loops:

### Example: Iteration Methods
Create `iterate_array.sh`:
```bash
#!/bin/bash

teams=("Developers" "Designers" "QA" "DevOps")

# Loop with indices
for i in "${!teams[@]}"; do
  echo "Team $i: ${teams[$i]}"
done

# Loop through elements directly
for team in "${teams[@]}"; do
  echo "Processing $team..."
done
```

---

## Associative Arrays (Bash 4+)

Associative arrays use key-value pairs for structured data:

### Example: Key-Value Storage
Create `associative_array.sh`:
```bash
#!/bin/bash

declare -A user_roles  # Declare associative array
user_roles=(
  ["alice"]="admin"
  ["bob"]="developer"
  ["eve"]="guest"
)

echo "Alice's role: ${user_roles["alice"]}"  # Output: admin
echo "All users: ${!user_roles[@]}"          # Output: alice bob eve
echo "All roles: ${user_roles[@]}"           # Output: admin developer guest
```

**Note:** Requires Bash version 4+. Check your version with `bash --version`.

---

## Use Cases

### 1. Processing Command-Line Arguments
Store arguments in an array for flexible handling:
```bash
#!/bin/bash
args=("$@")  # Capture all arguments
echo "First argument: ${args[0]}"
echo "All arguments: ${args[@]}"
```

### 2. Reading Files into Arrays
Use `mapfile` to read a file line-by-line into an array:
```bash
#!/bin/bash
mapfile -t lines < "input.txt"  # Read file into array "lines"
for line in "${lines[@]}"; do
  echo "Processing: $line"
done
```

### 3. Managing Multiple Values
Filter even numbers from a list:
```bash
#!/bin/bash
numbers=(10 15 20 25 30)
evens=()
for num in "${numbers[@]}"; do
  if (( num % 2 == 0 )); then
    evens+=("$num")
  fi
done
echo "Even numbers: ${evens[@]}"  # Output: 10 20 30
```

---

## Best Practices

1. **Quote Array Expansions**  
   Always use `"${array[@]}"` to preserve spaces in elements.  
   Example: `for item in "${array[@]}"; do`.

2. **Avoid Sparse Arrays**  
   Gaps from `unset` can complicate iterations. Consider rebuilding the array if needed:
   ```bash
   array=("${array[@]}")  # Re-index
   ```

3. **Use `declare -a` for Clarity**  
   Explicitly declare arrays for better readability:
   ```bash
   declare -a my_array=("item1" "item2")
   ```

4. **Prefer Associative Arrays for Key-Value Data**  
   Use them for structured data instead of parallel arrays.

---

## Conclusion

Arrays are indispensable for managing collections of data in Bash scripts. Whether you're handling command-line arguments, processing files, or organizing key-value pairs, arrays provide the flexibility needed for advanced scripting. Practice these examples to streamline your automation tasks and build more dynamic scripts.