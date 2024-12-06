# Running Jenkins on Port 80: Two Different Methods

By default, Jenkins runs on port 8080 after installation. However, there are scenarios where you might want to access Jenkins on port 80 or any other port, especially in production environments where port 80 is used for HTTP traffic. This documentation will guide you through two different methods to run Jenkins on port 80.

## Methods to Run Jenkins on Port 80
1. **Using IP Table Forwarding Rule**
2. **Using Nginx as a Reverse Proxy**

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2005/images/method-diagram.png)

## Prerequisites
- Create two EC2 instances for checking both the methods.

  ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2005/images/method-02.png)

- Ensure your jenkins server is up and running in both the instances. If you do not have one, follow this lab: [Jenkins Installation on Ubuntu](https://github.com/AhnafNabil/Jenkins-Labs/tree/main/Lab%2001)

## Method 1: Running Jenkins on Port 80 Using IP Table Forwarding Rule
This method involves creating an IP table forwarding rule that redirects traffic from port 80 to Jenkins's default port 8080. This is the simplest method and doesn't require additional software.

### Steps:

1. **Create the IP Table Forwarding Rule:**

    At first, find out the network interface name of the ec2 instance.

    ```
    ip a
    ```

    ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2005/images/method-03.png)

    Now, add the correct rule using the correct interface name (`enX0`):

    ```bash
    sudo iptables -A PREROUTING -t nat -i enX0 -p tcp --dport 80 -j REDIRECT --to-port 8080
    ```

2. **Save the IP Table Rules:**

    - For RedHat-based systems:

      ```bash
      sudo iptables-save > /etc/sysconfig/iptables
      ```

    - For Ubuntu-based systems:

      ```bash
      sudo sh -c "iptables-save > /etc/iptables.rules"
      ```

Now, when you access Jenkins on port 80, the IP table rule will automatically forward the requests to port 8080.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2005/images/method-01.png)

## Method 2: Running Jenkins Behind an Nginx Reverse Proxy
Using Nginx as a reverse proxy is a more robust solution, especially for production environments. Nginx will handle incoming traffic on port 80 and forward it to Jenkins on port 8080.

### Steps:

1. **Install Nginx:**

    - For Ubuntu-based systems:

      ```bash
      sudo apt-get install nginx
      ```

2. **Configure Nginx:**

    - Open the Nginx configuration file:

      ```bash
      sudo vi /etc/nginx/nginx.conf
      ```

    - Locate the following block:

      ```nginx
      location / {
      }
      ```

    - Modify it to include the Jenkins proxy settings:

      ```nginx
      location / {
          proxy_pass http://127.0.0.1:8080;
          proxy_redirect off;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
      ```

    - Note: If Nginx is running on a different server than Jenkins, replace `127.0.0.1` with your Jenkins server's IP address.

    - If the `location /` block isn't present in the default `nginx.conf` file, you can add the necessary configuration for Jenkins by creating a new server block or modifying an existing one. Here’s how you can do it:

    - **Create a new configuration file** for Jenkins:

      ```bash
      sudo vi /etc/nginx/sites-available/jenkins
      ```

    - **Add the following configuration** to this file:

      ```nginx
      server {
          listen 80;

          server_name your_domain_or_ip;

          location / {
              proxy_pass http://127.0.0.1:8080;
              proxy_redirect off;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
      }
      ```

      Replace `your_domain_or_ip` with your server's domain name or IP address.

    - **Enable the configuration** by creating a symbolic link to the `sites-enabled` directory:

      ```bash
      sudo ln -s /etc/nginx/sites-available/jenkins /etc/nginx/sites-enabled/
      ```


3. **Restart Nginx:**

    ```bash
    sudo systemctl restart nginx
    ```

    Check the status of the nginx using:

    ```bash
    sudo systemctl status nginx
    ```

    ![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2005/images/method-05.png)

Now, Nginx will forward all requests on port 80 to Jenkins on port 8080.

![alt text](https://raw.githubusercontent.com/AhnafNabil/Jenkins-Labs/main/Lab%2005/images/method-04.png)

## Conclusion
You can choose any of the methods based on your environment and requirements. For a simple setup, the IP table forwarding rule is sufficient. In production environments, using Nginx as a reverse proxy offers more flexibility and scalability.