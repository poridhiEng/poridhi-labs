# **Setting Up a VLAN Using Linux Virtualization Tools**

In this hands-on lab, we will learn how to use the native VLAN capabilities of a Linux bridge to split a single broadcast domain into multiple smaller domains. These VLANs will allow us to configure isolated IP subnets, enhancing network security and efficiency. We will emulate network components using Linux namespaces, virtual Ethernet (veth) devices, and Linux bridge devices.

![](./images/1.svg)

## **Prerequisites**

1. **Linux Environment**: Ensure you have a Linux machine with administrative privileges.
2. **Basic Networking Tools**: Tools like `ip`, `bridge`, and `tcpdump` must be installed.
3. **Helper Scripts**:
   - `create_new_bridge`: Creates a network namespace with a Linux bridge device and enables VLAN filtering. Paste the following code into  your   terminal.

        ```bash
        create_new_bridge() {
            local ns_name="$1"
            local if_name="$2"

            echo "Creating bridge ${ns_name}/${if_name}"

            ip netns add ${ns_name}
            ip netns exec ${ns_name} ip link set lo up
            ip netns exec ${ns_name} ip link add ${if_name} type bridge
            ip netns exec ${ns_name} ip link set ${if_name} up

            # Enable VLAN filtering on bridge.
            ip netns exec ${ns_name} ip link set ${if_name} type bridge vlan_filtering 1
        }
        ```

   - `create_new_node`: Creates a network namespace with a veth device and assigns it to a specific VLAN. Paste the following code into your terminal.

        ```bash
        create_new_node() {
            local host_ns_name="$1"
            local peer1_if_name="$2"
            local peer2_if_name="$2b"
            local vlan_vid="$3"
            local bridge_ns_name="$4"
            local bridge_if_name="$5"

            echo "Creating end host ${host_ns_name} connected to ${bridge_ns_name}/${bridge_if_name} bridge (VLAN ${vlan_vid})"

            # Create end host network namespace.
            ip netns add ${host_ns_name}
            ip netns exec ${host_ns_name} ip link set lo up

            # Create a veth pair connecting end host and bridge namespaces.
            ip link add ${peer1_if_name} netns ${host_ns_name} type veth peer \
                        ${peer2_if_name} netns ${bridge_ns_name}
            ip netns exec ${host_ns_name} ip link set ${peer1_if_name} up
            ip netns exec ${bridge_ns_name} ip link set ${peer2_if_name} up

            # Attach peer2 interface to the bridge.
            ip netns exec ${bridge_ns_name} ip link set ${peer2_if_name} master ${bridge_if_name}

            # Put host into right VLAN
            ip netns exec ${bridge_ns_name} bridge vlan del dev ${peer2_if_name} vid 1
            ip netns exec ${bridge_ns_name} bridge vlan add dev ${peer2_if_name} vid ${vlan_vid} pvid ${vlan_vid}
        }
        ```


4. **Python Tool for Ethernet Frames**: A utility (`ethsend`) for sending raw Ethernet frames. Create a file named `ethsend.py` and use the following code:

    ```python
    import fcntl
    import socket
    import struct
    import sys

    def send_frame(if_name, dstmac, eth_type, payload):
        # Open raw socket and bind it to network interface.
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        s.bind((if_name, 0))

        # Get source interface's MAC address.
        info = fcntl.ioctl(s.fileno(),
                            0x8927,
                            struct.pack('256s', bytes(if_name, 'utf-8')[:15]))
        srcmac = ':'.join('%02x' % b for b in info[18:24])

        # Build Ethernet frame
        payload_bytes = payload.encode('utf-8')
        assert len(payload_bytes) <= 1500  # Ethernet MTU

        frame = human_mac_to_bytes(dstmac) + \
                human_mac_to_bytes(srcmac) + \
                eth_type + \
                payload_bytes

        # Send Ethernet frame
        return s.send(frame)

    def human_mac_to_bytes(addr):
        return bytes.fromhex(addr.replace(':', ''))

    def main():
        if_name = sys.argv[1]
        dstmac = sys.argv[2]
        payload = sys.argv[3]
        ethtype = b'\x7A\x05'  # arbitrary, non-reserved
        send_frame(if_name, dstmac, ethtype, payload)

    if __name__ == "__main__":
        main()
    ```



## **How VLAN Is Implemented**

To split a single L2 network segment into multiple non-intersecting sub-segments without any rewiring a technique called frame tagging is used. 

![](./images/2.svg)

In standard Ethernet frames, VLAN tagging adds an extra 4-byte field to identify VLAN membership. This field is inserted between the Source MAC and EtherType fields. The 4 bytes include a reserved value (`0x8100`) to mark the frame as VLAN-tagged and a 12-bit VLAN ID to specify the VLAN.

![](./images/3.svg)

The VLAN tag slightly modifies the Ethernet frame structure. While the payload's minimum size is reduced by 4 bytes, the maximum frame size increases by 4 bytes. This tagging allows switches to logically segment traffic by VLAN and ensure proper data routing across access and trunk links.

Tagging occurs on trunk links to carry multiple VLANs, while switches remove tags when frames are forwarded to devices connected to access ports. This mechanism enables logical network separation over the same physical infrastructure.



There is more than one way to tag frames.
 In this lab, the tagging is transparent to the end nodes and fully implemented by the bridge.


## **Step-by-Step Process**

### **1. Create a Network Namespace with a Bridge Device**

The first step is to create a new network namespace containing a Linux bridge (`br1`). This bridge will handle VLAN tagging and filtering.

```bash
create_new_bridge bridge1 br1
```


- `create_new_bridge`: Script to set up a namespace (`bridge1`) with a bridge device (`br1`).
- Enables VLAN filtering on the bridge.



### **2. Create End Hosts for VLAN 10**

Next, create end hosts connected to the bridge and assign them to VLAN 10.

```bash
create_new_node host10 eth10 10 bridge1 br1
create_new_node host11 eth11 10 bridge1 br1
create_new_node host12 eth12 10 bridge1 br1
```

- `host10`, `host11`, and `host12` are namespaces representing end hosts.
- `eth10`, `eth11`, and `eth12` are veth interfaces connected to the bridge.
- VLAN ID `10` is assigned to isolate these hosts.



### **3. Create End Hosts for VLAN 20**

Similarly, create another set of end hosts connected to the bridge but assign them to VLAN 20.

```bash
create_new_node host20 eth20 20 bridge1 br1
create_new_node host21 eth21 20 bridge1 br1
create_new_node host22 eth22 20 bridge1 br1
```

- `host20`, `host21`, and `host22` are connected to the same bridge (`br1`).
- VLAN ID `20` ensures traffic isolation from VLAN 10.



### **4. Monitor Network Traffic**

Open multiple terminal tabs to monitor traffic in each VLAN using `tcpdump`.

**For VLAN 10:**

```bash
# On host11
nsenter --net=/var/run/netns/host11 tcpdump -i eth11 ether proto 0x7a05
```

```bash
# On host12
nsenter --net=/var/run/netns/host12 tcpdump -i eth12 ether proto 0x7a05
```

**For VLAN 20:**

```bash
# On host21
nsenter --net=/var/run/netns/host21 tcpdump -i eth21 ether proto 0x7a05
```

```bash
# On host22
nsenter --net=/var/run/netns/host22 tcpdump -i eth22 ether proto 0x7a05
```

- `nsenter` allows entering a network namespace to monitor traffic.
- `tcpdump` captures traffic on specific interfaces.



### **5. Send Broadcast Frames**

Use the `ethsend` tool to send broadcast frames from the first host of each VLAN.

**For VLAN 10:**

```bash
# From host10
nsenter --net=/var/run/netns/host10 ethsend eth10 ff:ff:ff:ff:ff:ff 'Hello VLAN 10!'
```

**For VLAN 20:**

```bash
# From host20
nsenter --net=/var/run/netns/host20 ethsend eth20 ff:ff:ff:ff:ff:ff 'Hello VLAN 20!'
```

- Sends a broadcast message (`Hello VLAN 10!` or `Hello VLAN 20!`) to all hosts in the respective VLAN.
- Hosts in different VLANs will not receive each other’s messages.



### **6. Validate VLAN Isolation**

Inspect the output of `tcpdump` in each terminal. Ensure that:
- Frames sent from VLAN 10 hosts are only received by other VLAN 10 hosts.
- Frames sent from VLAN 20 hosts are only received by other VLAN 20 hosts.

This confirms that VLANs provide effective traffic isolation.



### **7. Cleanup**

After completing the lab, remove the created namespaces to clean up the environment.

```bash
ip netns delete bridge1

ip netns delete host10
ip netns delete host11
ip netns delete host12

ip netns delete host20
ip netns delete host21
ip netns delete host22
```

- Deletes all namespaces created during the lab.



## **Conclusion**

In this lab, we successfully configured VLANs using a Linux bridge. We learned how to:
- Set up namespaces and bridges for VLAN functionality.
- Assign VLAN IDs to isolate traffic.
- Verify VLAN isolation using traffic monitoring and broadcast testing.

This exercise highlights the power of VLANs in segmenting a single broadcast domain into isolated subdomains, ensuring efficient and secure network communication.

