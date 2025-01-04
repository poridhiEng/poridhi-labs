# Networking Fundamentals Starting from LAN to VXLAN

## What is a LAN?

LAN is a local area network. It is a network that connects computers and other devices together within a limited area, such as a home, school, or office building. It is a network of computers and other electronic devices that are all located in the same physical area. The purpose of LAN is to allow computers and other peripherals located in the same area to connect and exchange information with one another easily.

**Key characteristics of a LAN include:**

- High data transfer speeds (typically 100Mbps to 10Gbps)
- Low latency since devices are physically close
- Direct physical connections via Ethernet cables or Wi-Fi
- Controlled by a single organization

### LAN Communication in a Small Office  

**Scenario Description:** 

![alt text](./images/Lan.svg)

In a small office, three devices are connected to a Local Area Network (LAN):  
- **Computer A** (IP: 192.168.1.10)  
- **Computer B** (IP: 192.168.1.11)  
- **Network Printer** (IP: 192.168.1.20)  

These devices communicate through a central switch using Ethernet cables, all configured within the same subnet: `192.168.1.0/24`. The following examples illustrate practical LAN communication scenarios in this setup.

#### **Example 1: Computer A Communicates with the Network Printer** 

**Task:** Computer A sends a document to the printer for printing. 

![alt text](./images/lan-01.svg)

**Steps:**  
1. **Network Check:** Computer A verifies that the printer’s IP address (192.168.1.20) is within the same subnet.  
2. **Address Resolution:**  
   - Computer A uses the Address Resolution Protocol (ARP) to find the printer’s MAC address.  
   - It broadcasts a message: “Who has IP 192.168.1.20?”  
   - The printer responds with its MAC address: `00:1B:44:11:3A:B7`.  
3. **Data Transfer:** Computer A sends the print data to the printer, addressing it by its MAC address.  

#### **Example 2: File Sharing Between Computers**  

**Task:** Computer A shares a file with Computer B.  

![alt text](./images/lan-02.svg)

**Steps:**  
1. **Connection Setup:**  
   - Computer A initiates a connection to Computer B using its IP address (192.168.1.11).  
2. **Address Resolution:** ARP resolves Computer B’s MAC address.  
3. **Data Transmission:**  
   - The file is divided into packets and sent to the switch.  
   - The switch forwards the packets to Computer B based on its MAC address.  
4. **Acknowledgment:** Computer B receives the packets and acknowledges receipt, completing the transfer.  

#### **Role of the Switch in LAN Communication**  
The switch facilitates efficient communication by:  
- Maintaining a **MAC address table** that maps devices to specific switch ports.  
- **Forwarding frames** only to the intended recipient’s port, reducing unnecessary traffic.  

**Example:**  
If Computer A sends data to the printer:  
1. The switch receives the frame from Computer A.  
2. It checks the MAC address table to identify the port associated with the printer’s MAC address.  
3. The frame is forwarded to the printer’s port, while other devices on the network remain unaffected.  

