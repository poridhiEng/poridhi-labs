# Simulating VLAN Networks with Mininet

Mininet is an incredibly versatile tool that allows for the simulation of complex networks within a virtualized environment. By leveraging Mininet, network engineers, researchers, and students can experiment with Virtual Local Area Network (VLAN) configurations to better understand and manage network segmentation and isolation. VLANs are a crucial aspect of modern networking, enabling enhanced security, traffic management, and logical separation within larger networks. This document provides a comprehensive guide to setting up a simulated VLAN network using a custom Mininet host class called `VLANHost`.

The key element of this simulation is the `vlanhost.py` script, which enables the creation of hosts configured with specific VLAN tags. These VLAN tags act as identifiers that segment the network, ensuring that only devices within the same VLAN can communicate, while others remain isolated. This provides an ideal platform for experimenting with VLAN-based network architectures.

## Task Description
The primary objectives of this task are as follows:
1. Simulate a network consisting of two VLANs.
2. Configure each VLAN with two hosts, ensuring proper isolation and segmentation.
3. Verify that communication is successful between hosts within the same VLAN.
4. Confirm that communication between hosts in different VLANs is blocked.
5. Offer a detailed step-by-step guide, complete with an architecture diagram and sample code, to facilitate the simulation process.

## Network Architecture

![](./1.svg)

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
sudo python simulate_vlan_network.py
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

### 3. Test Connectivity for Hosts Without VLANs
- If there are hosts without VLAN tags:
  ```bash
  mininet> h1 ping -c 1 h1-100
  ```
  This should fail, as VLAN tags enforce strict isolation.

## Conclusion
This simulation serves as an excellent example of how VLANs can be implemented and tested in a controlled environment. By assigning VLAN tags and configuring hosts accordingly, users can explore the principles of network segmentation and isolation. Mininet provides an efficient way to experiment with VLAN configurations, making it a valuable tool for both learning and practical applications. Through this exercise, you gain hands-on experience in creating secure and segmented virtual networks, mirroring real-world VLAN setups.

