# Use an official Ubuntu base image
FROM ubuntu:18.04

LABEL maintainer="yasinarafat@gmail.com"

# Update package repository and install necessary packages
RUN apt-get update && \
    apt-get install -qy \
        openjdk-8-jdk \
        maven \
        openssh-server \
        git && \
    apt-get clean

# Create Jenkins user
RUN adduser --quiet jenkins && \
    echo "jenkins:jenkins" | chpasswd

# Set up SSH
RUN mkdir -p /var/run/sshd && \
    echo "jenkins:jenkins" | chpasswd

# Copy SSH authorized keys if you have them
# Uncomment and adjust the path as needed
COPY .ssh/authorized_keys /home/jenkins/.ssh/authorized_keys

# Ensure permissions are correct
RUN chown -R jenkins:jenkins /home/jenkins && \
    chmod 700 /home/jenkins/.ssh && \
    chmod 600 /home/jenkins/.ssh/authorized_keys

# Expose SSH port
EXPOSE 22

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"]
