# Installing Prometheus with Binary and systemd

In this lab, we will set up Prometheus, an open-source monitoring and alerting toolkit, through the following steps:

1. **Install Prometheus**: Download the binary, set it up, and run it to access the web interface (GUI).

2. **Create a Non-root User**: Create a dedicated non-root user for enhanced security and start Prometheus with this user.

3. **Create a systemd Service**: Write a systemd service file to manage Prometheus, allowing it to start automatically on boot and simplifying service management.

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/4eb26939f981054bcdeb8c8f4ab05857fb5cca70/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/logo.svg)

## Install Prometheus with `Binary` 

### Download and Install Prometheus Binary

1. **Download Prometheus Binary:**
   - Go to the official Prometheus [download page](https://prometheus.io/download/). Copy the link to the latest release of Prometheus for Linux

      ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-1.png?raw=true)
      
   - Download the latest release of Prometheus for Linux by pasting the link we just copied after `wget` command:
     ```bash
     wget https://github.com/prometheus/prometheus/releases/download/v2.53.2/prometheus-2.53.2.linux-amd64.tar.gz
     ```

   - This command uses `wget` to download the Prometheus binary tarball from the official GitHub repository. 

2. **Extract the Tarball**:

     ```bash
     tar -xvzf prometheus-2.53.2.linux-amd64.tar.gz
     ```
     ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-3.png?raw=true)


3. **Move Prometheus Binaries to `/usr/local/bin`**:
   ```bash
   cd prometheus-2.53.2.linux-amd64
   sudo mv prometheus /usr/local/bin/
   sudo mv promtool /usr/local/bin/
   ```

4. **Set Up Prometheus Directories**:
   ```bash
   sudo mkdir /etc/prometheus
   sudo mkdir /var/lib/prometheus
   ```
5. **Move Configuration and Console Files**:
   ```bash
   sudo mv prometheus.yml /etc/prometheus/
   sudo mv consoles /etc/prometheus/
   sudo mv console_libraries /etc/prometheus/
   ```

### Start Prometheus

1. **Run Prometheus Executable**:
   ```bash
   prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus/
   ```

    - This command starts the Prometheus server. The parameters specify:
       - `--config.file`: Path to the configuration file.
       - `--storage.tsdb.path`: Path where time series data will be stored.


2. **Access the Prometheus Web Interface With Poridhi's LoadBalancer**

   - Find the `eth0` IP address for the Poridhi's VM currently you are running by using the command:

      ```bash
      ifconfig
      ```
      ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-10.png?raw=true)
    
   - Go to Poridhi's `LoadBalancer`and Create a `LoadBalancer` with the `eht0` IP and port `9090`.

      ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-11.png?raw=true)

    - By using the Provided `URL` by `LoadBalancer`, you can access the Prometheus web interface from any browser.

    -  Click on the **"Status"** tab in the top menu and select **"Targets"** in Prometheus GUI.

       ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-5.png?raw=true)
   -  You should see a target named `prometheus` with the URL 
      `http://localhost:9090/metrics`. The 
      `UP` status indicates that Prometheus 
      is successfully running and scraping metrics from itself.


## Create a Non-root User and Start Prometheus

### Create a Non-root User

1. **Create a Prometheus User**:
   ```bash
   sudo useradd --no-create-home --shell /bin/false prometheus
   ```

2. **Assign Ownership of Directories**:
   ```bash
   sudo chown -R prometheus:prometheus /etc/prometheus
   sudo chown -R prometheus:prometheus /var/lib/prometheus
   ```
### Start Prometheus with the Non-root User

1. **Run Prometheus as the Non-root User**
   ```bash
   sudo -u prometheus /usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/var/lib/prometheus/
   ```
   - By using the Generated `URL` by `LoadBalancer`, you can access the Prometheus web interface from any browser.Which clarify that Prometheus is running correctly under the non-root user.
## Create a systemd Service File for Prometheus

systemd is a system and service manager for Linux operating systems that initializes system components and manages services. Using systemd for Prometheus provides benefits like automatic service start on boot, easier service management, and better logging and monitoring of service performance.

### Write a systemd Service File

1. **Create a Prometheus Service File**:
   ```bash
   sudo vim /etc/systemd/system/prometheus.service
   ```

2. **Add the Following Configuration**:
   ```ini
   [Unit]
   Description=Prometheus Monitoring System
   Wants=network-online.target
   After=network-online.target

   [Service]
   User=prometheus
   Group=prometheus
   Type=simple
   ExecStart=/usr/local/bin/prometheus \
     --config.file=/etc/prometheus/prometheus.yml \
     --storage.tsdb.path=/var/lib/prometheus/

   [Install]
   WantedBy=multi-user.target
   ```
   - **Explanation**: 
     - `[Unit]`: General service description and dependencies.
     - `[Service]`: Defines how to run the Prometheus service.
       - `User`: Specifies the user to run the service.
       - `Group`: Specifies the group to run the service.
       - `Type`: Indicates the service type; `simple` means the service is considered started immediately after the exec command is invoked.
       - `ExecStart`: The command to start Prometheus with its configuration and data path.
     - `[Install]`: Defines how the service is installed and started.

### Start Prometheus with systemd

1. **Reload systemd Daemon**:
   ```bash
   sudo systemctl daemon-reload
   ```

2. **Enable Prometheus to Start at Boot**:

   ```bash
   sudo systemctl enable prometheus
   ```

3. **Start Prometheus Service**:
   ```bash
   sudo systemctl start prometheus
   ```

4. **Check Prometheus Service Status**:
   ```bash
   sudo systemctl status prometheus
   ```

     ![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-9.png?raw=true)

### Access the Prometheus Web Interface 

By using the Previously Generated `URL` by Poridhi's `LoadBalancer`, you can access the Prometheus web interface from any browser.Which clarify that Prometheus is running with `systemd` as a service.

![](https://github.com/poridhiEng/poridhi-labs/blob/main/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2003/images/new-8.png?raw=true)


By following these steps, you have successfully installed Prometheus, run it securely as a non-root user, and configured it to run as a systemd service. This setup provides a solid foundation for monitoring metrics in a production environment, with the flexibility to manage the service easily.


