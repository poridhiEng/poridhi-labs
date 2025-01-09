# **A network topology using Linux network namespaces, bridges, and veth pairs**

This lab outlines the steps to create an isolated network topology using Linux network namespaces, bridges, and veth pairs. The setup includes two racks `(TOR1 and TOR2)` connected to a distribution layer `(BR-DIST)`. Each rack contains two servers.

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-27.png)

## **Prerequisites**
- **Operating System**: Linux with root or sudo access.
- **Required Tools**:
  - `iproute2`: For managing namespaces, links, and routes.
  - `iptables`: For configuring forwarding and NAT.
  - `ping`: For connectivity testing.
  - `sysctl`: For modifying kernel parameters.

## **Setup Steps**

### **1. Create Network Namespaces**

We will simulate servers using network namespaces. Each server will be represented by a network namespace. Namespaces isolate the network environments of different servers. Run the following commands to create four namespaces for the servers:  

```bash
sudo ip netns add server1
sudo ip netns add server2
sudo ip netns add server3
sudo ip netns add server4
```

Network namespaces allow us to create isolated network environments. Each namespace functions like a virtual machine with its own routing table, interfaces, and rules.

**Commands:**

- `sudo ip netns add serverX`: Creates a namespace named serverX.
- `sudo ip netns`: Verifies created namespaces.

This is to simulate servers (server1 to server4) that are isolated and cannot interfere with the host's network or each other until explicitly connected.

Verify the namespaces are created:

```bash
sudo ip netns
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-17.png)


### **2. Create Bridge Interfaces**

Bridges simulate switches (e.g., ToR1, ToR2, distribution layer) in a real-world network. Assigning IPs allows communication with and between the bridges. Bridges simulate network switches and connect namespaces. We will create three bridges, `br-tor1`, `br-tor2`, and `br-dist`.

1. **Create the bridges**:

   ```bash
   sudo ip link add br-tor1 type bridge
   sudo ip link add br-tor2 type bridge
   sudo ip link add br-dist type bridge
   ```

    Verify the bridges are created:
    ```bash
    sudo ip link show
    ```
    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-18.png)

2. **Activate the bridges**:

   As we have created the bridges, we need to activate them.

   ```bash
   sudo ip link set br-tor1 up
   sudo ip link set br-tor2 up
   sudo ip link set br-dist up
   ```
3. **Assign IPs to TOR bridges**:

   Next, we need to assign IPs to the TOR bridges. We will assign the following IPs to the bridges:
   - `br-tor1`: 192.168.1.1/24
   - `br-tor2`: 192.168.2.1/24
   - `br-dist`: 10.0.0.1/24

   ```bash
   sudo ip addr add 192.168.1.1/24 dev br-tor1
   sudo ip addr add 192.168.2.1/24 dev br-tor2
   sudo ip addr add 10.0.0.1/24 dev br-dist
   ```
   Verify the IPs are assigned:
   ```bash
   sudo ip addr show
   ```
   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-19.png)

### **3. Create Server Connections**

Veth pairs act like virtual Ethernet cables that connect namespaces to bridges. Virtual Ethernet (veth) pairs connect namespaces to bridges. We will create four veth pairs, `veth1`, `veth2`, `veth3`, and `veth4`.

1. **Create veth pairs for each server**:
   ```bash
   sudo ip link add veth1 type veth peer name veth1-br
   sudo ip link add veth2 type veth peer name veth2-br
   sudo ip link add veth3 type veth peer name veth3-br
   sudo ip link add veth4 type veth peer name veth4-br
   ```

   Verify the veth pairs are created:
   ```bash
   sudo ip link show
   ```
    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-20.png)

2. **Assign to namespaces**:

   Next, we need to assign the veth pairs to the namespaces. We will assign the following veth pairs to the namespaces:

   ```bash
   sudo ip link set veth1 netns server1
   sudo ip link set veth2 netns server2
   sudo ip link set veth3 netns server3
   sudo ip link set veth4 netns server4
   ```
3. **Connect to bridges**:

   Next, we need to connect the veth pairs to the bridges. We will connect the following veth pairs to the bridges:

   ```bash
   sudo ip link set veth1-br master br-tor1
   sudo ip link set veth2-br master br-tor1
   sudo ip link set veth3-br master br-tor2
   sudo ip link set veth4-br master br-tor2
   ```
4. **Activate interfaces**:

   Next, we need to activate the interfaces. We will activate the following interfaces:

   ```bash
   sudo ip link set veth1-br up
   sudo ip link set veth2-br up
   sudo ip link set veth3-br up
   sudo ip link set veth4-br up
   ```

   Verify the interfaces are activated:
   ```bash
   sudo ip link show
   ```
   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-21.png)

   This setup connects the isolated namespaces to their respective ToR switches, enabling them to communicate with other namespaces and the outside network.

### **4. Configure Server Networking**

Each server (namespace) needs its own IP address and active interfaces for communication. Assign IP addresses and bring up interfaces inside each namespace. We will assign the following IPs to the servers:

- `server1`: 192.168.1.2/24
- `server2`: 192.168.1.3/24
- `server3`: 192.168.2.2/24
- `server4`: 192.168.2.3/24

1. **Rack 1 (TOR1)**:
   ```bash
   sudo ip netns exec server1 ip link set lo up
   sudo ip netns exec server1 ip link set veth1 up
   sudo ip netns exec server1 ip addr add 192.168.1.2/24 dev veth1

   sudo ip netns exec server2 ip link set lo up
   sudo ip netns exec server2 ip link set veth2 up
   sudo ip netns exec server2 ip addr add 192.168.1.3/24 dev veth2
   ```

   Verify the interfaces are activated:
   ```bash
   sudo ip netns exec server1 ip link show
   sudo ip netns exec server2 ip link show
   ```
   ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-22.png)

2. **Rack 2 (TOR2)**:

    ```bash
    sudo ip netns exec server3 ip link set lo up
    sudo ip netns exec server3 ip link set veth3 up
    sudo ip netns exec server3 ip addr add 192.168.2.2/24 dev veth3

    sudo ip netns exec server4 ip link set lo up
    sudo ip netns exec server4 ip link set veth4 up
    sudo ip netns exec server4 ip addr add 192.168.2.3/24 dev veth4
    ```

This step simulates server network configuration in real-world deployments. Each namespace (server) becomes uniquely identifiable by its IP.

### **5. Connect Distribution Layer**

The distribution layer `(br-dist)` connects ToR switches `(br-tor1 and br-tor2)`. This mimics the interconnection between racks and a distribution switch in real-world network topologies.

1. **Add veth pairs**:
   ```bash
   sudo ip link add tor1-dist type veth peer name dist-tor1
   sudo ip link add tor2-dist type veth peer name dist-tor2
   ```
2. **Attach links to the bridges**:
   ```bash
   sudo ip link set tor1-dist master br-tor1
   sudo ip link set dist-tor1 master br-dist
   sudo ip link set tor2-dist master br-tor2
   sudo ip link set dist-tor2 master br-dist
   ```
3. **Activate the interfaces**:
   ```bash
   sudo ip link set tor1-dist up
   sudo ip link set dist-tor1 up
   sudo ip link set tor2-dist up
   sudo ip link set dist-tor2 up
   ```

   Verify the interfaces are activated:
   ```bash
   sudo ip link show
   ```

### **6. Configure Bridge Settings**

Enable ARP proxy on TOR bridges and bridge-nf.

```bash
sudo sysctl -w net.ipv4.conf.br-tor1.proxy_arp=1
sudo sysctl -w net.ipv4.conf.br-tor2.proxy_arp=1
```

These commands enable:

- Proxy ARP (Address Resolution Protocol) for the specified bridge interfaces `(br-tor1 and br-tor2)`. 
- Proxy ARP allows a device (e.g., the bridge) to answer ARP requests on behalf of other devices, facilitating transparent forwarding of packets in complex networks.


```bash
# Enable bridge-nf
sudo modprobe br_netfilter
sudo bash -c 'echo 0 > /proc/sys/net/bridge/bridge-nf-call-iptables'
```

These commands enable:

- Loads the br_netfilter kernel module, which enables netfilter functionality for bridges. Netfilter is the framework used by iptables for packet filtering and NAT.
- Sets the bridge-nf-call-iptables parameter to 0, disabling iptables processing for packets traversing the bridge.

**Why it's necessary:**

- By default, bridge interfaces may filter packets through iptables, which can disrupt traffic routing.
- Disabling iptables processing `(bridge-nf-call-iptables)` ensures that the bridge forwards packets at Layer 2 (Ethernet) without applying any Layer 3 (IP) or Layer 4 (TCP/UDP) rules, allowing unimpeded traffic flow.
- This configuration is crucial for setups like transparent bridges, where no additional routing or filtering should occur.

**Set Bridges in Promiscuous Mode**

```bash
sudo ip link set br-tor1 promisc on
sudo ip link set br-tor2 promisc on
```

- Enables promiscuous mode on the bridge interfaces `(br-tor1 and br-tor2)`.
- In promiscuous mode, a network interface receives all packets on the network, not just the packets addressed to it.


### **7. Configure Routing**

Enable IP forwarding and add routes on the distribution bridge.  

```bash
# Enable IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1

# Add routes on br-dist
sudo ip route add 192.168.1.0/24 via 192.168.1.1 dev br-tor1
sudo ip route add 192.168.2.0/24 via 192.168.2.1 dev br-tor2

sudo ip netns exec server1 ip route add default via 192.168.1.1
sudo ip netns exec server2 ip route add default via 192.168.1.1
sudo ip netns exec server3 ip route add default via 192.168.2.1
sudo ip netns exec server4 ip route add default via 192.168.2.1
```

Verify the server routes are added:
```bash
sudo ip netns exec server1 ip route show
sudo ip netns exec server2 ip route show
sudo ip netns exec server3 ip route show
sudo ip netns exec server4 ip route show
```

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-23.png)

### **8. Configure Forwarding Rules**

Enable packet forwarding and masquerading.

```bash
# Enable packet forwarding
sudo iptables -A FORWARD -i br-tor1 -o br-tor2 -j ACCEPT
sudo iptables -A FORWARD -i br-tor2 -o br-tor1 -j ACCEPT
```

These commands enable:

- Packet forwarding between the two bridge interfaces `(br-tor1 and br-tor2)`.
- The FORWARD chain is where iptables processes packets that are destined for a different interface than the one they are received on.

**Why it's necessary:**

- By default, Linux kernel policies may not allow forwarding between network interfaces.
- These rules explicitly permit traffic to flow bidirectionally between `(br-tor1 and br-tor2)`, enabling seamless communication between networks connected to these bridges.

**Enable Masquerading**

```bash
sudo iptables -t nat -A POSTROUTING -o br-tor2 -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -o br-tor1 -j MASQUERADE
```

These commands enable:

- NAT (Network Address Translation) using the POSTROUTING chain in the nat table.
- Applies masquerading to packets leaving the specified interfaces `(br-tor1 and br-tor2)`.


**What is MASQUERADE in Networking?**

In networking, MASQUERADE is a specialized target used in iptables to implement a dynamic form of Source Network Address Translation (SNAT). It is commonly used in scenarios where the public IP address of a device or network interface is not static or is subject to frequent changes.


**Why it's necessary:**

- Masquerading is used to ensure packets leaving one bridge interface `(br-tor1 or br-tor2)` have a valid source IP address.
- This is essential in scenarios where the source devices behind the bridge do not have IP addresses in the same subnet as the destination or when using NAT for routing between subnets.

### **Testing**

Test intra-rack and inter-rack connectivity.

```bash
# Test intra-rack connectivity
sudo ip netns exec server1 ping 192.168.1.3
```

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/lab2-14.drawio.svg)

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-24.png)

```bash
# Test inter-rack connectivity
sudo ip netns exec server1 ping 192.168.2.2
```

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/lab2-13.drawio.svg)

![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2002/images/image-25.png)


## **Conclusion**

This lab provided a comprehensive understanding of how to create an isolated network topology using Linux network namespaces, bridges, and veth pairs. It demonstrated how to set up a simple network with two racks connected to a distribution layer, and how to configure routing and forwarding rules to ensure proper network communication between the servers.

