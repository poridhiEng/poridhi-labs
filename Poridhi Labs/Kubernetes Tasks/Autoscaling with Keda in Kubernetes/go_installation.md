To install Go (Golang) on a Linux system, follow these steps:

---

### **Step 1: Update System Packages**
Before installing, ensure your system is up-to-date:
```bash
sudo apt update && sudo apt upgrade -y
```

---

### **Step 2: Download the Latest Go Package**
1. Visit the [Go Downloads page](https://go.dev/dl/) to check for the latest version.
2. Use `wget` to download the Go tarball. For example, to download version `1.21.0`:
   ```bash
   wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
   ```

---

### **Step 3: Extract the Go Package**
Extract the tarball into `/usr/local` (the recommended directory):
```bash
sudo tar -xvf go1.21.0.linux-amd64.tar.gz -C /usr/local
```

---

### **Step 4: Set Up Go Environment Variables**
1. Add the Go binary path (`/usr/local/go/bin`) to your system's `PATH` environment variable:
   ```bash
   echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.profile
   ```

2. Reload the profile to apply changes:
   ```bash
   source ~/.profile
   ```

---

### **Step 5: Verify the Installation**
Check the installed Go version to ensure it's working:
```bash
go version
```

You should see output similar to:
```
go version go1.21.0 linux/amd64
```

---

### **Step 6 (Optional): Test Go Installation**
Create a simple Go program to verify the installation:
1. Create a file named `hello.go`:
   ```bash
   nano hello.go
   ```
2. Add the following code:
   ```go
   package main

   import "fmt"

   func main() {
       fmt.Println("Hello, World!")
   }
   ```
3. Run the program:
   ```bash
   go run hello.go
   ```

You should see the output:
```
Hello, World!
```

---

### **Uninstalling Go (Optional)**
If you need to uninstall Go:
1. Remove the Go directory:
   ```bash
   sudo rm -rf /usr/local/go
   ```
2. Remove the `PATH` entry from `~/.profile` or other shell configuration files.

---

Let me know if you need further assistance!