# **Configuring Multiple IP Subnets over a Single L2 Broadcast Domain**

In networking, a subnet is a logical subdivision of an IP network, and it plays a critical role in routing and traffic management. Most network setups map a single IP subnet to an L2 (Layer 2) broadcast domain, where devices can directly communicate using MAC addresses. However, it's also possible to configure multiple IP subnets over the same L2 segment. This lab demonstrates how to achieve such a configuration and explores its security implications. 

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2004/images/1.svg)


## **Prerequisites**
We will use Linux network virtualization tools to emulate a network environment. Here's what you'll need:

1. **Network Namespaces**: Used to emulate separate network nodes.
2. **veth Devices**: Virtual Ethernet devices to emulate network interfaces.
3. **Bridge Devices**: To emulate network switches.
4. **Helper Scripts**: Provided scripts to simplify the setup process.
5. **Install tcpdump:** Install tcpdump dump

    ```bash
    sudo apt update
    sudo apt install tcpdump -y
    ```



## **Helper Scripts Setup**
 Paste the following script into your terminal:

### **Script: create_new_bridge**
This script creates a network namespace with a Linux bridge device.

```bash
create_new_bridge() {
  local ns_name="$1"
  local br_name="$2"

  echo "Creating bridge ${ns_name}/${br_name}"

  ip netns add ${ns_name}
  ip netns exec ${ns_name} ip link set lo up
  ip netns exec ${ns_name} ip link add ${br_name} type bridge
  ip netns exec ${ns_name} ip link set ${br_name} up
}
```

### **Script: create_end_host**
This script creates a network namespace with a veth device and assigns an IP address. The other end of the veth pair connects to a bridge in another namespace.

```bash
create_end_host() {
  local host_ns="$1"
  local veth_host="$2"
  local veth_bridge="${veth_host}b"
  local ip_address="$3"
  local bridge_ns="$4"
  local br_name="$5"

  echo "Creating end host ${host_ns} with IP ${ip_address} connected to ${bridge_ns}/${br_name}"

  ip netns add ${host_ns}
  ip netns exec ${host_ns} ip link set lo up

  ip link add ${veth_host} netns ${host_ns} type veth peer ${veth_bridge} netns ${bridge_ns}
  ip netns exec ${host_ns} ip link set ${veth_host} up
  ip netns exec ${bridge_ns} ip link set ${veth_bridge} up

  ip netns exec ${host_ns} ip addr add ${ip_address} dev ${veth_host}
  ip netns exec ${bridge_ns} ip link set ${veth_bridge} master ${br_name}
}
```



## **Scenario 1: Single IP Subnet over an L2 Broadcast Domain**

### **Objective**
Configure an IP subnet `192.168.0.0/24` over a single L2 broadcast domain.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2004/images/2.svg)

### **Steps**

1. **Create a Bridge Device**:
   ```bash
   create_new_bridge bridge1 br1
   ```

2. **Create End Hosts**:
   ```bash
   create_end_host host1 eth1 '192.168.0.1/24' bridge1 br1
   create_end_host host2 eth2 '192.168.0.2/24' bridge1 br1
   create_end_host host3 eth3 '192.168.0.3/24' bridge1 br1
   ```

3. **Test Connectivity**:
   - Monitor traffic on `host2`:
     ```bash
     nsenter --net=/var/run/netns/host2 tcpdump -i eth2
     ```
   - Ping `host2` from `host1`:
     ```bash
     nsenter --net=/var/run/netns/host1 ping 192.168.0.2
     ```

4. **Verify results:**

    - Host 1:

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2004/images/image-1.png)

    - Host 2:

        ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2004/images/image.png)

4. **Clean Up**:
   ```bash
   ip netns delete bridge1
   ip netns delete host1
   ip netns delete host2
   ip netns delete host3
   ```



## **Scenario 2: Multiple IP Subnets over an L2 Broadcast Domain**

### **Objective**
Configure two separate IP subnets (`192.168.0.0/24` and `192.168.1.0/24`) over a single L2 broadcast domain.

![](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2004/images/3.svg)

### **Steps**

1. **Create a Bridge Device**:
   ```bash
   create_new_bridge bridge2 br2
   ```

2. **Configure Subnet 1 (`192.168.0.0/24`)**:
   ```bash
   create_end_host host10 eth10 '192.168.0.10/24' bridge2 br2
   create_end_host host11 eth11 '192.168.0.11/24' bridge2 br2
   create_end_host host12 eth12 '192.168.0.12/24' bridge2 br2
   ```

3. **Configure Subnet 2 (`192.168.1.0/24`)**:
   ```bash
   create_end_host host20 eth20 '192.168.1.20/24' bridge2 br2
   create_end_host host21 eth21 '192.168.1.21/24' bridge2 br2
   create_end_host host22 eth22 '192.168.1.22/24' bridge2 br2
   ```

4. **Test Connectivity Within Subnets**:
   - Monitor traffic on a host from Subnet 1 (e.g., `host11`):
     ```bash
     nsenter --net=/var/run/netns/host11 tcpdump -i eth11 arp or icmp
     ```
   - Monitor traffic on a host from Subnet 2 (e.g., `host21`):
     ```bash
     nsenter --net=/var/run/netns/host21 tcpdump -i eth21 arp or icmp
     ```
   - Ping a host within Subnet 1:
     ```bash
     nsenter --net=/var/run/netns/host10 ping 192.168.0.12
     ```
   - Ping a host within Subnet 2:
     ```bash
     nsenter --net=/var/run/netns/host20 ping 192.168.1.22
     ```

5. **Observe Results**:
   Notice how traffic from one subnet is visible to nodes in the other subnet due to the shared L2 domain.

    ![alt text](https://github.com/poridhiEng/poridhi-labs/raw/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2004/images/image-2.png)

6. **Clean Up**:
   ```bash
   ip netns delete bridge2
   ip netns delete host10
   ip netns delete host11
   ip netns delete host12
   ip netns delete host20
   ip netns delete host21
   ip netns delete host22
   ```



## **Conclusion**
This lab demonstrates the configuration and implications of running multiple IP subnets over a shared L2 segment. While this setup works, it lacks proper isolation, posing potential security risks. Introducing VLANs can address these concerns by isolating traffic into separate broadcast domains.

#### References

- [Computer Networking Fundamentals](https://labs.iximiuz.com/courses/computer-networking-fundamentals)
