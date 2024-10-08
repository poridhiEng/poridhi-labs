#!/bin/bash

# Script to install jq, cfssl, cfssljson, kubectl, and python3.8-venv

# Function to check if a command exists
command_exists() {
  command -v "$1" &> /dev/null
}

echo "Updating package list..."
sudo apt-get update -y

# Install jq if not already installed
if command_exists jq; then
  echo "jq is already installed."
else
  echo "Installing jq..."
  sudo apt-get install jq -y
fi

# Download and install cfssl and cfssljson if not already installed
if command_exists cfssl && command_exists cfssljson; then
  echo "cfssl and cfssljson are already installed."
else
  echo "Installing cfssl and cfssljson..."
  wget -q --show-progress --https-only --timestamping \
    https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 \
    https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64

  chmod +x cfssl_linux-amd64 cfssljson_linux-amd64

  sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
  sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssljson
  echo "cfssl and cfssljson installed successfully."
fi

# Download and install kubectl if not already installed
if command_exists kubectl; then
  echo "kubectl is already installed."
else
  echo "Installing kubectl..."
  curl -LO "https://dl.k8s.io/release/v1.21.0/bin/linux/amd64/kubectl"
  chmod +x ./kubectl
  sudo mv ./kubectl /usr/local/bin/kubectl
  echo "kubectl installed successfully."
fi

# Install python3.8-venv if not already installed
if command_exists python3.8 && python3.8 -m venv --help &> /dev/null; then
  echo "python3.8-venv is already installed."
else
  echo "Installing python3.8-venv..."
  sudo apt-get install python3.8-venv -y
  echo "python3.8-venv installed successfully."
fi

echo "All tools installed successfully!"
