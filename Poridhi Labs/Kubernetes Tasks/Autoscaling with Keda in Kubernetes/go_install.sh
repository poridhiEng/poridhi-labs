#!/bin/bash

log() {
    echo -e "\033[1;32m$1\033[0m"
}

log "Updating system packages..."
sudo apt update && sudo apt upgrade -y

GO_VERSION="1.21.0"
GO_PACKAGE="go${GO_VERSION}.linux-amd64.tar.gz"

# Download the latest Go package
log "Downloading Go version ${GO_VERSION}..."
wget "https://go.dev/dl/${GO_PACKAGE}" -O "${GO_PACKAGE}"

# Verify download
if [[ $? -ne 0 ]]; then
    echo "Error downloading Go package. Exiting."
    exit 1
fi

# Extract the Go tarball
log "Extracting Go package..."
sudo tar -xvf "${GO_PACKAGE}" -C /usr/local

# Clean up the tarball
log "Cleaning up..."
rm -f "${GO_PACKAGE}"

# Set up Go environment variables
log "Setting up Go environment variables..."
if ! grep -q "export PATH=\$PATH:/usr/local/go/bin" ~/.profile; then
    echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.profile
fi
source ~/.profile

# Verify the installation
log "Verifying Go installation..."
go version

if [[ $? -eq 0 ]]; then
    log "Go installation completed successfully!"
else
    echo "Go installation failed. Please check the steps and try again."
    exit 1
fi
