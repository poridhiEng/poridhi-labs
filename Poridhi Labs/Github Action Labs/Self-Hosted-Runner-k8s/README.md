# Comprehensive Guide: Self-Hosted GitHub Actions Runner in Kubernetes

## Introduction

GitHub Actions is a powerful CI/CD tool that enables developers to automate workflows directly in their GitHub repositories. While GitHub provides hosted runners, these may not always suit specific needs such as cost efficiency, custom environments, or organizational compliance. Self-hosted runners allow you to control your runner environment, offering:

- Customization of tools, dependencies, or configurations.

- Enhanced security by executing workflows within your private network.

- Cost efficiency by utilizing your existing infrastructure.

## What is Self-Hosted Runner?

A self-hosted GitHub Actions runner is a machine (virtual or physical) that you configure and manage yourself to run GitHub Actions workflows. Unlike GitHub-hosted runners, which are managed by GitHub and run on shared infrastructure, self-hosted runners give you greater control over the environment, resources, and dependencies used in your workflows.

## How Self-Hosted GitHub Action Runners Work?

A self-hosted GitHub Actions runner operates as a service on a machine you configure, acting as a bridge between GitHub and your local environment to execute workflows.

**Runner Software:**

- GitHub provides runner software that can be installed on your machine.
- The runner listens for job requests from GitHub and executes them when triggered by workflows.

**Integration:**

- After installation, the runner connects to your GitHub repository or organization.
- Jobs defined in workflow YAML files are dispatched to the runner when triggered.

**Execution:**

- The runner downloads the workflow steps and executes them sequentially.
- It reports logs, statuses, and results back to GitHub.

### Why Kubernetes for Self-Hosted Runners?

**1. Scalability**

Dynamic Scaling: Kubernetes can automatically scale runners up or down based on demand using features like Horizontal Pod Autoscaling (HPA). You can increase the number of runner pods during peak activity and reduce them during low activity, saving costs and resources.

**2. High Availability**

Kubernetes ensures high availability by automatically restarting pods if they fail. Self-healing capabilities reduce downtime for workflows. Kubernetes can distribute jobs across multiple nodes, ensuring optimal utilization and no single point of failure.

**3. Resource Management**

Kubernetes allows fine-grained control over resource allocation using requests and limits for CPU and memory. This ensures that self-hosted runners don't overwhelm the cluster or underutilize resources.

### Example Use Case with Kubernetes

Imagine a GitHub repository with frequent CI/CD workflows:

1. A workflow is triggered.
2. GitHub dispatches the job to a Kubernetes-hosted runner `(runs-on: self-hosted)`.
3. Kubernetes creates a pod for the job using pre-defined configurations.
4. The pod completes the workflow, uploads artifacts to GitHub, and is then terminated.
5. Kubernetes reclaims resources, maintaining cluster efficiency.

## Prerequisites

Before you begin, ensure you have the following:

- A functional Kubernetes cluster (e.g., k3s, EKS, or kind).
- Kubernetes command-line tool (`kubectl`) installed and configured.
- Docker installed on your system for building images.
- A GitHub account with a repository.
- A GitHub Personal Access Token (PAT) with the required permissions.

## Step 1: Project Structure Setup

**1. Create a new project directory:**

```bash
mkdir github-runner-k8s
cd github-runner-k8s
```

**2. Create the necessary files:**

```bash
touch Dockerfile entrypoint.sh kubernetes.yaml
```

## Step 2: Creating the Custom runner image

Now we will create a Dockerfile that defines the container image for the self-hosted runner, including all required dependencies and configurations.

### **Base Image**
```dockerfile
FROM debian:bookworm-slim
```
**Purpose**: Specifies the base image.  

- `debian:bookworm-slim` is a lightweight version of the Debian Bookworm operating system, minimizing unnecessary components for a smaller, faster image.

### **Arguments and Environment Variables**
```dockerfile
ARG RUNNER_VERSION="2.302.1"
ENV GITHUB_PERSONAL_TOKEN ""
ENV GITHUB_OWNER ""
ENV GITHUB_REPOSITORY ""
```
**Purpose**:

- `ARG RUNNER_VERSION`: Allows setting the Actions Runner version during the build. The default is `2.302.1`.
- `ENV GITHUB_PERSONAL_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPOSITORY`: Defines environment variables for the GitHub token, repository owner, and repository name. These are placeholders that will be configured at runtime.

### **Install Docker**
```dockerfile
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg
```
**Purpose**: Updates the package list and installs essential utilities:

- `ca-certificates`: Ensures HTTPS support for secure communications.
- `curl`: Used to fetch external resources, like Docker GPG keys and GitHub Runner binaries.
- `gnupg`: For verifying digital signatures (needed for Docker key verification).

```dockerfile
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg
```
**Purpose**: Adds Docker's GPG key securely.

- Creates a directory for keyrings (`/etc/apt/keyrings`).
- Downloads and converts Docker's GPG key into a binary format (`gpg --dearmor`).
- Sets permissions for the key file to make it readable.

```dockerfile
RUN echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update
```
**Purpose**: Adds Docker’s repository to the system and updates the package list.
- Ensures `docker-ce-cli` (Docker CLI) can be installed.

```dockerfile
RUN apt-get install -y docker-ce-cli sudo jq
```
**Purpose**: This command will install:

- `docker-ce-cli`: Docker CLI for interacting with Docker containers.
- `sudo`: Allows privileged commands.
- `jq`: A lightweight tool for parsing JSON (useful for processing GitHub API responses).

### **Set Up GitHub User**
```dockerfile
RUN useradd -m github && \
    usermod -aG sudo github && \
    echo "%sudo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
```
**Purpose**:

- Creates a new user `github`.
- Adds `github` to the `sudo` group, allowing administrative tasks without a password prompt.

### **Create Directories with Correct Permissions**
```dockerfile
RUN mkdir -p /actions-runner && \
    chown -R github:github /actions-runner && \
    mkdir -p /work && \
    chown -R github:github /work
```
**Purpose**:
  - Creates required directories (`/actions-runner` for the GitHub runner and `/work` for workflow operations).
  - Sets ownership to the `github` user to avoid permission issues.

### **Switch User and Working Directory**
```dockerfile
USER github
WORKDIR /actions-runner
```
- **Purpose**:
  - Switches to the `github` user to run processes with non-root privileges.
  - Sets the working directory for subsequent commands to `/actions-runner`.

### **Download and Install GitHub Runner**
```dockerfile
RUN curl -Ls https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -o actions-runner.tar.gz && \
    tar xzf actions-runner.tar.gz && \
    rm actions-runner.tar.gz && \
    sudo ./bin/installdependencies.sh
```
**Purpose**:
  - Downloads the specified version of the GitHub Actions Runner binary.
  - Extracts the runner software to the `/actions-runner` directory.
  - Deletes the tarball to save space.
  - Installs the runner’s dependencies via `installdependencies.sh`.

### **Add Entrypoint Script**
```dockerfile
COPY --chown=github:github entrypoint.sh /actions-runner/entrypoint.sh
RUN sudo chmod u+x /actions-runner/entrypoint.sh
```
- **Purpose**:
  - Copies the `entrypoint.sh` script to the `/actions-runner` directory.
  - Makes the script executable.

### **Set Entrypoint**
```dockerfile
ENTRYPOINT ["/actions-runner/entrypoint.sh"]
```
- **Purpose**:
  - Specifies the command to be run when the container starts. The entrypoint script typically handles runner registration, job execution, and cleanup.

Here is the complete dockerfile:

```dockerfile
FROM debian:bookworm-slim
ARG RUNNER_VERSION="2.302.1"
ENV GITHUB_PERSONAL_TOKEN ""
ENV GITHUB_OWNER ""
ENV GITHUB_REPOSITORY ""

# Install Docker
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg
RUN install -m 0755 -d /etc/apt/keyrings
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
RUN chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
RUN echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
RUN apt-get update

# Install required packages
RUN apt-get install -y docker-ce-cli sudo jq

# Setup github user
RUN useradd -m github && \
    usermod -aG sudo github && \
    echo "%sudo ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Create directories with correct permissions
RUN mkdir -p /actions-runner && \
    chown -R github:github /actions-runner && \
    mkdir -p /work && \
    chown -R github:github /work

USER github
WORKDIR /actions-runner

# Download and install runner
RUN curl -Ls https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz -o actions-runner.tar.gz && \
    tar xzf actions-runner.tar.gz && \
    rm actions-runner.tar.gz && \
    sudo ./bin/installdependencies.sh

COPY --chown=github:github entrypoint.sh /actions-runner/entrypoint.sh
RUN sudo chmod u+x /actions-runner/entrypoint.sh

ENTRYPOINT ["/actions-runner/entrypoint.sh"]
```

## Step 3: Entrypoint Script

The `entrypoint.sh` script handles runner registration, execution, and cleanup. Lets create this script step by step: 

#### **1. Requesting the Runner Registration Token**
```sh
registration_url="https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPOSITORY}/actions/runners/registration-token"
echo "Requesting registration URL at '${registration_url}'"
payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PERSONAL_TOKEN}" ${registration_url})
export RUNNER_TOKEN=$(echo $payload | jq .token --raw-output)
```
**Purpose**:
  - Fetches a **registration token** from the GitHub API to register the self-hosted runner with a repository.

**How It Works**:
  1. Constructs the API URL for the repository based on `GITHUB_OWNER` and `GITHUB_REPOSITORY`.
  2. Sends a POST request to the API with the `GITHUB_PERSONAL_TOKEN` for authentication.
  3. Parses the response using `jq` to extract the `token` and assigns it to the environment variable `RUNNER_TOKEN`.

---

#### **2. Configuring the Runner**
```sh
./config.sh \
    --name $(hostname) \
    --token ${RUNNER_TOKEN} \
    --labels my-runner \
    --url https://github.com/${GITHUB_OWNER}/${GITHUB_REPOSITORY} \
    --work "/work" \
    --unattended \
    --replace
```
**Purpose**:
  - Configures the GitHub Actions runner to associate it with the repository.

**Key Flags**:
  - `--name $(hostname)`: Sets the runner's name as the container's hostname for identification in GitHub.
  - `--token ${RUNNER_TOKEN}`: Uses the registration token for authentication.
  - `--labels my-runner`: Adds a label (`my-runner`) to the runner for workflows to target specific runners.
  - `--url https://github.com/${GITHUB_OWNER}/${GITHUB_REPOSITORY}`: Specifies the repository URL for the runner.
  - `--work "/work"`: Defines the working directory where jobs will execute.
  - `--unattended`: Runs without interactive prompts.
  - `--replace`: Replaces any existing runner with the same name.

#### **3. Runner Cleanup on Exit**
```sh
remove() {
    ./config.sh remove --unattended --token "${RUNNER_TOKEN}"
}

trap 'remove; exit 130' INT
trap 'remove; exit 143' TERM
```
**Purpose**:
  - Defines a cleanup function (`remove`) that deregisters the runner from the repository.
  - Sets traps to handle signals (`INT` for Ctrl+C and `TERM` for termination signals). When the container receives these signals, the `remove` function is called to cleanly unregister the runner.

#### **4. Running the Runner Process**
```sh
./run.sh "$*" &
wait $!
```
- **Purpose**:
  - Starts the GitHub Actions runner process using `run.sh`.
  - Runs it in the background (`&`) and waits for it to complete.
  - The `wait` command ensures the script stays active, allowing the container to continue running until the runner process stops.

Here is the complete script:

```sh
#!/bin/sh
registration_url="https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPOSITORY}/actions/runners/registration-token"
echo "Requesting registration URL at '${registration_url}'"
payload=$(curl -sX POST -H "Authorization: token ${GITHUB_PERSONAL_TOKEN}" ${registration_url})
export RUNNER_TOKEN=$(echo $payload | jq .token --raw-output)

./config.sh \
    --name $(hostname) \
    --token ${RUNNER_TOKEN} \
    --labels my-runner \
    --url https://github.com/${GITHUB_OWNER}/${GITHUB_REPOSITORY} \
    --work "/work" \
    --unattended \
    --replace

remove() {
    ./config.sh remove --unattended --token "${RUNNER_TOKEN}"
}

trap 'remove; exit 130' INT
trap 'remove; exit 143' TERM

./run.sh "$*" &
wait $!
```

### Make the script executable:

```sh
chmod +x entrypoint.sh
```

## Step 4: Build the docker image

To build the docker image run the following commands:

```sh
docker build -t <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION> .
docker push <DOCKERHUB_USERNAME>/<IMAGE_NAME>:<VERSION>
```

> NOTE: Make sure to login to the dockerhub.