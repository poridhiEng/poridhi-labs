Here's how you can verify the created virtual Ethernet interfaces (veth), bridge, and namespaces during the lab:

### **Verification Commands for the Created Resources**

#### **1. List All Network Namespaces**
To check the network namespaces created:
```bash
ip netns list
```
This should display:
```
bridge1
host1
host2
host3
```

#### **2. Inspect the Bridge (`br1`)**
To view the bridge (`br1`) and its associated interfaces:
```bash
ip netns exec bridge1 brctl show
```
This will show the bridge and its attached virtual Ethernet interfaces (`eth1`, `eth2`, `eth3`).

#### **3. Check Virtual Ethernet Interfaces**
To view the virtual Ethernet interfaces associated with each namespace:
```bash
ip netns exec host1 ip link
ip netns exec host2 ip link
ip netns exec host3 ip link
```
Each command should list the interfaces, such as `eth1` for `host1`, `eth2` for `host2`, and `eth3` for `host3`.

#### **4. Verify Connectivity**
To test connectivity between hosts (e.g., `host1` and `host2`):
```bash
ip netns exec host1 ping -c 4 $(ip netns exec host2 ip addr show eth2 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
```
This assumes you have assigned IP addresses to the interfaces. If no IP addresses are set, the `ping` test won't work since it's an L3 function. 

#### **5. Check Network Traffic**
To ensure traffic flows through the bridge, you can monitor the bridge's interface using:
```bash
ip netns exec bridge1 tcpdump -i br1
```

### **Additional Notes**
- Ensure you have `tcpdump`, `bridge-utils`, and `iproute2` installed on your system.
- The `nsenter` commands allow you to execute commands within specific namespaces, providing direct access to their virtual interfaces.

Would you like to include these verification steps in the lab document? Let me know!