# Understanding ARP with Mininet: A Hands-on Tutorial

This tutorial provides a hands-on approach to understanding the Address Resolution Protocol (ARP) using Mininet. You will learn how devices discover each other's MAC addresses on a local network and observe ARP behavior through practical experiments.

---

## Prerequisites

1. **System Requirements:**
   - Linux system with Mininet installed.
   - Root access or sudo privileges.

2. **Knowledge Requirements:**
   - Basic understanding of networking concepts (IP, MAC addresses, ARP).
   - Familiarity with tools like Wireshark or tcpdump for packet capture.

---

## Part 1: Basic Setup

### Step 1: Create a Simple Topology

We will create a simple topology with two hosts connected through a switch. Follow these steps:

1. **Create the topology file:**
   Save the following Python code in a file named `arp_topo.py`:

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

2. **Run the topology:**

```bash
# Make the script executable
chmod +x arp_topo.py

# Run the topology
sudo python arp_topo.py
```

---

## Part 2: ARP Experiments

### Experiment 1: Observe Initial ARP Tables

1. **Check the ARP cache on `h1`:**
   
   ```bash
   mininet> h1 arp -n
   ```
   The ARP cache will initially be empty.

2. **Find the MAC addresses of the hosts:**

   ```bash
   mininet> h1 ifconfig
   mininet> h2 ifconfig
   ```
   Note down the MAC addresses for reference.

### Experiment 2: Trigger and Observe ARP

1. **Capture ARP packets on `h1`:**

   ```bash
   mininet> h1 tcpdump -i h1-eth0 arp -w /tmp/arp.pcap
   ```

2. **Trigger ARP by pinging `h2`:**

   ```bash
   mininet> h1 ping -c1 10.0.0.2
   ```

3. **Check the updated ARP cache on `h1`:**

   ```bash
   mininet> h1 arp -n
   ```
   You should now see `h2`'s MAC address in the cache.

### Experiment 3: Manipulate ARP Entries

1. **Clear the ARP cache:**

   ```bash
   mininet> h1 ip neigh flush all
   ```

2. **Add a static ARP entry:**

   ```bash
   mininet> h1 arp -s 10.0.0.2 <h2-mac-address>
   ```

3. **Verify the static entry:**

   ```bash
   mininet> h1 arp -n
   ```

---

## Part 3: Advanced ARP Topology

To explore ARP behavior across network segments, we will create a more complex topology.

### Step 1: Create the Advanced Topology

Save the following Python code in a file named `advanced_arp_topo.py`:

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
        
        # Add links
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)
        self.addLink(s1, s2)

def run():
    topo = AdvancedARPTopo()
    net = Mininet(topo=topo)
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
```

Run the script:

```bash
# Make the script executable
chmod +x advanced_arp_topo.py

# Run the topology
sudo python advanced_arp_topo.py
```

### Step 2: Advanced Experiments

1. **Cross-Segment ARP:**

   - Start packet capture on multiple interfaces:

     ```bash
     mininet> h1 tcpdump -i any arp -w /tmp/segment1.pcap &
     mininet> h3 tcpdump -i any arp -w /tmp/segment2.pcap &
     ```

   - Trigger ARP by pinging across segments:

     ```bash
     mininet> h1 ping -c1 10.0.2.1
     ```

2. **ARP Broadcasting:**

   - Monitor ARP broadcasts on all hosts:

     ```bash
     mininet> h1 tcpdump -i any arp &
     mininet> h2 tcpdump -i any arp &
     mininet> h3 tcpdump -i any arp &
     mininet> h4 tcpdump -i any arp &
     ```

   - Generate traffic:

     ```bash
     mininet> h1 ping -c1 10.0.2.2
     ```

---

## Part 4: Analyzing ARP Packets

Use Wireshark to analyze captured packets. Key details:

1. **ARP Request Format:**
   - Destination MAC: `ff:ff:ff:ff:ff:ff` (broadcast)
   - Source MAC: Sender's MAC
   - Operation code: `1` (request)
   - Target MAC: `00:00:00:00:00:00` (unknown)

2. **ARP Reply Format:**
   - Destination MAC: Unicast to requester
   - Source MAC: Responder's MAC
   - Operation code: `2` (reply)
   - Complete MAC-IP mapping

---

## Troubleshooting

1. **No ARP Replies:**
   - Verify network connectivity.
   - Check if IPs are in the same subnet.
   - Ensure switches are properly connected.

2. **Packet Capture Issues:**
   - Ensure tcpdump is running with correct permissions.
   - Verify interface names.
   - Check storage space for captures.

---

## Cleanup

1. **Stop Mininet:**

   ```bash
   mininet> exit
   ```

2. **Clean up Mininet:**

   ```bash
   sudo mn -c
   ```

---

By following this tutorial, you will gain practical insights into ARP and its role in local network communication. Happy learning!

