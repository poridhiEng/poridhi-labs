# **Bypassing HTML Encoding with Burp Suite**

In Reflected XSS, a user's input is included in the response of a web application without proper sanitization. When an application is vulnerable to Reflected XSS, an attacker can exploit the application by injecting a malicious script in the input field. In this lab, we will simulate **Reflected XSS** in a vulnerable web application and systematically **test all possible HTML tags** using **Burp Suite** to find an effective payload. By doing so, we will learn how attackers exploit such vulnerabilities and understand the importance of strong security measures.

## **Objective**  

The goal of this hands-on lab is to:  

- Understand Reflected XSS and how it works in a real-world scenario.  
- Explore how HTML encoding can be bypassed despite partial security measures.  
- Use Burp Suite to automate testing for different HTML tags to identify working exploits.  
- Analyze application responses to determine which tags and attributes are vulnerable.  
- Gain insight into the mitigation strategies that can effectively prevent these types of attacks. 

## **Prerequisites**

- Docker
- `Burp Suite` installed in your system
- Basic knowledge of `HTML`, `CSS`, and `JavaScript`

## **Reflected XSS** 

Reflected XSS is a type of XSS attack where the malicious script is reflected off the web application back to the victim's browser. This type of XSS is common in web applications that handle user input, such as name fields, comment sections, and login forms.

![](./images/2.svg)

An attacker crafts a malicious URL containing a script and tricks a user into clicking it. The vulnerable website reflects the script in its response without proper sanitization, causing the user's browser to execute it, leading to data theft or session hijacking.

## **Burp Suite**

Burp Suite is a leading tool for web application security testing. It offers a comprehensive suite of tools for:

- Intercepting and analyzing HTTP/HTTPS traffic.
- Detecting and exploiting web application vulnerabilities.
- Automating security testing workflows.

## **Why use Burp Suite to Bypass HTML Encoding?**

We have so many tags in HTML like `<script>`, `<img>`, `<svg>`, `<a>`, etc. and each of them has so many attributes. When an developer builds a web application, he/she may not encode all the possible HTML tags and attributes. Attackers use Burp Suite to brute-force the HTML tags and find a working exploit.


For example, a developer forget the encode the `svg` tag, so an attacker can use the `svg` tag to execute the JavaScript code.

```html
<svg onload="alert('XSS')"></svg>
```

But in `HTML` we have more than 100 tags, for attackers it is very difficult to test all the tags and attributes. So, attackers use Burp Suite to brute-force the HTML tags and find a working exploit.

## **How Burp Suite Bypass HTML Encoding**  

Burp Suite is an advanced web security tool that can help identify vulnerabilities in web applications, including **bypassing HTML encoding protections**. One of its core features, **Intruder**, plays a crucial role in testing how a web server processes encoded HTML inputs and whether they can be exploited. 

![](./images/logo1.svg)

### **Capturing and Modifying Requests**  
Burp Suite’s **Proxy** intercepts the request sent from the browser to the server, allowing an attacker to examine the structure of the request. If the request contains a user input field (such as a form or search bar), Burp Suite extracts and isolates the specific parameter where HTML encoding protections might be applied.  

### **Injecting Payloads via Intruder**  
Burp Suite’s **Intruder** automates the process of sending multiple variations of a payload to determine how the server handles different encoding schemes. It does this by:  

1. **Identifying Input Fields:** Intruder pinpoints parameters where user input is processed and attempts to manipulate them.  
2. **Replacing User Input with Payloads:** It substitutes normal user input with various HTML-encoded payloads such as:  
   - `<script>alert('XSS')</script>` (raw HTML)  
   - `&lt;script&gt;alert('XSS')&lt;/script&gt;` (HTML encoded)  
   - `&#x3C;script&#x3E;alert('XSS')&#x3C;/script&#x3E;` (Hex encoding)  
   - `%3Cscript%3Ealert('XSS')%3C/script%3E` (URL encoding)  

Intruder **systematically injects** these payloads into the selected parameter and sends them to the server to analyze the response.  

### **Analyzing Server Responses**  

![](./images/logo2.svg)

Burp Suite **monitors the behavior** of the server when different encoded versions of the payload are received. It does this by:  

- **Comparing HTTP Response Codes:** If different encoding formats return different HTTP status codes (e.g., `200 OK` for successful execution, `403 Forbidden` for blocked input), it indicates how the server processes the input.  
- **Checking Content Reflection:** If the server returns the payload **without encoding it again**, it suggests a potential vulnerability where the input is rendered as raw HTML, leading to execution in the browser.  
- **Detecting Filtering Mechanisms:** If some payloads are blocked while others pass through, Intruder helps identify which encoding methods successfully bypass input sanitization.  

### **Finding Bypasses through Encoding Variations**  
Burp Suite **automates** the process of testing different encoding techniques. If one encoding method is blocked, it tries alternative formats until it finds a **working bypass**. This includes:  

1. **Double Encoding**: `%253Cscript%253Ealert('XSS')%253C/script%253E`  
2. **Mixed Encoding**: Using combinations of **hex, URL, and HTML encoding** to trick the filtering mechanism.  
3. **Character Injection**: Injecting broken sequences or null bytes (`%00`) to disrupt encoding routines.  

If a certain encoded version gets **executed instead of displayed as text**, Burp Suite flags it as a potential exploit.  

### **Extracting the Exploit**  
Once Burp Suite identifies a bypass, it refines the payload to **maximize impact** while avoiding detection. If an encoded version executes JavaScript or injects unwanted HTML elements, it confirms that the encoding protections are weak. The final exploit is then extracted and used for further testing or reporting the vulnerability.



## **Hands-On Lab**  

Now we will simulate a real-world attack scenario and demonstrate how applications with partial encoding can still be exploited.

### **Step 1: Pull the docker image**  

```bash
docker pull fazlulkarim105925/reflectedxss-with-most-tags-blocked
```

### **Step 2: Run the docker container**  

```bash
docker run -d -p 8000:8000 fazlulkarim105925/reflectedxss-with-most-tags-blocked
```

### **Step 3: Create Load Balancer in Poridhi's Cloud**

Find the `eth0` IP by using the following command:

```bash
ifconfig
```

![](./images/9.png)

Now create a load balancer in Poridhi's Cloud with the `eth0` IP and the port `8000`.

![](./images/10.png)

Now you can access the application by using the load balancer URL from any browser.

![](./images/1.png)

### **Step 4: Exploit the application**

In the `name` field, try to inter you name (e.g., `Poridhi`) and see how it reflected in the response.

![](./images/2.png)

If we open the `DevTools` of the browser, we can see that the application rendered the `name` field a Greeter message. It takes the `name` parameter and renders it as a Greeter message.

![](./images/25.png)

It also take the `name` parameter and render it in the `URL` as a parameter.

![](./images/3.png)

Now try to inter the `name` parameter as a `script` tag. for example:

```html
url/?name=<script>alert(1)</script>
```

![](./images/4.png)

We can see that the application is blocked the `script` tag.

Now try with simple `<div>` tag.

```html
url/?name=<div>test</div>
```

![](./images/5.png)

We can see that the application blocked the `<div>` tag also.

It suggested that the application blocked most of the HTML tags. But we need to find a `tag` which is not blocked by the application. We need to brute-force the HTML tags and find a working exploit. So we will use Burp Suite to brute-force the HTML tags and find a working exploit.

### **Step 5: Configure Burp Suite**

If Burp Suite is not installed in your system, you can download it from [here](https://portswigger.net/burp/communitydownload).

![](./images/6.png)

Download and installed Burp Suite.

Open `Burp Suite` and open a temporary project.

Navigate to `Proxy` tab in `Burp Suite`.

![](./images/7.png)

Make sure that the `Intercept is on` option is enabled. And launch the `Browser`.

![](./images/8.png)

A `Chromium` browser will be opened. Paste the `Load Balancer` URL in the address bar and edit the `name` parameter.

```bash
<loadbalancer-url>/?name=<a>
```

![](./images/12.png)

As `Burp Suite` `Intercept` is enabled, it will intercept the request and we can see the request in `Burp Suite` `Proxy` tab.

![](./images/13.png)

Now we need to intercept the request and send it to `Intruder`. To do this, we need to right click on the request and select `Send to Intruder`.

![](./images/14.png)

Now we need to configure the `Intruder` tab in `Burp Suite`. Navigate to `Intruder` tab. We will see the `Target` `url` and intercepted request.

![](./images/15.png)

In the first line, we have the `Target` `url` and intercepted request.

```bash
GET /?name=%3Ca%3E HTTP/2
```
`%3C` and `%3E` are the encoded `<` and `>` characters. Between these characters, we have the `name` parameter (e.g., `<a>`).

Now select the `name` parameter (e.g., `a` only) and right click and select `Add payload position`.

![](./images/17.png)

`$` symbol is used to inject the payload. After adding the payload position, we will see the following.
```bash
GET /?name=%3C$a$%3E HTTP/2
```

![](./images/18.png)

Now we need the list of all the HTML tags. Postswigger has a cheat sheet for the HTML tags. We can use it to get the list of all the HTML tags. To get the cheat sheet, follow the `url` below. Copy all the `HTML` tags from the website.

```bash
https://portswigger.net/web-security/cross-site-scripting/cheat-sheet
```

![](./images/11.png)

Now paste the list of `HTML` tags in the `Intruder` `Payloads` tab.

![](./images/20.png)

Now we need to configure the `Intruder` tab in `Burp Suite`. Navigate to `Intruder` tab. We will see the `Target` `url` and intercepted request.

Now we are all set to start the attack. Click on the `Start attack` button on the top right corner. A new `window` will be opened. Here we can see the `payload` that was injected in the `name` parameter and corresponding `response`  and other details.

To find the only `working` payload, we need to find the payload which is not blocked by the application. We can do this by checking the `status code` of the response. If the status code is `200`, then the payload is working. To sort the payloads by the `status code`, we need to click on the `status code` column. 

![](./images/21.png)

We have successfully found the `working` `HTML` tag. Now we can use this tag to exploit the application.

## **Step 6: Exploit the application**

Now we need to exploit the application. We will use the `working` `HTML` tag to exploit the application.

From `Burp Suite` `Intruder` tab, we have found the following `working` `HTML` tag.

```bash
<details>
<input>
<marquee>
```

We need to generate some payloads with this tags to exploit the application.

If you use the following payload in the `name` parameter, you will see that the tag is working, `Latest Community Posts` section is moving right to left.

```bash
name=<marquee>
```

![](./images/22.png)

We can also try out this payload in the `name` parameter. It will open an `alert` box with a message `1`.

```bash
name=<details ontoggle=alert(1) open>
```

Congratulations! You have successfully exploited the application. Find the `vulnerable` `endpoint` of the application and exploit it with the `working` `HTML` tag.


## **How to prevent XSS Attacks?**

To prevent XSS attacks, web developers should:    
- Try to encode all the `HTML` tags and attributes. use tools like `Burp Suite` to find the `vulnerable` `endpoints` and `HTML` tags and improve the security of the application.
- Implement **proper encoding** for **all** user input.
- Use **secure JavaScript APIs** like `textContent` instead of `innerHTML`.  
- Enforce **strict Content Security Policies (CSPs)** to restrict script execution.

## **Conclusion**  

In this lab, we have learned how to exploit the application using `Burp Suite`. We have also learned how to prevent XSS attacks. We have used the `Burp Suite` to find the `vulnerable` `endpoints` and `HTML` tags and improve the security of the application.






