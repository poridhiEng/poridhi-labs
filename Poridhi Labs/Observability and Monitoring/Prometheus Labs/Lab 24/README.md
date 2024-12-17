

# **Alertmanager Configuration**


Alertmanager is a tool in the Prometheus ecosystem that manages alerts. It routes, silences, and groups alerts, sending notifications to receivers like **Slack**, **email**, or **webhooks**.

## **Objective**

- Understand the **main components** of the Alertmanager configuration file.
- Learn how to:
   - Group alerts.
   - Route alerts based on conditions.
   - Silence or inhibit specific alerts.

## **Main Sections of Alertmanager Configuration**

![](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/539f9d1e752733790fd7b1b08793843642327ea7/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2024/images/x2.svg)

The configuration file has three key sections:

1. **Global Configurations**: Defines global settings applied across all routes and receivers.  
2. **Route Section**: Specifies how alerts are matched, grouped, and routed to receivers.  
3. **Receivers Section**: Contains the integrations (e.g., Slack, email, webhook) where alerts are sent.


### **Global Configurations**

The **Global Configurations** in Alertmanager define settings that apply across all routes and receivers. These configurations serve as defaults for **timeouts**, **notification settings**, and other parameters that can be reused globally.


### **Common Global Configuration Options**

1. **resolve_timeout**  
   - Controls how long Alertmanager waits before marking an alert as **resolved** once it stops firing.  
   - Alerts are considered active until they have been resolved for the specified time.  
     ```yaml
     global:
       resolve_timeout: 5m
     ```
     - If an alert stops firing, Alertmanager will mark it as "resolved" after 5 minutes.  
     - Used to avoid premature notifications when issues temporarily recover.

2. **smtp_* (SMTP Email Settings)**  
   - These settings configure the **SMTP server** for sending email notifications.  
   - If any `email_configs` use email notifications, the global SMTP settings apply by default.  

     ```yaml
     global:
       smtp_smarthost: 'smtp.example.com:587'   
       smtp_from: 'alertmanager@example.com'    
       smtp_auth_username: 'username'           
       smtp_auth_password: 'password'          
       smtp_require_tls: true                 
     ```
   - **smtp_smarthost**: Specifies the SMTP server (e.g., `smtp.example.com`) and port.  
   - **smtp_from**: Email address used as the sender for notifications.  
   - **smtp_auth_username/password**: Credentials to authenticate with the SMTP server.  
   - **smtp_require_tls**: Ensures emails are sent securely over TLS.  


3. **slack_api_url**  
   - Defines the global webhook URL for **Slack notifications**.  
   - Instead of specifying the webhook in every receiver, you can set it globally and reference it in `slack_configs`.

     ```yaml
     global:
       slack_api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
     ```

   - This saves time and reduces redundancy when configuring Slack as a receiver.

### **Route Section**

The **Route Section** is the **core** of the configuration file. It defines:  
- **How alerts are grouped**.  
- **Where alerts are routed** (to which receivers).  
- **How frequently alerts are sent**.

```yaml
route:
  group_by: ['alertname', 'job']  
  group_wait: 30s                 
  group_interval: 5m              
  repeat_interval: 1h             
  receiver: 'slack'           
```

- **group_by**:  
   Alerts with the same labels (e.g., `alertname` and `job`) are grouped into a single notification.  
   - Example: If multiple "High CPU Usage" alerts occur for different servers, they will be grouped into one message.

- **group_wait**:  
   Delay before sending the first notification. This helps batch alerts that occur close together.  
   - Example: If multiple alerts trigger within 30 seconds, they are sent as a group.

- **group_interval**:  
   Time interval between notifications for new alerts in the same group.  
   - Example: Send additional alerts every 5 minutes for the same issue.

- **repeat_interval**:  
   If an alert is not resolved, it will resend the notification after this interval.  
   - Example: Remind the user every 1 hour until the issue is fixed.

- **receiver**:  
   The **default receiver** where all alerts go if no other route matches.  

#### **Sub-Route**

The routes section allows you to define sub-routes under the main route. Sub-routes match alerts based on conditions and send them to specific receivers. This is helpful for sending different types of alerts to different teams or channels.

**How Sub-Routes Work**:  
- Sub-routes are evaluated **in order** from top to bottom.  
- Alerts are matched using **label conditions** (e.g., `severity`, `alertname`, `instance`).  
- If an alert matches a condition, it is sent to the corresponding receiver.

#### **Example: Using Sub-Routes**

```yaml
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'default'

  routes:
    - match:
        severity: 'critical'  
      receiver: 'slack-critical'

    - match:
        severity: 'warning'     
      receiver: 'slack-warning'

    - match_re:
        instance: '.*prod.*'   
      receiver: 'slack-prod-team'

receivers:
  - name: 'default'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/WEBHOOK/DEFAULT'
        channel: '#alerts-default'

  - name: 'slack-critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/WEBHOOK/CRITICAL'
        channel: '#alerts-critical'

  - name: 'slack-warning'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/WEBHOOK/WARNING'
        channel: '#alerts-warning'

  - name: 'slack-prod-team'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/WEBHOOK/PROD'
        channel: '#alerts-prod-team'
```

#### **Sub-Route Options**

1. **match**:  
   - Matches alerts where specific labels have exact values.  
   - Example:  
     ```yaml
     match:
       severity: 'critical'
     ```
     Alerts with `severity="critical"` will match this route.

2. **match_re**:  
   - Matches alerts using **regular expressions** (regex) on labels.  
   - Example:  
     ```yaml
     match_re:
       instance: '.*prod.*'
     ```
     Any alert with `prod` in the `instance` label will match this route.

3. **Fallback to Default Receiver**:  
   - If an alert doesn't match any sub-route, it will be sent to the **default receiver** specified in the parent route.

#### **Adding Inhibit Rules**

Inhibit rules suppress alerts when higher-priority alerts are active.
   ```yaml
   inhibit_rules:
     - source_match:
         severity: 'critical'
       target_match:
         severity: 'warning'
       equal: ['alertname', 'job']
   ```
- If a `critical` alert is active for the same `alertname` and `job`, `warning` alerts are suppressed.

### **Receivers Section**

The **Receivers Section** defines the destinations where alerts are sent.  Receivers can include integrations like **Slack**, **email**, or custom **webhooks**.  

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'Prometheus Alert: {{ .CommonLabels.alertname }}'
        text: >-
          *Alert:* {{ .CommonLabels.alertname }}
          *Instance:* {{ .CommonLabels.instance }}
          *Severity:* {{ .CommonLabels.severity }}
          *Description:* {{ .CommonAnnotations.description }}
```

- **name**:  
   The name of the receiver (e.g., `slack`). This name is referenced in the **route** section.

- **slack_configs**:  
   Defines the integration with **Slack**.  
   - **api_url**: Slack webhook URL used to send notifications.  
   - **channel**: Slack channel where alerts are posted (e.g., `#alerts`).  
   - **title** and **text**: Customize how alerts appear in Slack messages using templates.  


### **Template Variables**

The **`title`** and **`text`** fields use **Go templating** to dynamically insert values from alert data. Here are the commonly used options:

![alt text](https://raw.githubusercontent.com/poridhiEng/poridhi-labs/539f9d1e752733790fd7b1b08793843642327ea7/Poridhi%20Labs/Observability%20and%20Monitoring/Prometheus%20Labs/Lab%2024/images/image.png)


### **Conclusion**

In this lab, you learned the key components of Alertmanager's configuration, including **Global Configurations**, **Route Section**, **Sub-Routes**, **Inhibit Rules**, and the **Receivers Section**. By integrating with Slack and understanding how to group, route, and suppress alerts, you now have a robust foundation to manage alerts effectively in your monitoring system. 

