# String Operations in Bash Scripting

Strings are fundamental in Bash scripting, enabling text processing, data manipulation, and dynamic output. This lab dives into essential string operations, from basic concatenation to advanced manipulation techniques, empowering you to handle text efficiently in your scripts.

By the end of this lab, you will understand:
- String declaration and interpolation
- Concatenation and length calculation
- Substring extraction and substitution
- Trimming whitespace
- Case conversion
- Splitting strings into arrays
- Checking substrings and empty strings

## Prerequisites

- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell (v4+ for some operations)

---

## Basic String Declaration and Printing

### Example: Declaring and Printing Strings
Create a script `string_basics.sh`:
```bash
#!/bin/bash

# Declare strings
str1="Bash"
str2='Scripting'
str3="Hello, World!"

# Print strings
echo "$str1 $str2"  # Output: Bash Scripting
echo "$str3"        # Output: Hello, World!
```

**Explanation:**
- Use double quotes (`" "`) or single quotes (`' '`) to define strings.
- Double quotes allow variable interpolation (e.g., `echo "$var"`), while single quotes treat text literally.

**Run the script:**
```bash
chmod +x string_basics.sh
./string_basics.sh
```

---

## String Concatenation

Combine strings using variables or literals:

### Example: Concatenation
Create `concatenate.sh`:
```bash
#!/bin/bash

first="Hello"
second="World"

# Concatenate variables
combined="$first $second"
echo "$combined"  # Output: Hello World

# Concatenate with literals
echo "Welcome to $first $second!"  # Output: Welcome to Hello World!
```

---

## String Length

Calculate the length of a string using `${#variable}`:

### Example: String Length
Create `string_length.sh`:
```bash
#!/bin/bash

str="OpenAI"
echo "Length of '$str': ${#str}"  # Output: 6
```

---

## Substring Extraction

Extract parts of a string using `${variable:start:length}`:

### Example: Substring Extraction
Create `substring.sh`:
```bash
#!/bin/bash

str="Hello World"

# Extract from index 6 (length 5)
substr="${str:6:5}"
echo "Substring: $substr"  # Output: World

# Extract from index 0 to end
echo "First 5 chars: ${str:0:5}"  # Output: Hello
```

**Syntax:**
- `${str:start:length}`: Extract `length` characters starting at `start`.

---

## String Substitution

Replace parts of a string using `${variable/pattern/replacement}`:

### Example: Substitution
Create `substitution.sh`:
```bash
#!/bin/bash

str="Bash is fun. Bash is powerful."

# Replace first occurrence of "Bash" with "Shell"
echo "${str/Bash/Shell}"  # Output: Shell is fun. Bash is powerful.

# Replace all occurrences
echo "${str//Bash/Shell}" # Output: Shell is fun. Shell is powerful.

# Replace suffix
echo "${str%.*}"          # Output: Bash is fun. Bash is powerful
```

---

## Trimming Whitespace

Remove leading/trailing whitespace using parameter expansion or `sed`:

### Example: Trimming
Create `trimming.sh`:
```bash
#!/bin/bash

str="   Trim this string   "

# Method 1: Parameter expansion (requires extglob)
shopt -s extglob
trimmed="${str##*( )}"   # Trim leading spaces
trimmed="${trimmed%%*( )}"  # Trim trailing spaces
echo "Trimmed: '$trimmed'"

# Method 2: Using sed
trimmed_sed=$(echo "$str" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
echo "Trimmed with sed: '$trimmed_sed'"
```

**Explanation:**
- Enable `extglob` for advanced pattern matching in parameter expansion.
- `sed` uses regex to strip spaces.

---

## Case Conversion

Convert string case using `${variable^^}` (uppercase) or `${variable,,}` (lowercase):

### Example: Case Conversion
Create `case_conversion.sh`:
```bash
#!/bin/bash

str="Bash Scripting"

# Convert to uppercase
echo "${str^^}"  # Output: BASH SCRIPTING

# Convert to lowercase
echo "${str,,}"  # Output: bash scripting

# Capitalize first letter
echo "${str^}"   # Output: Bash Scripting
```

---

## Splitting Strings into Arrays

Split strings using `IFS` (Internal Field Separator):

### Example: Splitting
Create `split_string.sh`:
```bash
#!/bin/bash

csv="apple,banana,grape"

# Split into array
IFS=',' read -ra fruits <<< "$csv"

echo "First fruit: ${fruits[0]}"  # Output: apple
echo "All fruits: ${fruits[@]}"   # Output: apple banana grape
```

---

## Checking Substrings and Empty Strings

### Example: Substring Check
Create `substring_check.sh`:
```bash
#!/bin/bash

str="Linux is awesome"

# Check if substring exists
if [[ "$str" == *"is"* ]]; then
  echo "Substring found!"
fi

# Check if string is empty
empty_str=""
if [[ -z "$empty_str" ]]; then
  echo "String is empty"
fi
```

---

## Best Practices

1. **Quote Variables**  
   Always use quotes (`"$var"`) to handle spaces and special characters.

2. **Use Built-in Operations**  
   Prefer Bash parameter expansion over external commands like `sed` for performance.

3. **Enable `extglob` for Advanced Patterns**  
   Use `shopt -s extglob` for complex trimming or substitutions.

4. **Leverage Arrays for Splitting**  
   Use `IFS` and `read -ra` to split strings into arrays for structured data.

---

## Conclusion

String operations are vital for text processing in Bash scripts. Whether trimming whitespace, extracting substrings, or converting cases, these techniques enhance your ability to manipulate data dynamically. Apply these skills to automate log parsing, format outputs, or process user inputs effectively.