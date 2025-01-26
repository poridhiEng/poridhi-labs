# Networking Basics

Networking is the foundation of modern communication. It allows devices to exchange data efficiently and securely, enabling everything from browsing the web to video calls. This lab focuses on breaking down complex networking concepts such as packets, frames, TCP/IP, UDP, and ports with some real-world examples.

## Objective
The goal of this lab is to provide a clear understanding of the essential components of data communication in a network. By the end of this lab, you will:

1. Understand what packets and frames are.
2. Learn how TCP/IP works and ensures secure communication.
3. Differentiate between TCP and UDP protocols.
4. Recognize the importance of ports in organizing network communication.

## Packets and Frames

To understand how data travels across a network, imagine sending a letter in the mail. When you mail a letter, it is placed inside an envelope with the recipient’s address written on it. In networking, this letter represents the data you want to send, and the envelope is the packet. A packet contains not only the data but also important information like the sender’s and receiver’s addresses, ensuring it reaches the right destination. Packet are encapsulated with the necessary addressing information like source and destination IP addresses and ports.

![](./images/packetandframe.svg)

Frames are small units of data used for communication within a local network, like your home Wi-Fi or office Ethernet. They contain the data being sent, along with important information like the sender and receiver's MAC addresses. Frames ensure that data travels efficiently between devices within the same network. They work within the Data Link Layer of the OSI model and are essential for local communication. Frames encapsulate packets by adding MAC addressing information.


This process of wrapping data with the necessary addressing information is called encapsulation. It ensures that data, no matter how large, is split into manageable pieces and routed correctly to its destination. This also helps reduce congestion and bottlenecks, making communication faster and more reliable.

## TCP/IP

TCP/IP, or Transmission Control Protocol/Internet Protocol, is the backbone of the internet. It is a set of rules or protocols that define how data is sent, transmitted, and received across networks. Think of TCP/IP as a translator that ensures devices with different hardware and software can communicate seamlessly.

TCP/IP is a more shorter version of OSI model. In OSI model, there are 7 layers and in TCP/IP model, there are 4 layers. Some of the layers are combined in TCP/IP model. TCP/IP is more popular than OSI model because it is more practical and easier to understand.

![](./images/osivstcp.svg)


TCP/IP works through a process called encapsulation, where data is wrapped with headers containing critical information as it moves through four layers: Application, Transport, Internet, and Network Interface. These layers work together to ensure the data reaches its destination correctly.

### Application Layer

The Application Layer of TCP/IP model is the same as the Application Layer of OSI model. It is the layer that interacts with the user. It is responsible for providing services to the user. It act as the sum of the OSI model's Application, Presentation, and Session layers. 

### Transport Layer

The Transport Layer of TCP/IP model is the same as the Transport Layer of OSI model. It is the layer that ensures the data is delivered to the correct destination. It is responsible for providing services to the user. It act as the sum of the OSI model's Transport Layer. It uses protocols like TCP and UDP.

### Internet Layer

The Internet Layer of TCP/IP model is the same as the Network Layer of OSI model. It is the layer that ensures the data is delivered to the correct destination. It is responsible for providing services to the user. It act as the sum of the OSI model's Network Layer. It uses protocols like IP, ICMP, ARP, RARP, etc.

### Network Access Layer

The Network Access Layer of TCP/IP model is the same as the Data Link Layer of OSI model. It is the layer that ensures the data is delivered to the correct destination. It is responsible for providing services to the user. It act as the sum of the OSI model's Data Link Layer.

### Why is TCP Secure?

One of the key features of TCP is its reliability. Before any data is sent, TCP establishes a connection between the sender and receiver through a process called the **Three-way Handshake**. This ensures both devices are synchronized and ready to communicate. 

![](./images/1.svg)

To establish a connection, the client sends a `SYN` message to the server. The server responds with a `SYN-ACK` message. Then the client sends an `ACK` message to the server. This is because TCP is a connection-oriented protocol and requires a response. Now the connection is established and data can be sent.

Once the data is sent, TCP checks that all packets have arrived and reassembles them in the correct order. If any packet is missing or corrupted, it is resent. This makes TCP a secure and reliable protocol for tasks like downloading files or sending emails.

### TCP Segment

After establishing a connection, the data is sent in smaller chunks, and each chunk is wrapped in a TCP segment that includes the TCP header and the data payload. Each segment is wrapped in a TCP header and data payload. 20-60 bytes for the TCP header + up to 1460 bytes of data (in most cases). 

![](./images/new.svg)

The TCP header contains the source and destination ports, sequence number, acknowledgment number, header length, reserved, flags, window size, checksum, and urgent pointer. 

![](./images/2.svg)

- **Source Port**: The 16-bit address of the port sending the data.
- **Destination Port**: The 16-bit address of the port receiving the data.
- **Sequence Number**: Tracks the position of data in the session.
- **Acknowledgment Number**: Acknowledges receipt of data. If segment 'x' is received, the acknowledgment will be 'x+1'.
- **HLEN (Header Length)**: Specifies the size of the header in 4-byte chunks. The header size ranges from 20 bytes (5 chunks) to 60 bytes (15 chunks).
- **Reserved**: 4 bits set to 0 for future use.
- **Flags (Control Bits)**:
  - **URG**: Urgent data is present.
  - **ACK**: Indicates acknowledgment is included in the packet.
  - **PSH**: Requests immediate delivery of data to the application without buffering.
  - **RST**: Requests to reset the connection.
  - **SYN**: Initiates a connection.
  - **FIN**: Closes a connection.
- **Window Size**: A 16-bit field that specifies how much data the receiver can handle. Helps with flow control.
- **Checksum**: A 16-bit mandatory field to check for errors in the segment.
- **Urgent Pointer**: Points to urgent data when the URG flag is set. It adds to the sequence number to locate the last urgent byte.
- **Options**: Extra features, stored in 32-bit units. If less than 32 bits, padding is added to make up the difference.

### TCP Connection Close

For closing a TCP connection, the client will send a `FIN` message to the server. The server will respond with a `ACK` message. Then the server will send a `FIN` message to the client. The client will respond with a `ACK` message. This is because TCP is a connection-oriented protocol and requires a response.

![](./images/tcpclose.svg)


## User Datagram Protocol (UDP)

UDP, or User Datagram Protocol, is another protocol used for sending data across networks. Unlike TCP, UDP is connectionless, meaning it does not establish a handshake before transmitting data. This makes it much faster but less reliable. There is no gurantee of delivery of packets. Some packets may be lost or corrupted.

Imagine streaming a live video. If a small amount of data is lost during the stream, it’s better to keep playing the video rather than pausing to recover the lost data. This is where UDP shines. It’s ideal for applications where speed is more important than accuracy, such as online gaming, video streaming, or voice calls.

### Why is UDP Unreliable?

UDP is unreliable because it does not require a response. This means that if a packet is lost, there is no way to know if it was received. This can lead to data loss, especially in real-time applications like video streaming.

![](./images/udp.svg)

### UDP Header

UDP header is 8 bytes long. It contains the source and destination ports, length, and checksum. It is much simpler than the TCP header, making it faster to process. 

![](./images/new2.svg)

**Source Port (2 bytes)**: Identifies the sending application.  
**Destination Port (2 bytes)**: Identifies the receiving application.  
**Length (2 bytes)**: Total size of the UDP packet (header + data).  
**Checksum (2 bytes)**: Ensures data integrity using the header, pseudo-header, and data.


## Key Differences Between TCP and UDP

| **Feature**       | **TCP**                                | **UDP**                     |
|-------------------|----------------------------------------|-----------------------------|
| Connection        | Connection-oriented (requires handshake). | Connectionless (no handshake). |
| Reliability       | Ensures reliable data delivery.        | No guarantee of delivery.   |
| Speed             | Slower due to reliability checks.      | Faster, suitable for real-time data. |
| Use Case          | File transfers, emails, web browsing.  | Video streaming, gaming, VoIP. |

## Ports

Ports are essential for organizing and directing data on a network. Think of a port as a specific docking point for data on a device. Each port is assigned a number, ranging from 0 to 65535, and is used to identify specific applications or services.

For example, when you browse a website, your browser communicates with the server using port 80 for HTTP or port 443 for HTTPS. Similarly, when you log into a remote server using SSH, port 22 is used. These standard port numbers ensure that devices and applications know how to interact with each other.

| **Protocol**                 | **Port Number** | **Description**                                          |
|------------------------------|-----------------|--------------------------------------------------------|
| File Transfer Protocol (FTP) | 21              | Transfers files between a client and server.           |
| Secure Shell (SSH)           | 22              | Securely logs into systems via a text-based interface. |
| HyperText Transfer Protocol (HTTP) | 80       | Loads web pages and content.                          |
| HTTPS                        | 443             | Secure version of HTTP using encryption.              |
| Remote Desktop Protocol (RDP)| 3389            | Connects to remote desktops.                          |

Ports help manage network traffic efficiently. Without them, a device would struggle to determine which application should handle incoming data. By using a system of standard ports, networking remains organized and consistent.

## Conclusion

Understanding networking concepts like packets, frames, TCP/IP, UDP, and ports is essential for appreciating how data travels across networks. Packets and frames break down large messages into manageable pieces, while protocols like TCP and UDP define how this data is transmitted. Ports ensure that data reaches the correct application, keeping communication organized. Together, these components form the foundation of reliable and efficient networking, enabling the seamless connectivity we rely on every day.

