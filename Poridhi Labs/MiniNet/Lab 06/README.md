# Simulating VLAN Networks with Mininet

Mininet is an incredibly versatile tool that allows for the simulation of complex networks within a virtualized environment. By leveraging Mininet, network engineers, researchers, and students can experiment with Virtual Local Area Network (VLAN) configurations to better understand and manage network segmentation and isolation. 

![](./images/2.svg)

VLANs are a crucial aspect of modern networking, enabling enhanced security, traffic management, and logical separation within larger networks. This document provides a comprehensive guide to setting up a simulated VLAN network using a custom Mininet host class called `VLANHost`. The key element of this simulation is the `vlanhost.py` script, which enables the creation of hosts configured with specific VLAN tags. These VLAN tags act as identifiers that segment the network, ensuring that only devices within the same VLAN can communicate, while others remain isolated. This provides an ideal platform for experimenting with VLAN-based network architectures.

## Task Description
The primary objectives of this task are as follows:
1. Simulate a network consisting of two VLANs.
2. Configure each VLAN with two hosts, ensuring proper isolation and segmentation.
3. Verify that communication is successful between hosts within the same VLAN.
4. Confirm that communication between hosts in different VLANs is blocked.
5. Offer a detailed step-by-step guide, complete with an architecture diagram and sample code, to facilitate the simulation process.

## Network Architecture

![](./images/1.svg)



The provided diagram illustrates the logical structure of a network simulation featuring VLANs (Virtual Local Area Networks) using a single switch, S1, and two VLANs (VLAN 100 and VLAN 101). Here’s a detailed explanation:

### **Key Components**
1. **Switch S1:** 
   - The central point of communication, enabling connectivity between all the hosts in the network. It supports VLAN tagging to segregate traffic.

2. **VLAN 100 and VLAN 101:** 
   - VLAN 100 consists of two hosts: `H1-100` and `H2-100`.
   - VLAN 101 also has two hosts: `H1-101` and `H2-101`.
   - Each VLAN operates as a distinct broadcast domain, ensuring that traffic within one VLAN remains isolated from the other.

3. **Hosts:** 
   - `H1-100` and `H2-100` are configured to operate on VLAN 100.
   - `H1-101` and `H2-101` are configured for VLAN 101.

### **Connections**
- **Switch to Hosts:** 
  - The switch (S1) has interfaces connected to all the hosts.
  - Each interface is associated with a VLAN ID, ensuring traffic from a host is tagged with the corresponding VLAN ID when leaving the switch.
  - For instance, packets from `H1-100` and `H2-100` are tagged with VLAN 100, while packets from `H1-101` and `H2-101` are tagged with VLAN 101.

### **Behavior**
1. **Intra-VLAN Communication:** 
   - Hosts within the same VLAN (e.g., `H1-100` and `H2-100`) can communicate directly, as their packets carry the same VLAN tag. 
   - The switch forwards these packets without interference to other VLANs.

2. **Inter-VLAN Isolation:**
   - Communication between hosts in different VLANs (e.g., `H1-100` and `H1-101`) is not allowed by default, ensuring logical segmentation. This is a critical feature of VLANs, enhancing network security and reducing broadcast domain sizes.






## File Creation

### 1. `vlanhost.py`
This script is essential for defining the `VLANHost` class, which facilitates the creation of hosts with VLAN tags. The class extends Mininet's `Host` class and overrides its configuration method to include VLAN-specific settings.

```python
#!/usr/bin/env python
from sys import exit
from functools import partial
from mininet.node import Host
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, error
from mininet.util import quietRun

class VLANHost(Host):
    """Host connected to VLAN interface"""

    def config(self, vlan=100, **params):
        r = super(VLANHost, self).config(**params)
        intf = self.defaultIntf()
        self.cmd('ifconfig %s inet 0' % intf)  # remove IP from default interface
        self.cmd('vconfig add %s %d' % (intf, vlan))  # create VLAN interface
        self.cmd('ifconfig %s.%d inet %s' % (intf, vlan, params['ip']))  # assign IP to VLAN interface

        newName = '%s.%d' % (intf, vlan)
        intf.name = newName
        self.nameToIntf[newName] = intf
        return r

hosts = {'vlan': VLANHost}

class VLANStarTopo(Topo):
    """Topology with VLAN hosts connected to a single switch"""

    def build(self, k=2, n=2, vlanBase=100):
        s1 = self.addSwitch('s1')
        for i in range(k):
            vlan = vlanBase + i
            for j in range(n):
                name = 'h%d-%d' % (j+1, vlan)
                h = self.addHost(name, cls=VLANHost, vlan=vlan)
                self.addLink(h, s1)
```

### 2. `simulate_vlan_network.py`
This script sets up the VLAN network and provides an interactive Mininet CLI for testing and verification.

```python
#!/usr/bin/env python
from vlanhost import VLANStarTopo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel

def simulate_vlan_network():
    """Simulate a VLAN network with Mininet"""
    topo = VLANStarTopo(k=2, n=2, vlanBase=100)  # 2 VLANs, each with 2 hosts
    net = Mininet(topo=topo, waitConnected=True)

    net.start()
    print("Network setup complete. Entering CLI...")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    simulate_vlan_network()
```

## Run Steps

### 1. Install Dependencies
Before running the simulation, ensure the necessary VLAN package is installed:
```bash
sudo apt-get install vlan
```

### 2. Save Files
- Save the first script as `vlanhost.py`.
- Save the second script as `simulate_vlan_network.py`.

### 3. Execute the Simulation
Run the simulation script using the command:
```bash
sudo python3 simulate_vlan_network.py
```

## Verification
After starting the simulation, the Mininet CLI will allow you to test and verify the setup. Use the following commands:

### 1. Test Connectivity Within the Same VLAN
- For VLAN 100:

  ```bash
  mininet> h1-100 ping -c 1 h2-100
  ```
  This command should show a successful ping response.
- For VLAN 101:

  ```bash
  mininet> h1-101 ping -c 1 h2-101
  ```
  This should also succeed.

### 2. Test Connectivity Across Different VLANs
- Test between VLAN 100 and VLAN 101:

  ```bash
  mininet> h1-100 ping -c 1 h1-101
  ```
  This command should fail, demonstrating VLAN isolation.


### 3. Test Connectivity from all hosts 

- If there are hosts without VLAN tags:

  ```bash
  mininet> pingall
  ```

  Expected output:

  ```bash
  mininet> pingall
  *** Ping: testing ping reachability
  h1-100 -> X h2-100 X 
  h1-101 -> X X h2-101 
  h2-100 -> h1-100 X X 
  h2-101 -> X h1-101 X 
  *** Results: 66% dropped (4/12 received)
  ```

  This should show a list of successful and failed ping responses.

## Conclusion
This simulation serves as an excellent example of how VLANs can be implemented and tested in a controlled environment. By assigning VLAN tags and configuring hosts accordingly, users can explore the principles of network segmentation and isolation. Mininet provides an efficient way to experiment with VLAN configurations, making it a valuable tool for both learning and practical applications. Through this exercise, you gain hands-on experience in creating secure and segmented virtual networks, mirroring real-world VLAN setups.

