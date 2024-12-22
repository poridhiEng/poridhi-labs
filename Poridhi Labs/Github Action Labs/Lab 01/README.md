# Introduction to GitHub Actions

GitHub Actions is a powerful tool for automating workflows directly within your GitHub repositories. This hands-on lab provides a beginner-friendly introduction to GitHub Actions, guiding you through creating a basic workflow. You'll learn how to execute commands, check out repository code, and view workflow results.

![](./images/lab11.svg)

Imagine you want to automate routine tasks like running tests, building your code, or deploying your application whenever you push changes to your repository. GitHub Actions can simplify this by automating workflows triggered by specific events like code pushes or pull requests.

### What is a Runner?

A runner is a server that executes the commands defined in your GitHub Actions workflows. It provides the environment for running jobs, which can be configured to meet specific requirements.

### Types of Runners

1. **GitHub-Hosted Runners:** These are virtual machines provided and maintained by GitHub. They are preconfigured with tools and environments for most workflows and are a great choice for general automation tasks.

2. **Self-Hosted Runners:** These are servers you configure and manage yourself. They allow for more control and customization, such as using specialized hardware or accessing private resources.

This lab focuses on a basic workflow that demonstrates how to:
- Clone a repository onto a GitHub-hosted runner.
- Execute single and multi-line commands.
- Display system and software information.

## Prerequisites

To complete this lab, ensure you have:
1. A GitHub account.
2. A GitHub repository where you have write access.
3. Basic understanding of YAML syntax.
4. Familiarity with basic command-line operations.

## Task Description

![](./images/lab1.svg)

In this lab, you'll:
1. Create a GitHub Actions workflow file.
2. Configure a workflow to trigger on code pushes to the `main` branch.
3. Execute commands to list files, display system information, and check software versions.
4. Learn how to debug workflows and troubleshoot common issues.

## Project Structure

The lab creates the following structure within your repository:

```
├── .github/
│   └── workflows/
│       └── basic-checkout.yml
└── README.md
```

## Step 1: Create Workflow Directory

Start by creating the necessary directory structure for GitHub Actions workflows.

```bash
mkdir -p .github/workflows
```

This command creates the `.github/workflows` directory in your repository, where workflow files are stored.



## Step 2: Create Workflow File

Create a file named `basic-checkout.yml` in the `.github/workflows` directory with the following content:

```yaml
name: Basic Checkout Lab

# Trigger workflow on push to the main branch
on:
  push:
    branches:
      - main

jobs:
  basic-checkout:
    runs-on: ubuntu-latest
    steps:
      # Step 1: Checkout the repository
      - name: Checkout repository
        uses: actions/checkout@v4

      # Step 2: List repository contents
      - name: List files
        run: ls -la

      # Step 3: Display system information
      - name: Show system info
        run: |
          echo "Repository: $GITHUB_REPOSITORY"
          echo "Operating System: $(uname -a)"
          echo "Current Directory: $(pwd)"

      # Step 4: Check software versions
      - name: Check versions
        run: |
          echo "Node version: $(node --version)"
          echo "Python version: $(python --version)"
          echo "Git version: $(git --version)"
```

- **Trigger Condition**: The workflow runs on a `push` event to the `main` branch.
- **Runner**: The workflow uses `ubuntu-latest` as the runner (a virtual machine provided by GitHub).
- **Steps**:
  - **Checkout Repository**: Clones the repository onto the runner.
  - **List Files**: Lists all files, including hidden ones.
  - **System Information**: Displays repository details, operating system, and current directory.
  - **Version Checks**: Shows the versions of Node.js, Python, and Git installed on the runner.



## Step 3: Push Workflow File to Repository








To push code from a remote VS Code server to a GitHub repository using SSH, follow these steps:



### **1. Generate an SSH Key**
1. Open the terminal in your remote VS Code server.
2. Run the following command to generate a new SSH key pair:
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```
   - If prompted, specify a file location (default is `~/.ssh/id_ed25519`) or press Enter to accept the default.
   - Set a passphrase (recommended) or press Enter to skip.

3. Confirm the SSH key was created:
   ```bash
   ls ~/.ssh/
   ```
   You should see files like `id_ed25519` (private key) and `id_ed25519.pub` (public key).




### **2. Add the SSH Key to Your GitHub Account**
1. Display the public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy the output.

2. Open [GitHub SSH settings](https://github.com/settings/keys).

3. Click **"New SSH Key"**, provide a descriptive title (e.g., "Remote VS Code"), and paste the public key.

4. Click **"Add SSH Key"**.



### **3. Setup githubs default account**

```
git config --global user.email "minhaz.jisun@gmail.com"
git config --global user.name "Your Name"
```


### **4. Configure the Remote Repository in Git**
1. Navigate to your project directory in the terminal:
   ```bash
   cd /path/to/your/project
   ```

2. Initialize a Git repository if not already done:
   ```bash
   git init
   ```

3. Add the GitHub repository as a remote:
   ```bash
   git remote add origin git@github.com:<username>/<repository>.git
   ```

4. Verify the remote URL:
   ```bash
   git remote -v
   ```



### **6. Push Code to GitHub**
1. Stage and commit your changes:
   ```bash
   git add .
   git commit -m "Initial commit"
   ```

2. Push the code to the repository:
   ```bash
   git push -u origin main
   ```
   Replace `main` with the default branch name if different.



You are now set up to use SSH with GitHub from your remote VS Code server!















Commit and push the `basic-checkout.yml` file to the `main` branch:

```bash
git add .github/workflows/basic-checkout.yml
git commit -m "Add basic GitHub Actions workflow"
git push origin main
```

Once pushed, the workflow automatically runs.



## Step 4: View Workflow Results

Navigate to the **Actions** tab in your repository to view the workflow execution details. Each step's logs show the command output, helping you understand how the workflow executed.

![alt text](./images/image.png)

![alt text](./images/image-1.png)

#### Outputs

![alt text](./images/image-2.png)

![alt text](./images/image-3.png)

![alt text](./images/image-4.png)

![alt text](./images/image-5.png)


## Detailed Breakdown of Steps

### 1. Checkout Repository

```yaml
- name: Checkout repository
  uses: actions/checkout@v4
```

**Purpose**: Clones the repository onto the runner. This step ensures access to the repository's files for subsequent steps.



### 2. List Files

```yaml
- name: List files
  run: ls -la
```

**Purpose**: Lists all files in the repository directory, including hidden ones. Outputs file permissions, ownership, and sizes.



### 3. Display System Information

```yaml
- name: Show system info
  run: |
    echo "Repository: $GITHUB_REPOSITORY"
    echo "Operating System: $(uname -a)"
    echo "Current Directory: $(pwd)"
```

**Purpose**:
- Demonstrates using environment variables (e.g., `$GITHUB_REPOSITORY`).
- Displays system information using Linux commands (`uname`, `pwd`).



### 4. Check Software Versions

```yaml
- name: Check versions
  run: |
    echo "Node version: $(node --version)"
    echo "Python version: $(python --version)"
    echo "Git version: $(git --version)"
```

**Purpose**: Verifies the versions of Node.js, Python, and Git installed on the runner. Uses command substitution to insert command output into `echo` statements.



# Practice Exercises

### 1. Add New Commands
Modify the workflow to include:
- Current date and time:
  ```bash
  date
  ```
- Available disk space:
  ```bash
  df -h
  ```
- Memory usage:
  ```bash
  free -m
  ```

### 2. Custom Environment Variables
Add a custom environment variable to the job:

```yaml
env:
  CUSTOM_MESSAGE: "Hello from GitHub Actions!"
```

Print the variable:
```yaml
- name: Display custom message
  run: echo "$CUSTOM_MESSAGE"
```

### 3. Conditional Execution
Add a step that runs only if the workflow is triggered by a push event:

```yaml
- name: Conditional step
  if: github.event_name == 'push'
  run: echo "This was triggered by a push event"
```



## Troubleshooting

### Common Issues
1. **Workflow Not Triggering**:
   - Ensure the branch name matches the trigger condition.
   - Verify workflow file syntax.
   - Check repository settings to ensure GitHub Actions is enabled.

2. **Checkout Action Fails**:
   - Check Git configuration:
     ```bash
     git config --global --list
     ```
   - Verify repository permissions.

3. **Command Execution Errors**:
   - Ensure commands are available on the runner.
   - Verify syntax for multi-line commands.
   - Check environment variable usage.

### Debugging Tips
- Enable debug logging by setting the `ACTIONS_RUNNER_DEBUG` secret to `true`.
- Use `echo` statements to debug variables.
- Check workflow logs in the **Actions** tab.

