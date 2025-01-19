# Observing Address Resolution Protocol (ARP) in Action

This lab will help you understand the Address Resolution Protocol (ARP) through practical experimentation using Linux network namespaces. By the end, you'll have hands-on experience with how ARP operates in real networks.

## Prerequisites

- **Linux system** with root access or sudo privileges
- Basic understanding of IP networking
- `iproute2` tools installed (usually included in Linux distributions)
- `tcpdump` for packet capture

## Task Overview

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/47288166c8e72883133a1a5acfea8067d18142cb/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/ARP-01%20(1).svg)

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

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image.png)

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

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-1.png)

3. Check ARP cache again

    ```bash
    sudo ip netns exec ns1 ip neigh show
    ```

    This should now show the ARP entry for `192.168.1.2` with the corresponding MAC address sent by `ns2`.

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-3.png)

### Example tcpdump Output

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/47288166c8e72883133a1a5acfea8067d18142cb/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/ARP-02%20(1).svg)

In the `tcpdump` window, you should see something like:

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-2.png)

### Understand What's Happening?

This output shows ARP communication on `veth2` in `ns2`.  

- `192.168.1.1` sends a broadcast request asking for the MAC address of `192.168.1.2`, which replies with its MAC (`12:d6:fd:8f:7f:c2`).  
- Similarly, `192.168.1.2` requests the MAC of `192.168.1.1`, which replies with its MAC (`ea:93:63:ff:d8:dc`).  

This exchange allows both IPs to resolve each other's MAC addresses for communication.

## Advanced Experiments

### **Experiment 1: Watch ARP Cache Timing**

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/47288166c8e72883133a1a5acfea8067d18142cb/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/ARP-03%20(1).svg)

Observe how long ARP entries remain in the cache.

1. **Clear the cache again**

    ```bash
    sudo ip netns exec ns1 ip neigh flush all
    ```

2. **Ping from ns1 to ns2**

    ```bash
    sudo ip netns exec ns1 ping -c 1 192.168.1.2
    ```

3. **Monitor the ARP cache**

    ```bash
    sudo ip netns exec ns1 watch -n 1 'ip neigh show'
    ```

    This command runs the `ip neigh show` command every second (-n 1).

    - Displays the ARP cache entries in the ns1 namespace in real-time.
    - Immediately after the ping, you will see an entry like:

        ```bash
        192.168.1.2 dev veth1 lladdr aa:bb:cc:dd:ee:ff REACHABLE
        ```

        ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-4.png)

    - Over time, the state may change to STALE, depending on the kernel's ARP cache timeout.

4. **Wait for the Entry to Transition to `STALE`**

    - ARP entries remain in the `REACHABLE` state for a certain timeout period (default: 30 seconds in Linux).
    - After this period, the state changes to `STALE` if no further communication occurs.
    - Keep monitoring the cache using the `watch` command, and after the timeout, you will see:

        ```bash
        192.168.1.2 dev veth1 lladdr aa:bb:cc:dd:ee:ff STALE
        ```

        ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-5.png)

5. **Access the STALE Entry**

    - Open another terminal and send another ping to access the `STALE` entry:

        ```bash
        sudo ip netns exec ns1 ping -c 1 192.168.1.2
        ```

    - The ARP entry will transition back to `REACHABLE` after the ping:

        ```bash
        192.168.1.2 dev veth1 lladdr aa:bb:cc:dd:ee:ff REACHABLE
        ```

        ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-6.png)

### **Experiment 2: Force ARP Updates**

In this experiment, you will manually delete and add ARP entries and verify the changes in the ARP cache.

1. **Retrieve the Current MAC Address**:

    Before manually adding an ARP entry, ensure you have the correct MAC address of `veth2` in the `ns2` namespace. Check the MAC Address of `veth2` using:

   ```bash
   sudo ip netns exec ns2 ip link show veth2
   ```
   - Look for the `link/ether` field in the output, which will display the MAC address (e.g., `aa:bb:cc:dd:ee:ff`).

   ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-7.png)

2. **Delete the Existing ARP Entry**:

    To remove the current ARP entry for `192.168.1.2` in the `ns1` namespace:

    ```bash
    sudo ip netns exec ns1 ip neigh del 192.168.1.2 dev veth1
    ```

    - **Verify Deletion:**

        ```bash
        sudo ip netns exec ns1 ip neigh show
        ```
        The entry for `192.168.1.2` should no longer appear in the ARP cache.

3. **Manually Add an ARP Entry**:

    Using the MAC address retrieved in Step 1, manually add the ARP entry:

    ```bash
    sudo ip netns exec ns1 ip neigh add 192.168.1.2 lladdr aa:bb:cc:dd:ee:ff dev veth1
    ```

    Replace `aa:bb:cc:dd:ee:ff` with the actual MAC address of `veth2`.

4. **Verify the Manually Added ARP Entry**:

    Check that the new ARP entry has been added successfully:

    ```bash
    sudo ip netns exec ns1 ip neigh show
    ```

    You should see an entry like this:

    ![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/refs/heads/main/Poridhi%20Labs/CN%20Fundamentals/Lab%2006/images/image-8.png)

    Manually added entries are marked as `PERMANENT`, meaning they will not time out or transition to `STALE` automatically.

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
- How to experiment with ARP cache timing and manual updates.

This hands-on approach provides a deeper understanding of ARP and its role in local network communication. Keep experimenting and exploring to solidify your networking skills!

