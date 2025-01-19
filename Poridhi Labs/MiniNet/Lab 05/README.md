# Exploring ARP Fundamentals and Advanced Topologies with Mininet

This tutorial provides an interactive and practical approach to understanding the Address Resolution Protocol (ARP) using Mininet. ARP is essential for devices on a local network to discover each other's MAC addresses. Through this guide, you will observe ARP behavior and experiment with it in a controlled environment.

## Prerequisites

- A Linux system with Mininet installed.
- Basic knowledge of IP addresses and MAC addresses.

## **Task Overview**

This tutorial demonstrates the Address Resolution Protocol (ARP) in a simulated network environment using Mininet. By the end of this tutorial, you will:

1. Understand the ARP process.
2. Experiment with ARP requests and responses.
3. Analyze ARP in both basic and advanced network topologies.

## Part 1: Setting Up a Basic Topology

We will create a simple network topology with two hosts connected through a switch.

### Step 1: Create the Topology File

Create a file named `arp_topo.py` and copy the following code into it:

```python
#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

class ARPTopo(Topo):
    def build(self):
        # Add a switch
        s1 = self.addSwitch('s1')
        
        # Add two hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)

def run():
    topo = ARPTopo()
    net = Mininet(topo=topo)
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
```

This script uses Mininet to create a simple network topology with one switch and two hosts, each with a specific IP address. It starts the network, opens a CLI for testing (e.g., ping between hosts), and stops the network when done.

- **Switch**: `s1`  
- **Hosts**:  
  - `h1` with IP `10.0.0.1/24`  
  - `h2` with IP `10.0.0.2/24`  
- **Links**:  
  - Between `h1` and `s1`  
  - Between `h2` and `s1`

### Step 2: Run the Topology

1. Make the script executable by running:

   ```bash
   chmod +x arp_topo.py
   ```

2. Execute the script to start the topology:

   ```bash
   sudo python3 arp_topo.py
   ```

This will launch Mininet with the defined topology and open its CLI.

## Part 2: Understanding ARP in Action

### Basic ARP Process
When host `h1` communicates with `h2`:

1. `h1` checks its ARP cache for `h2`'s IP (10.0.0.2).
2. If not found, `h1` broadcasts an ARP request.
3. `h2` responds with its MAC address.
4. `h1` saves this mapping in its ARP cache.

### Experimenting with ARP

1. **Check the initial ARP cache**:

   In the Mininet CLI, run:

   ```bash
   h1 arp -n
   ```

   The ARP cache will be empty initially as no communication has occurred.

2. **Trigger ARP by pinging `h2`**:

   Send a ping from `h1` to `h2` to initiate ARP resolution:

   ```bash
   h1 ping -c1 10.0.0.2
   ```

   This will trigger ARP resolution, and `h2` will respond with its MAC address.

3. **View the updated ARP cache**:

   After the ping, verify that `h2`'s MAC address is now in `h1`'s ARP cache:

   ```bash
   h1 arp -n
   ```

   The output will show `h2`'s MAC address mapped to 10.0.0.2.

### Managing ARP Entries

1. **Clear the ARP cache**:

   Clear the ARP cache on `h1`:

   ```bash
   h1 ip neigh flush all
   ```

2. **Find the MAC address of `h2`**:   

   Retrieve the MAC address of `h2`:

   ```bash
   h2 ifconfig
   ```

3. **Add a static ARP entry**:

   Add a static ARP entry to `h1`:

   ```bash
   h1 arp -s 10.0.0.2 <h2-mac-address>
   ```
   Replace `<h2-mac-address>` with the actual MAC address of `h2`.

4. **Verify the static entry**:

   Check that the static ARP entry is present:

   ```bash
   h1 arp -n
   ```

   The output will show the static ARP entry for `10.0.0.2`.

## Part 3: Understanding ARP Packets

### ARP Request Packet

- **Source**: `h1`
- **Destination**: Broadcast (FF:FF:FF:FF:FF:FF)
- **Message**: "Who has IP 10.0.0.2?"
- **Broadcast by switch**: Sent to all ports except the source

### ARP Reply Packet

- **Source**: `h2`
- **Destination**: `h1`'s MAC address
- **Message**: "10.0.0.2 is at [h2's MAC address]"
- **Unicast**: Sent directly to `h1`

## Part 4: Advanced ARP Topology

To observe ARP behavior across different network segments, we will create a more complex topology.

### Setting Up the Topology

Create a Python file named `advanced_arp_topo.py` and add the following code:

```python
#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

class AdvancedARPTopo(Topo):
    def build(self):
        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Add hosts to first segment
        h1 = self.addHost('h1', ip='10.0.1.1/24')
        h2 = self.addHost('h2', ip='10.0.1.2/24')
        
        # Add hosts to second segment
        h3 = self.addHost('h3', ip='10.0.2.1/24')
        h4 = self.addHost('h4', ip='10.0.2.2/24')
        
        # Add a router
        r1 = self.addHost('r1')  # No IP set here, we'll configure interfaces manually
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, r1)
        self.addLink(s2, r1)

def run():
    topo = AdvancedARPTopo()
    net = Mininet(topo=topo)
    net.start()
    
    # Configure the router (r1)
    r1 = net.get('r1')
    r1.cmd('ifconfig r1-eth0 10.0.1.254/24')  # Interface connected to s1
    r1.cmd('ifconfig r1-eth1 10.0.2.254/24')  # Interface connected to s2
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')  # Enable IP forwarding
    
    # Configure default gateways on hosts
    net.get('h1').cmd('ip route add default via 10.0.1.254')
    net.get('h2').cmd('ip route add default via 10.0.1.254')
    net.get('h3').cmd('ip route add default via 10.0.2.254')
    net.get('h4').cmd('ip route add default via 10.0.2.254')
    
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
```

This script creates an advanced Mininet topology with the following components:  

- **2 Switches**: `s1` and `s2`  
- **4 Hosts**:  
  - `h1` and `h2` in subnet `10.0.1.0/24`, connected to `s1`  
  - `h3` and `h4` in subnet `10.0.2.0/24`, connected to `s2`  
- **1 Router**: `r1`, connected to both `s1` and `s2` for inter-subnet communication  

#### Additional Configurations

- The router (`r1`) is configured with two interfaces for the two subnets (`10.0.1.254/24` and `10.0.2.254/24`) and IP forwarding is enabled.  
- Default gateways are set on all hosts to route traffic through the router for cross-subnet communication.  

This topology allows testing communication between hosts in different subnets via the router.

### Run the Advanced Topology

1. Make the script executable:

   ```bash
   chmod +x advanced_arp_topo.py
   ```

2. Execute the script:

   ```bash
   sudo python3 advanced_arp_topo.py
   ```

This will start the advanced topology in Mininet.

### Testing the Advanced Topology

1. Test cross-segment communication:

   Ping from `h1` to `h3` to trigger ARP resolution:

   ```bash
   h1 ping -c1 10.0.2.1
   ```

2. View ARP caches:

   Check the ARP caches on `h1`, `r1`, and `h3`:

   ```bash
   h1 arp -n    # Shows router's MAC for 10.0.1.254
   r1 arp -n    # Shows MACs for hosts it communicated with
   h3 arp -n    # Shows router's MAC for 10.0.2.254
   ```

## Cleanup

1. **Exit Mininet:**

   ```bash
   mininet> exit
   ```

2. **Clean up Mininet:**

   Clean up the Mininet environment:

   ```bash
   sudo mn -c
   ```

   This will remove all Mininet-related files and processes.

## Conclusion

This tutorial provided hands-on experience with ARP in both basic and advanced network topologies using Mininet. By exploring ARP requests, replies, and cache management, you now have a solid understanding of how ARP facilitates communication in a network.


