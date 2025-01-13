# Introduction to Gobuster and Its Functions

Gobuster is a powerful and flexible tool used in the field of offensive security for discovering hidden files, directories, DNS subdomains, and virtual hosts on a target system. This document provides a detailed overview of Gobuster, including its architecture, core functions, installation steps, and usage examples.

![](./images/banner2.svg)

## Objective
The primary goal of this lab is to introduce Gobuster, its architecture, and its functionality through a structured and practical approach. By the end of this lab, you will:
- Understand what Gobuster is and how it works.
- Learn about the different functions and options provided by Gobuster.
- Gain hands-on experience using Gobuster in a controlled environment.

## Architecture of Gobuster
Gobuster is designed to perform brute-forcing tasks efficiently by leveraging the following components:

1. **Target Specification**:
   - Allows specifying the target URL or domain.
   - Flexible enough to handle different protocols (HTTP, HTTPS).

2. **Wordlist Processing**:
   - Uses user-provided wordlists containing potential paths, file names, subdomains, or virtual hosts.

3. **Request Handling**:
   - Sends HTTP or DNS requests to the target for each wordlist entry.
   - Filters and reports results based on status codes, response sizes, or custom criteria.

4. **Concurrency**:
   - Utilizes multi-threading for faster execution.
   - Configurable thread count for optimal performance.

5. **Output Reporting**:
   - Provides both real-time and file-based output.
   - Supports verbose and filtered result formats.


## Functions of Gobuster
Gobuster offers multiple modes of operation tailored to different offensive security tasks:

### 1. Directory and File Brute-Forcing
Discover hidden directories and files on a web server.
#### Example:
```bash
gobuster dir -u http://example.com -w wordlist.txt
```
**Options:**
- `-x`: Specify file extensions (e.g., `.php`, `.html`).
- `-t`: Number of threads (default: 10).
- `-o`: Output results to a file.
- `-s`: Filter results by HTTP status codes.

### 2. DNS Subdomain Enumeration
Identify subdomains for a given domain.
#### Example:
```bash
gobuster dns -d example.com -w subdomains.txt
```
**Options:**
- `-r`: Specify a DNS server.
- `-z`: Skip wildcards.
- `-i`: Show IPs of discovered subdomains.

### 3. Virtual Host Discovery
Find virtual hosts configured on a server.
#### Example:
```bash
gobuster vhost -u http://example.com -w vhosts.txt
```
**Options:**
- `-k`: Skip SSL verification.
- `-o`: Output results to a file.

### 4. Common Options for All Modes
- `-u`: Target URL or domain.
- `-w`: Path to the wordlist.
- `-t`: Number of concurrent threads.
- `-o`: Save output to a file.
- `-v`: Enable verbose mode.

---

## How to Install Gobuster

### Install Using Package Manager
1. Update the package list:
   ```bash
   sudo apt update
   ```
2. Install Gobuster:
   ```bash
   sudo apt install gobuster -y
   ```
3. Verify the installation:
   ```bash
   gobuster -h
   ```

### Manual Installation
1. Install Go (Golang):
   ```bash
   sudo apt install golang -y
   ```
2. Clone the Gobuster repository:
   ```bash
   git clone https://github.com/OJ/gobuster.git
   cd gobuster
   ```
3. Build Gobuster:
   ```bash
   go build
   ```
4. Move the binary to a directory in your PATH:
   ```bash
   sudo mv gobuster /usr/local/bin/
   ```
5. Verify the installation:
   ```bash
   gobuster -h
   ```

---

## Conclusion
Gobuster is an essential tool in the offensive security toolkit, enabling penetration testers and security researchers to identify hidden files, directories, subdomains, and virtual hosts. Its flexibility and efficiency make it a go-to choice for brute-forcing tasks.

This lab has covered:
- The architecture and components of Gobuster.
- Its functions and practical use cases with examples.
- Installation instructions for quick setup.

By mastering Gobuster, you can enhance your ability to uncover vulnerabilities and improve the security posture of web applications and systems.
