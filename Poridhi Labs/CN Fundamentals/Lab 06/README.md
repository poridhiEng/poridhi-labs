# Understanding ARP: A Hands-on Tutorial with Network Namespaces

This lab will help you understand the Address Resolution Protocol (ARP) through practical experimentation using Linux network namespaces. By the end, you'll have hands-on experience with how ARP operates in real networks.

## Prerequisites

- **Linux system** with root access or sudo privileges
- Basic understanding of IP networking
- `iproute2` tools installed (usually included in Linux distributions)
- `tcpdump` for packet capture

## Task Overview

In this lab, we will:
1. Create two isolated network namespaces connected by a virtual ethernet link.
2. Observe ARP in action when these namespaces communicate.
3. Experiment with ARP cache timing and manual ARP updates.

This setup mimics two computers connected on a local network.

## Setting Up the Environment

### Step 1: Create Network Namespaces

Network namespaces allow you to create isolated network environments on a single Linux machine.

```bash
# Create two network namespaces
sudo ip netns add ns1
sudo ip netns add ns2

# Verify creation
sudo ip netns list
```

**Expected Output:**
```
ns2
ns1
```

### Step 2: Create Virtual Network Interfaces

A virtual ethernet pair acts as a direct connection between two network namespaces.

```bash
# Create a virtual ethernet pair
sudo ip link add veth1 type veth peer name veth2

# Move interfaces to respective namespaces
sudo ip link set veth1 netns ns1
sudo ip link set veth2 netns ns2
```

#### Why is this step important?

Network namespaces are isolated networking environments. Each namespace has its own network interfaces, routing tables, and ARP tables. By moving the veth interfaces into specific namespaces, we connect these isolated environments, enabling communication between them.

In this setup:
- `ns1` has `veth1`, which will serve as its network interface.
- `ns2` has `veth2`, which will serve as its network interface.
- Communication between `ns1` and `ns2` will happen via this veth pair.


### Step 3: Configure IP Addresses

Assign IP addresses to the virtual interfaces and bring them up.

1. Configure IP addresses for `ns1` and `ns2`

    ```bash
    # Configure IP for ns1
    sudo ip netns exec ns1 ip addr add 192.168.1.1/24 dev veth1

    # Configure IP for ns2
    sudo ip netns exec ns2 ip addr add 192.168.1.2/24 dev veth2
    ```

    These commands assign IP addresses (`192.168.1.1/24` and `192.168.1.2/24`) to the virtual Ethernet interfaces (`veth1` and `veth2`) inside the network namespaces `ns1` and `ns2`, respectively.

2. Bring up the interfaces  

    ```bash
    sudo ip netns exec ns1 ip link set dev veth1 up
    sudo ip netns exec ns2 ip link set dev veth2 up
    ```

    By default, network interfaces are created in a down state (inactive). These commands bring up the `veth1` and `veth2` interfaces, making them active and ready to send/receive packets.


3. Enable loopback interfaces

    ```bash
    sudo ip netns exec ns1 ip link set dev lo up
    sudo ip netns exec ns2 ip link set dev lo up
    ```

    The loopback interface (`lo`) is a virtual network interface present in all Linux systems, used for internal communication within a namespace or system, such as accessing services on `127.0.0.1`. These commands activate the loopback interface in the `ns1` and `ns2` network namespaces, enabling internal communication within each namespace.

## Observing ARP in Action

### Step 1: Clear ARP Caches

Clear the ARP caches in both namespaces to ensure we start with a clean state.

```bash
# Clear ARP cache in both namespaces
sudo ip netns exec ns1 ip neigh flush all
sudo ip netns exec ns2 ip neigh flush all
```

### Step 2: Set Up Packet Capture

Open a new terminal window to capture ARP packets in `ns2`.

```bash
sudo ip netns exec ns2 tcpdump -i veth2 arp
```

### Step 3: Trigger ARP Process

In your original terminal, trigger the ARP process by pinging `192.168.1.2` from `ns1`.

1. Check initial ARP cache

    ```bash
    sudo ip netns exec ns1 ip neigh show
    ```

    This should show an empty ARP cache because we cleared it earlier.

2. Ping from ns1 to ns2

    ```bash
    sudo ip netns exec ns1 ping -c 1 192.168.1.2
    ```

    This sends an ARP request to `ns2` to find the MAC address for `192.168.1.2`.

3. Check ARP cache again

    ```bash
    sudo ip netns exec ns1 ip neigh show
    ```

    This should now show the ARP entry for `192.168.1.2` with the corresponding MAC address sent by `ns2`.

### Example tcpdump Output

In the `tcpdump` window, you should see something like:

```
12:00:00.123456 ARP, Request who-has 192.168.1.2 tell 192.168.1.1, length 28
12:00:00.123457 ARP, Reply 192.168.1.2 is-at aa:bb:cc:dd:ee:ff, length 28
```

### Understand What's Happening?

This output shows ARP communication on `veth2` in `ns2`.  

- `192.168.1.1` sends a broadcast request asking for the MAC address of `192.168.1.2`, which replies with its MAC (`f2:07:c7:c9:f7:f4`).  
- Similarly, `192.168.1.2` requests the MAC of `192.168.1.1`, which replies with its MAC (`82:c7:2f:8d:8d:c1`).  

This exchange allows both IPs to resolve each other's MAC addresses for communication.

## Advanced Experiments

### Experiment 1: Watch ARP Cache Timing

Observe how long ARP entries remain in the cache.

```bash
# Clear the cache again
sudo ip netns exec ns1 ip neigh flush all

# Monitor the ARP cache
sudo ip netns exec ns1 watch -n 1 'ip neigh show'
```

### Experiment 2: Force ARP Updates

Manually delete and add ARP entries.

```bash
# Delete a specific ARP entry
sudo ip netns exec ns1 ip neigh del 192.168.1.2 dev veth1

# Manually add an ARP entry
sudo ip netns exec ns1 ip neigh add 192.168.1.2 lladdr aa:bb:cc:dd:ee:ff dev veth1
```

## Cleanup

When you are done experimenting, clean up the environment to avoid leaving unused namespaces or interfaces.

```bash
# Delete network namespaces (this also removes associated interfaces)
sudo ip netns del ns1
sudo ip netns del ns2
```

## Conclusion

In this lab, you learned:
- How to set up and use Linux network namespaces.
- How ARP operates, including request and reply mechanisms.
- How to capture and analyze ARP traffic using `tcpdump`.
- How to experiment with ARP cache timing and manual updates.

This hands-on approach provides a deeper understanding of ARP and its role in local network communication. Keep experimenting and exploring to solidify your networking skills!

