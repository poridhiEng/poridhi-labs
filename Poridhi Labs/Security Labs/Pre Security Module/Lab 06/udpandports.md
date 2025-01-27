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
