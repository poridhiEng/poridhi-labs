# Gobuster: A Tool for Offensive Security

Gobuster is a powerful and flexible tool used in the field of offensive security for discovering hidden files, directories, DNS subdomains, and virtual hosts on a target system. This document provides a detailed overview of Gobuster, including its architecture, core functions, installation steps, and usage examples.

![](./images/banner2.svg)


## Objective

The primary goal of this lab is to introduce Gobuster, its architecture, and its functionality through a structured and practical approach. By the end of this lab, you will:

- Understand what Gobuster is and how it works.
- Learn about the different functions and options provided by Gobuster.
- Gain hands-on experience using Gobuster in a controlled environment.

## Architecture of Gobuster

Gobuster is designed to perform brute-forcing tasks efficiently by leveraging the following components:

![](./images/banner3.svg)

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
   - Threads are the number of requests that Gobuster will send to the target at a time.

5. **Output Reporting**:

   - Provides both real-time and file-based output.
   - Supports verbose and filtered result formats.

## Functions of Gobuster

Gobuster offers multiple modes of operation tailored to different offensive security tasks:

### 1. Directory and File Brute-Forcing

Discover hidden directories and files on a web server.

**Options:**

- `-x`: Specify file extensions (e.g., `.php`, `.html`).
- `-t`: Number of threads (default: 10).
- `-o`: Output results to a file.
- `-s`: Filter results by HTTP status codes.

#### Example:

```bash
gobuster dir -u http://example.com -w wordlist.txt
```
```bash
gobuster dir -u http://example.com -w wordlist.txt -x php,html,txt
```
```bash
gobuster dir -u http://example.com -w wordlist.txt -s 200,301,302,307
```


### 2. DNS Subdomain Enumeration

Identify all the subdomains for a given domain. 

**Options:**
- `-d`: Specify the domain to enumerate.
- `-w`: Specify the wordlist to use.
- `-r`: Specify a DNS server.
- `-z`: Skip wildcards. (`Wildcards` are the `*` in the wordlist. By skipping wildcards, Gobuster will not try to find the subdomains with `*`.)
- `-i`: Show IPs of discovered subdomains.

#### Example:

```bash
gobuster dns -d example.com -w subdomains.txt
```
```bash
gobuster dns -d example.com -w subdomains.txt -r 8.8.8.8
```
```bash
gobuster dns -d example.com -w subdomains.txt -z
```
```bash
gobuster dns -d example.com -w subdomains.txt -i
```

### 3. Virtual Host Discovery

Find virtual hosts configured on a server. Virtual hosts are the subdomains that are configured on a server.

**Options:**

- `-u`: Specify the URL to enumerate.
- `-w`: Specify the wordlist to use.
- `-k`: Skip SSL verification.
- `-o`: Output results to a file.

#### Example:

```bash
gobuster vhost -u http://example.com -w vhosts.txt
```
```bash
gobuster vhost -u http://example.com -w vhosts.txt -k
```
```bash
gobuster vhost -u http://example.com -w vhosts.txt -o vhosts.txt
```

### 4. S3 Bucket Enumeration

Enumerate AWS S3 buckets. Buckets are the containers that are used to store the data in AWS. By enumerating the buckets, you can find the hidden data in the buckets.

**Options:**

- `-w`: Specify the wordlist to use.
- `-v`: Enable verbose mode.
- `-t`: Number of threads. ( Threads are the number of requests that Gobuster will send to the target at a time. )

#### Example:

```bash
gobuster s3 -w bucket-names.txt
```
```bash
gobuster s3 -w bucket-names.txt -v
```
```bash
gobuster s3 -w bucket-names.txt -t 10
```


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

## Conclusion

Gobuster is an essential tool in the offensive security toolkit, enabling penetration testers and security researchers to identify hidden files, directories, subdomains, and virtual hosts. Its flexibility and efficiency make it a go-to choice for brute-forcing tasks.

This lab has covered:

- The architecture and components of Gobuster.
- Its functions and practical use cases with examples.
- Installation instructions for quick setup.
- Test cases to validate its usage.

By mastering Gobuster, you can enhance your ability to uncover vulnerabilities and improve the security posture of web applications and systems.

