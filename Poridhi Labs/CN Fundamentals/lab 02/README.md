# Bridge vs Switch: A deeper dive

Networking devices are essential components that enable communication between different nodes in a network. They operate at various layers of the OSI model and perform specific tasks to ensure efficient data flow. Common networking devices include:  

1. **Switches:** Operate at Layer 2 (Data Link Layer) to connect multiple devices within a local area network (LAN). Switches forward frames based on MAC addresses.  
2. **Bridges:** Logical devices that interconnect multiple network segments at Layer 2, creating a single broadcast domain while filtering traffic to improve performance.  
3. **Routers:** Operate at Layer 3 (Network Layer) to route packets between different networks. Routers use IP addresses to determine the best path for forwarding data.  

These devices form the backbone of modern networks, ensuring seamless communication and data exchange.

---

## **Bridge and Switch: A Detailed Perspective**

### **What is a Bridge?**  
A **bridge** is a logical function that transparently connects multiple network nodes into a single Layer 2 segment or broadcast domain. It enables devices within the domain to exchange data link layer frames using either unicast (MAC) or broadcast communication. From the perspective of network participants, bridges are invisible, as they operate transparently, forwarding Ethernet frames based on learned MAC addresses. Bridges can also interconnect smaller sub-segments, extending the segment size.

### **What is a Switch?**  
A **switch** is the physical implementation of the bridge function. It connects multiple devices in a network and manages the forwarding of Ethernet frames based on MAC addresses. Switches are more advanced than traditional bridges, offering higher performance, multiple ports, and features like VLANs for network segmentation. Essentially, a switch performs the same role as a bridge but with greater efficiency and scalability.


## **Network Switch AKA Bridge**

The main point is that a **bridge** and a **switch** essentially perform the same function at the **data link layer (Layer 2)** of the OSI model. However, the terms differ in their usage and context:

![](./images/lab2-2.drawio.svg)

**1. Bridge as a Logical Function:**

- A **bridge** is the **logical function** of connecting network nodes within the same broadcast domain. 
- It operates at Layer 2 and `transparently` forwards `Ethernet` frames based on their MAC addresses.

**2. Switch as a Physical Device:**

- A **switch** is the **physical hardware device** that implements this logical bridging function. 
- It uses specialized hardware to process and forward frames faster and more efficiently.

## **What Does a Bridge (or Switch) Do?**

### **1. Combining Network Nodes into Broadcast Domains:**

- A bridge connects devices (nodes) within a single **Layer 2 broadcast domain**. 
- Within this domain:
  - Devices can communicate with each other using **unicast** (specific MAC address)

    ![](./images/lab2-3.drawio.svg)

  - Devices can communicate with each other using **broadcast** (all devices in the domain).

    ![](./images/lab2-4.drawio.svg)

### **2. Transparent Operation:**

Transparent operation refers to the way certain networking devices, like bridges and switches, function without being visible or detectable to the devices connected to the network. 

- Bridges and switches operate at Layer 2 (Data Link Layer) and forward data frames without the source or destination devices being aware of their presence.
- Devices on the network "see" each other directly, not the bridge or switch in between.

### **3. Learning and Forwarding:**

- Bridges and switches dynamically learn the MAC addresses of connected devices by inspecting the source address of incoming frames.
- They maintain a MAC address table (also called a forwarding table) to associate each address with the appropriate port.

### **4. Selective Forwarding:**

- Bridges and switches forward frames selectively based on the destination MAC address.
- If the destination MAC address is not in the MAC address table, the frame is broadcast to all connected devices.

---

### **Extending Network Segments with Bridges**

In networking, **extending network segments** means increasing the size or reach of a local network at the **Data Link Layer (Layer 2)**. Bridges achieve this by connecting separate parts of the network (end-nodes or sub-segments) into a single cohesive broadcast domain.

![](./images/lab2-5.drawio.svg)

### **1. Connecting End-Nodes**  
Bridges can connect individual devices, such as:  
- Computers  
- Printers  

**How It Works:**  
- A bridge has multiple ports, each connected to a different device.  
- When a device sends a frame, the bridge receives it and examines the frame's destination MAC address.  
- The bridge forwards the frame to the port where the destination device is connected (based on its MAC address table).  
- If the destination device is unknown, the frame is broadcasted to all ports, except the one it was received on.

**Benefit:**  
Devices connected via the bridge operate as if they were part of the same physical network segment, allowing seamless communication.

---

### **2. Connecting Sub-Segments**  
A sub-segment is a smaller network that may consist of:  
- Groups of end-nodes (e.g., computers in a department).  
- Other network devices like switches or even other bridges.

**How It Works:**  
- Bridges can connect one segment of a network to another, effectively extending the network.  
- For instance, one bridge can connect two different LANs, merging them into a single Layer 2 segment.  
- This creates a larger network where all devices can communicate as if they are part of the same broadcast domain.

**Example:**  
- **Bridge 1** connects a group of computers.  
- **Bridge 2** connects another group of devices.  
- Connecting Bridge 1 and Bridge 2 links these two sub-segments into a larger network.

**Benefit:**  
This hierarchical connectivity allows networks to scale by linking smaller segments without requiring them all to be directly connected to a central switch or router.

## **Top-of-Rack (TOR) Switch**

A **Top-of-Rack (TOR) switch** is a key networking device in modern data centers. It’s located physically at the top of a server rack (hence the name) and serves as the primary point of connection for all servers in that rack. Its design simplifies cabling, optimizes performance, and integrates seamlessly into the broader data center network.

### **What Roles Does a TOR Switch Serve?**

The TOR switch is multifunctional, fulfilling roles in both Layer 2 (L2) and Layer 3 (L3) of the OSI model:

**1. Layer 2 (L2) Bridge Role:**

- Acts as a transparent multi-port bridge, meaning it facilitates communication within the rack at the data link layer.
- Operates based on MAC (Media Access Control) addresses, forwarding Ethernet frames between servers without involving IP routing.
- Ensures that all devices in the rack belong to the same broadcast domain (a group of devices that can reach each other via L2 broadcasts).
- Key features:
    - **MAC Learning:** Dynamically learns which MAC address resides on which port.
    - **Frame Forwarding:** Directs traffic between servers in the rack based on MAC tables.

    ![](./images/lab2-6.drawio.svg)

**2. Layer 3 (L3) Router Role:**

- Some ports on the TOR switch are configured as Layer 3 interfaces. These ports handle traffic leaving the rack, forwarding it to other subnets or networks.
- Operates based on IP routing, directing packets between different subnets using routing tables.
- Acts as the **default gateway** for all servers in the rack, meaning all traffic destined for external networks flows through it.

    ![](./images/lab2-7.drawio.svg)

### **Why is it Called a TOR Switch?**

- **Physical Location:** Positioned at the top of the rack for easy cable management. All servers connect to this single switch using short cables.
- **Logical Organization:** Forms the "top" of the rack’s networking hierarchy, interfacing with higher-level devices.

---

## **TOR Switch and Rack Design**

### **Rack Networking Structure**

A typical data center rack consists of:
- **Servers:** Physical machines performing computations or hosting applications.
- **TOR Switch:** Connecting all servers within the rack and linking the rack to the larger data center network.

### **Network Segmentation**

- All servers in the rack belong to the same **IP subnet** (e.g., `/24`, meaning up to 254 usable addresses).
- The subnet boundary ensures that L2 (frame-based) communication stays within the rack.
- The TOR switch ensures that:
  - **Intra-rack communication** (between servers in the same rack) remains in L2 mode.
  - **Inter-rack communication** (between servers in different racks) is routed through L3.

### **How TOR Switches Operate**
- **L2 Mode:**  
  TOR switches handle intra-rack traffic as a transparent bridge. Servers in the rack communicate directly using their MAC addresses, without involving higher-layer switches.
- **L3 Mode:**  
  One or more ports on the TOR switch operate in L3 mode to connect the rack's subnet to the broader network. These ports:
  - Have IP addresses and act as nodes in the L3 topology.
  - Route traffic to "distribution layer" switches for internetworking.
- **Distribution Layer Switches:**  
  - These higher-layer switches connect multiple TOR switches.
  - They work as pure L3 routers with many ports (48, 64, or more), each assigned an IP address.
  - Provide redundancy and scalability by connecting to multiple TOR switches.

---

### **Physical and Logical Design**
- **Physical Connections:**
  - Each TOR switch connects to at least two distribution switches for redundancy and increased throughput.
  - If multiple physical links are bundled into a single logical connection (e.g., using link aggregation), network performance improves significantly.
- **Logical Configuration:**
  - TOR switches combine bridging and routing capabilities:
    - A bridge (with many L2 ports) connects servers within the rack.
    - A router (with fewer L3 ports) connects the rack to the distribution layer.

---

### **Management and Configuration**
- **Out-of-Band Ports:**
  - Switches include dedicated out-of-band management ports (always in L3 mode).
  - These ports allow administrators to log in remotely (e.g., via SSH) and manage the switch, even if other ports are misconfigured.
- **Switch OS:**
  - Internally, many modern switches run Linux, FreeBSD, or Unix-like operating systems.
  - Administrators can manage them using familiar tools (e.g., `ip`, `bridge`) to configure routing tables, assign IPs, or enslave ports to virtual bridges.
- **Perspective:**  
  - A managed switch is essentially a highly optimized Linux server with multiple network interfaces.

---

### **Extending Beyond the Physical Network**
- **Broadcast Domains:**
  - While physical broadcast domains are confined to a single rack, technologies like **VXLAN (Virtual Extensible LAN)** can span multiple racks or L3 networks.
  - VXLAN creates an **overlay network**, enabling flexibility for end-user use cases.

This section emphasizes that while TOR switches act as bridges and routers, their configuration determines their function. Moreover, advanced tools like VXLAN extend the functionality beyond physical limitations, offering scalable and flexible networking solutions in modern data centers.


