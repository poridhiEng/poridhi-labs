# **Using MAC Addresses (Layer 2 Data)**

In this lab, we will use **MAC addresses** to create flow rules for traffic between hosts. We will create rules based on the source and destination MAC addresses of the packets.

![alt text](image-3.png)

## Network Topology

The network topology consists of:
- A single OpenFlow switch (`s1`).
- Three hosts:
  - `h1` (IP: `10.0.0.1`, Port: `s1-eth1`)
  - `h2` (IP: `10.0.0.2`, Port: `s1-eth2`)
  - `h3` (IP: `10.0.0.3`, Port: `s1-eth3`)

All hosts are connected to the same switch (`s1`).

## Start Mininet

Launch Mininet with the default topology:

```bash
sudo mn --topo=single,3 --controller=none --mac
```

This creates a network with one switch and three hosts.

### Find the MAC Addresses of the hosts:

```bash
mininet> h1 ifconfig
mininet> h2 ifconfig
mininet> h3 ifconfig
```

![alt text](image.png)

### Add flow rules based on source and destination MAC addresses:

We will create flow rules to forward traffic from `h1` to `h2` and from `h2` to `h1`.

```bash
mininet> sh ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02,actions=output:2
mininet> sh ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01,actions=output:1
```

### Try to ping the hosts:

Send ping requests to each host:

```bash
mininet> pingall
```

![alt text](image-1.png)

Here we can see that the ping fails. This is because when you run `pingall` in Mininet, it tries to send ICMP packets (ping) from each host to all others. However, ICMP operates at the `**IP layer**` (Layer 3), while the underlying network setup requires ARP (Address Resolution Protocol) at the `**data link layer (Layer 2)**` to resolve IP addresses to MAC addresses. 

### **Why the Ping Fails?**

**1. ARP Requests Are Blocked**:

- Before a host can send an IP packet to another host, it must resolve the target IP address into a MAC address. This is done using ARP, which sends a **broadcast request** to all devices in the network asking, **"Who has this IP?"**
- The Open vSwitch (OVS), with its current flow rules, does not forward ARP broadcast packets by default.  It's filtering out **ARP data traffic**.

**2. No Matching Flow for ARP Packets**:

OVS checks its flow table for a rule to handle ARP packets (`dl_type=0x806`). Without a rule for `ARP`, these packets are dropped, preventing hosts from learning each other’s MAC addresses.

### **How to Fix It?**

To allow **ARP broadcasts** and enable communication between hosts, you need to add a flow rule to handle ARP packets:

```bash
mininet> sh ovs-ofctl add-flow s1 dl_type=0x806,nw_proto=1,action=flood
```

- **`dl_type=0x806`**: Matches Ethernet frames of type `0x806`, which indicates ARP packets.
- **`nw_proto=1`**: Matches ARP request packets.
- **`action=flood`**: Broadcasts the ARP request to all ports on the switch.

### **How It Works**

**1. ARP Requests Broadcasted**:

With this rule, whenever a host sends an **ARP request**, OVS **broadcasts** it to all connected devices. This allows the target host to receive the request and respond with its **MAC address** in an ARP reply.

**2. Unicast ARP Replies**:

ARP replies are **unicast** (sent directly to the requester). These unicast replies are handled correctly by the existing flow rules, as they match the source and destination MAC addresses specified in the rules.

### **Testing the Fix**

```bash
mininet> pingall
```

![alt text](image-2.png)

When you run `pingall`, the ARP requests are broadcasted to all hosts, enabling them to resolve each other's MAC addresses. Once MAC addresses are resolved, ICMP packets (ping) can flow as expected. 

![](./images/lab3-5.drawio.svg)

> `h3` is not able to communicate with h1 and h2 as we have not added any flow rules for h3. You can try adding flow rules for h3 and see if it works.

## Conclusion

In this lab, we learned how to use MAC addresses to create flow rules for traffic between hosts. We created rules based on the source and destination MAC addresses of the packets. We also learned how to add flow rules to handle ARP packets and how to test the setup.

