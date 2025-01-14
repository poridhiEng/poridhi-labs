### **Using MAC Addresses (Layer 2 Data)**
Add flow rules based on source and destination MAC addresses:

```bash
mininet> sh ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02,actions=output:2
mininet> sh ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01,actions=output:1
```

#### **Issue with ARP Traffic**
Ping tests fail due to lack of ARP broadcast handling. Add an ARP flood rule:

```bash
mininet> sh ovs-ofctl add-flow s1 dl_type=0x806,nw_proto=1,action=flood
```

- **dl_type=0x806:** Matches ARP packets.
- **action=flood:** Broadcasts ARP requests to all ports.

---

### **Using IP Addresses (Layer 3 Data)**
Define flows based on IP headers:

```bash
mininet> sh ovs-ofctl add-flow s1 priority=500,dl_type=0x800,nw_src=10.0.0.0/24,nw_dst=10.0.0.0/24,actions=normal
mininet> sh ovs-ofctl add-flow s1 priority=800,dl_type=0x800,nw_src=10.0.0.3,nw_dst=10.0.0.0/24,actions=mod_nw_tos:184,normal
```

6. **Explanation:**  
- **dl_type=0x800:** Matches IPv4 packets.
- **nw_src/nw_dst:** Filters packets by source and destination IP.
- **mod_nw_tos:184:** Modifies the DSCP value for quality of service (QoS).

---

### **Using Layer 4 (Transport Layer) Data**
Start a simple Python web server on host `h3`:

```bash
mininet> h3 python -m SimpleHTTPServer 80 &
```

Add a rule for TCP traffic to port 80:

```bash
mininet> sh ovs-ofctl add-flow s1 priority=500,dl_type=0x800,nw_proto=6,tp_dst=80,actions=output:3
```

8. **Explanation:**  
- **nw_proto=6:** Matches TCP traffic.
- **tp_dst=80:** Matches traffic destined for port 80.
  
Check connectivity:

```bash
mininet> h1 curl h3
```

---

This step-by-step guide explains key concepts and commands for managing SDN networks manually, providing a comprehensive foundation for hands-on learning in Mininet environments.