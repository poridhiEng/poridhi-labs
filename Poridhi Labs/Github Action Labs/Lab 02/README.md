# GitHub Actions Multiple Jobs with Dependencies

GitHub Actions is a powerful CI/CD (Continuous Integration and Continuous Deployment) tool integrated into GitHub. It allows developers to automate tasks such as building, testing, and deploying code directly from their repositories. In this lab, we will learn how to create GitHub Actions workflows with multiple jobs that depend on each other. This guide demonstrates a basic CI/CD pipeline with build, test, deploy, and notify stages.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2002/images/workflows.svg)

## Jobs in Github action

In GitHub Actions, jobs are `independent` units of work within a workflow. Each job runs in its own environment (e.g., a virtual machine or container) and can perform specific tasks, such as building an application, running tests, or deploying code. Jobs are defined under the jobs section of a workflow file.

**Key Features of Jobs:**

1. `Isolation`: Each job runs in a clean environment. For example, runs-on: ubuntu-latest provisions a fresh Ubuntu machine for the job.
2. `Parallel Execution`: Jobs without dependencies can run simultaneously, reducing overall workflow execution time.
3. `Dependencies`: Use the needs keyword to specify job dependencies, ensuring jobs run in a specific order.
4. `Steps`: Jobs consist of one or more steps, which execute commands or use actions.

## Dependent Jobs

A **dependent job** in a GitHub Actions workflow is a job that relies on the successful completion of one or more preceding jobs. The relationship between jobs is specified using the `needs` keyword. Dependent jobs are executed only after the jobs they depend on have completed successfully.

### Real-World Use Cases:

**1. CI/CD Pipelines**:

   - **Build** → Compile the source code.
   - **Test** → Run unit and integration tests after building.
   - **Deploy** → Deploy only if both build and test succeed.
   
**2. Multi-Environment Testing**:

   - **Build** → Prepare the application.
   - **Test on Ubuntu** → Run tests on an Ubuntu environment.
   - **Test on macOS** → Run tests on a macOS environment, dependent on the build.

## Prerequisites

To complete this lab, ensure you have:

- A GitHub account.
- A GitHub repository where you have write access.
- Basic understanding of YAML syntax.
- Familiarity with basic command-line operations.

## Task Description

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2002/images/lab-02-new.svg)

In this lab, you'll:

- Create a GitHub Actions workflow file.
- Configure a workflow to trigger on code pushes to the main branch.
- Learn how dependent or sequential jobs works.
- Learn how to debug workflows and troubleshoot common issues.

### Folder Structure
```
your-repository/
└── .github/
    └── workflows/
        └── multiple-jobs.yml
```

### Create Workflow Directory

Start by creating a workflow file at `.github/workflows/multiple-jobs.yml`.

```sh
mkdir -p .github/workflows
```

This command creates the `.github/workflows` directory in your repository, where workflow files are stored.


### Create Workflow File

We will create a GitHub Actions workflow with multiple jobs demonstrates how to orchestrate sequential and dependent tasks. Create a file named `multiple-jobs.yml` in the `.github/workflows` directory and fill the file with following content step by step:


```yaml
name: Multiple Jobs Lab
on:
  push:
    branches:
      - main
```

#### 1. Build Job (`build`)
**Purpose**: The `build` job is the first in the sequence and serves to simulate building the application.

```yaml
build:
  name: Build Application
  runs-on: ubuntu-latest
  steps:
    - name: Checkout code
      uses: actions/checkout@v4
    - name: Build step
      run: |
        echo "🏗️ Building the application..."
        echo "Build completed successfully!"
```

- **Steps**:
  - `actions/checkout@v4`: Checks out the repository's code.
  - Build simulation: Outputs messages about the build process.

- **Dependencies**: None (it runs independently).

---

#### 2. Test Job (`test`)
**Purpose**: Runs after the `build` job to simulate testing the application.

```yaml
test:
  name: Run Tests
  needs: build  # Depends on build job
  runs-on: ubuntu-latest
  steps:
    - name: Run tests
      run: |
        echo "🧪 Running tests..."
        echo "All tests passed!"
```

- **Dependencies**: The `needs: build` field ensures the `test` job only runs after the `build` job completes successfully.

- **Steps**:
  - Simulates running tests and outputs messages.

---

#### 3. Deploy Job (`deploy`)
**Purpose**: Deploys the application after successful build and test jobs.

```yaml
deploy:
  name: Deploy Application
  needs: [build, test]  # Depends on both build and test jobs
  runs-on: ubuntu-latest
  steps:
    - name: Deploy
      run: |
        echo "🚀 Deploying application..."
        echo "Deployment successful!"
```

- **Dependencies**: Runs after both `build` and `test` jobs complete successfully (specified using `needs: [build, test]`).

- **Steps**:
  - Simulates deployment and outputs messages about the process.

#### 4. Notify Job (`notify`)
**Purpose**: Sends a notification after the deployment.

```yaml
notify:
  name: Send Notification
  needs: deploy  # Depends on deploy job
  runs-on: ubuntu-latest
  steps:
    - name: Send notification
      run: |
        echo "📧 Sending deployment notification..."
        echo "Notification sent!"
```

- **Dependencies**: Runs only after the `deploy` job completes successfully.

- **Steps**:
  - Simulates sending a notification and outputs messages.


Here is the complete workflow file:

```yaml
name: Multiple Jobs Lab
on:
  push:
    branches:
      - main

jobs:
  # First job: Build
  build:
    name: Build Application
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Build step
        run: |
          echo "🏗️ Building the application..."
          echo "Build completed successfully!"
  
  # Second job: Test
  test:
    name: Run Tests
    needs: build  # Depends on build job
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: |
          echo "🧪 Running tests..."
          echo "All tests passed!"
  
  # Third job: Deploy
  deploy:
    name: Deploy Application
    needs: [build, test]  # Depends on both build and test jobs
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: |
          echo "🚀 Deploying application..."
          echo "Deployment successful!"

  # Fourth job: Notify
  notify:
    name: Send Notification
    needs: deploy  # Depends on deploy job
    runs-on: ubuntu-latest
    steps:
      - name: Send notification
        run: |
          echo "📧 Sending deployment notification..."
          echo "Notification sent!"
```

### Workflow Overview
The workflow, will be triggered on a `push` to the `main` branch. We will define a pipeline with four distinct jobs:

1. **Build Application** (`build` job)
2. **Run Tests** (`test` job)
3. **Deploy Application** (`deploy` job)
4. **Send Notification** (`notify` job)

Each job has dependencies and runs on an Ubuntu-based virtual environment (`ubuntu-latest`).

## Configure Github to Poridhi's VsCode

This lab is intended to run on Poridhi's Cloud. To setup remote repository to VsCode, follow these steps:

```sh
git config user.email "your email"
git config user.username "your github username"
```

Then authorize the VsCode with Github with valid credentials.

After configuring Github, save and commit and push the changes.

```sh
git add .
git commit -m "Workflow"
git push
```
Once pushed, the workflow will be automatically triggered.

## View Workflow Results

Navigate to the Actions tab in your repository to view the workflow execution details. Each step's logs show the command output, helping you understand how the workflow executed.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/Github%20Action%20Labs/Lab%2002/images/image.png)

## Practice Exercises

### Add Success/Failure Messages
Adding success messages ensures that you are informed when a job completes successfully. These messages improve the clarity and usability of workflow logs. For instance, in the build job, you can include a success message like this:

```yaml
- name: Build status
  if: success()
  run: echo "✅ Build succeeded!"
```

Similarly, you can use conditional steps to handle failures gracefully:

```yaml
- name: Handle failure
  if: failure()
  run: echo "⚠️ Build failed. Please check the logs!"
```

### Add Job Conditions
Job conditions allow you to fine-tune when specific jobs should run. For example, you might want the deploy job to run only when changes are pushed to the `main` branch:

```yaml
deploy:
  if: github.ref == 'refs/heads/main'
  needs: [build, test]
  runs-on: ubuntu-latest
  steps:
    - name: Deploy
      run: |
        echo "Deploying application to production..."
```
This ensures deployments are restricted to the main branch, reducing accidental deployments from feature branches.

### Add Environment Variables
Environment variables are useful for parameterizing workflows. For instance, in the build job, you can define and use an environment variable for the application version:

```yaml
jobs:
  build:
    env:
      BUILD_VERSION: 1.0.0
    steps:
      - run: echo "Building version $BUILD_VERSION"
```
This approach ensures consistency and makes it easier to update values across multiple jobs.

### Add Dynamic Inputs
You can make workflows dynamic by using inputs from GitHub Actions events. For example:

```yaml
steps:
  - name: Print branch name
    run: echo "The current branch is ${{ github.ref }}"
```
This outputs the branch name, which is helpful for debugging and conditional logic.

## Troubleshooting

### Common Issues
#### Job Dependencies
- Ensure job names match exactly in the `needs` field.
- Avoid circular dependencies, where jobs depend on each other.

#### Job Failures
- Check detailed logs in the "Actions" tab.
- Verify resources (e.g., tokens, permissions) and environment variables.
- Review scripts for syntax errors or missing dependencies.

#### Workflow Triggers
- Ensure branch names in the trigger match the repository's structure.
- Confirm the event type (e.g., `push`, `pull_request`) aligns with your needs.
- Validate the YAML syntax using a linter.

### Quick Fixes

#### Dependency Issues
If a job fails to find its dependencies, double-check the `needs` field:

```yaml
jobs:
  test:
    needs: build  # Must match job name exactly
```

#### Add Error Handling
Improve workflow resilience by handling failures:

```yaml
steps:
  - name: Handle errors
    if: failure()
    run: echo "Job failed!"
```

#### Check Workflow Syntax
Use tools like GitHub's built-in syntax checker or external YAML linters to identify errors.

## Tips
- Use descriptive job and step names for better visibility.
- Keep individual jobs focused on a single task to improve maintainability.
- Add meaningful status messages to guide users through the workflow.
- Use emojis to improve readability and make logs visually appealing.
- Set timeouts for long-running jobs to avoid unnecessary resource consumption.

For example:

```yaml
jobs:
  build:
    timeout-minutes: 10
    steps:
      - name: Build application
        run: echo "Building..."
```

## Conclusion

Creating workflows with multiple dependent jobs in GitHub Actions allows you to structure and automate your CI/CD pipeline effectively. By using job dependencies, you can ensure that each stage of your pipeline runs in the correct order, reducing errors and improving efficiency.