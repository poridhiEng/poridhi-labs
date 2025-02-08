# Mastering Redirection in Bash Scripting

Redirection is an essential feature in Bash scripting that enables you to control input and output streams effectively. By mastering redirection, you can efficiently log activities, debug errors, and manage file input/output operations. This lab will guide you through different types of redirections, including standard output, standard error, combined redirection, and input redirection.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/38c4e40ccb6944c752d1d761fd18e571f65daf27/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/Redirection.svg)


By the end of this lab, you will understand:
- Input and output redirection using (>, >>, 2>, &>, <, <<)
- Suppressing output using /dev/null
- Practical examples to apply these redirections in scripts


## Prerequisites
- Basic knowledge of Linux/Unix command line
- A Linux environment or terminal with Bash shell

## What is Redirection?

Redirection allows you to control where the input comes from and where the output/errors go. This is crucial for logging, automation, and scripting. With redirection, you can redirect output to a file instead of displaying it on the terminal, or instruct an application to read input from a file rather than the keyboard. Below are the key operators:

## 1. **Standard Output (stdout) Redirection**

Standard output is the output that a command sends to the terminal. We can redirect it to a file using the `>` operator.

- **`>`**: Overwrites a file with stdout.
- **`>>`**: Appends stdout to a file.

### Overwrite with `>`

```bash
echo "Hello Poridhi" > output.txt
```

#### What Happens?

- Creates `output.txt` if it doesn't exist.
- Overwrites the file with "Hello World".

#### Check the file

```bash
cat output.txt
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image.png)

### Append with `>>`

```bash
echo "New line" >> output.txt
```

#### What Happens?

- Adds "New line" to the end of `output.txt` without deleting existing content.  

#### Check the file

```bash
cat output.txt
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-1.png)

## 2. **Standard Error (stderr) Redirection**

Standard error is the error that a command sends to the terminal. We can redirect it to a file using the `2>` operator.

- **`2>`**: Overwrites a file with stderr.
- **`2>>`**: Appends stderr to a file.

### Overwrite with `2>`

```bash
ls /non-existent-directory 2> error.log
```

#### What Happens?

- The `ls` command tries to list a non-existent directory, generating an error.
- The error message is saved to `error.log`.

#### Check the file  

```bash
cat error.log
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-2.png)

### Append with `2>>`  

```bash
ls /another-fake-dir 2>> error.log
```

#### What Happens?   

- Adds the error message to `error.log` without deleting existing content.

#### Check the file

```bash
cat error.log
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-3.png)

## 3. **Redirect Both stdout and stderr**

- **`&>`** or **`2>&1`**: Redirects both stdout and stderr to a file.
- **`&>>`** or **`2>&1 >>`**: Appends both to a file.

### Capture Everything with `&>`

```bash
ls /tmp /non-existent &> combined.log
```

#### What Happens?      

- Lists `/tmp` (success → stdout) and fails for `/non-existent` (stderr).
- Both outputs go to `combined.log`.

**Note:** the `/tmp` folder is always present in Unix/Linux systems by default. It's a standard directory created automatically by the operating system for temporary files. That's why the `ls /tmp` command will always succeed.

#### Check the file

```bash        
cat combined.log
```

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-4.png)

### Append with `&>>`

```bash
ls /tmp /non-existent &>> combined.log
```

#### What Happens?

- Adds the output to `combined.log` without deleting existing content.

#### Check the file

```bash
cat combined.log
```

## 4. **Input Redirection**

- **`<`**: Uses a file as input for a command.
- **`<<`** (Here Document): Passes multiline input to a command.

#### Feed a File with `<`

- Create input.txt

   ```bash
   echo "banana" > input.txt
   echo "apple" >> input.txt
   echo "cherry" >> input.txt
   ```

   This will create a file named `input.txt` with the fruits in it.

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-5.png)

- Sort the input.txt file

   ```bash
   sort < input.txt
   ```

   This will sort the fruits in the file.

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-6.png)

### Multi-Line Input with `<<`

```bash
cat << EOF
This is a multi-line
text block.
EOF
```

This will display the multi-line text block.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-7.png)

## 5. **Silence Output with `/dev/null`**

- **`/dev/null`** discards all data written to it. Use it to suppress unwanted output.
- It's a special file that acts as a black hole for data. 

### Suppress stdout

```bash
echo "Secret Message" > /dev/null
```

This will suppress the output of the `echo` command.

### Suppress stderr

```bash
rm non-existent-file 2> /dev/null
```

The error `rm: cannot remove 'non-existent-file'` is silenced.

### Suppress both stdout and stderr

```bash
ls /root &> /dev/null
```

If `/root` is inaccessible, both stdout and stderr are discarded. Great for `quiet mode` in scripts!

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/Bash%20Script%20Labs/Lab%2010/images/image-8.png)

We can see that both the stdout and stderr are discarded and prints nothing in the terminal.

## Conclusion

Understanding redirection in Bash scripting allows you to manage output and input efficiently. By applying these techniques, you can:

- Store logs for debugging.
- Redirect error messages to separate files.
- Use files as input sources for commands.
- Suppress unnecessary output in scripts.

By mastering redirection, you enhance automation, logging, and script reliability—making your Bash scripts more professional and efficient!