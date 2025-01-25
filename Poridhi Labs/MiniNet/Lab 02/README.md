# Simulating a Simple Network with Mininet

In this lab, we will explore the basics of Mininet and learn how to simulate a simple network topology. Mininet is a powerful network emulator that allows users to create virtual networks for testing, research, and learning without requiring physical hardware. By the end of this lab, you will understand how to create a custom network topology using Mininet, test connectivity between hosts, and interact with the network using Mininet's command-line interface (CLI).

## Prerequisites

Before starting this lab, ensure that you have the following:

1. **Mininet Installed**: Mininet can be installed on Linux-based systems. You can install it using:

   ```bash
   sudo apt-get update
   sudo apt-get install mininet
   ```
2. **Python Installed**: Ensure Python 3 is installed on your system.
3. **Basic Networking Knowledge**: Familiarity with terms like hosts, switches, and ping.

## Task Overview

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/9326b22e2d6c578030a1c9978f83913f712fd2af/Poridhi%20Labs/MiniNet/Lab%2002/images/Mininet-lab-02.svg)

We will create a simple network topology consisting of:

- Two hosts (`h1` and `h2`)
- One switch (`s1`)

The hosts will be connected to the switch, and we will test their connectivity using the `ping` command. Additionally, we will interact with the network through the Mininet CLI.

## What is Mininet?

Mininet is a lightweight emulator that creates virtual networks using software. It allows users to:
- Build custom network topologies.
- Run unmodified code for real applications and protocols.
- Test and prototype network designs efficiently.

Mininet operates by creating virtual hosts, switches, and links that run on a single machine. These components behave like their physical counterparts, making it ideal for learning and experimentation.

## Steps to Simulate the Network

### Step 1: Define the Network Topology

We will define the network topology using a Python script. The script creates a simple topology with two hosts connected to one switch.

#### Python Script
Save the following script as `simple_topo.py`:

```python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.cli import CLI

class SimpleTopo(Topo):
    def build(self):
        # Add two hosts
        h1 = self.addHost('h1')  # Host 1
        h2 = self.addHost('h2')  # Host 2
        
        # Add one switch
        s1 = self.addSwitch('s1')  # Switch 1
        
        # Add links between hosts and switch
        self.addLink(h1, s1)
        self.addLink(h2, s1)

# Create and start the network
if __name__ == '__main__':
    topo = SimpleTopo()  # Create topology
    net = Mininet(topo=topo)  # Initialize Mininet
    net.start()  # Start the network
    
    print("Testing network connectivity with ping...")
    net.pingAll()  # Test connectivity between hosts
    
    CLI(net)  # Launch Mininet CLI for manual testing
    net.stop()  # Stop the network
```

### Step 2: Run the Script

1. Save the script as `simple_topo.py`.
2. Open a terminal and navigate to the directory containing the script.
3. Run the script using:

   ```bash
   sudo python3 simple_topo.py
   ```

### Step 3: Observe the Results

#### Automatic Ping Test

The script automatically tests connectivity between the two hosts using the `pingAll()` function. The output will look something like this:

```
*** Ping: testing ping reachability
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
```

This confirms that the two hosts can communicate with each other through the switch.

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MiniNet/Lab%2002/images/image.png)

#### Manual Testing with Mininet CLI

After the script starts the network, you can interact with it using the Mininet CLI. For example:

1. Ping `h2` from `h1`:

   ```bash
   mininet> h1 ping h2
   ```

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MiniNet/Lab%2002/images/image-1.png)

2. Check the IP address of `h1`:

   ```bash
   mininet> h1 ifconfig
   ```

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/MiniNet/Lab%2002/images/image-2.png)

3. Exit the CLI:

   ```bash
   mininet> exit
   ```

## Summary

In this lab, we:
1. Learned about Mininet and its capabilities.
2. Created a simple network topology with two hosts and one switch.
3. Tested connectivity between the hosts using `ping`.
4. Interacted with the network using the Mininet CLI.

This exercise demonstrated how Mininet can be used to emulate networks for learning and testing purposes. You can expand this topology by adding more hosts, switches, or experimenting with different configurations.

