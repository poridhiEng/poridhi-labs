# Nginx Log Monitoring with Sidecar Container

## Overview

This guide provides a step-by-step approach to implementing a real-time log monitoring solution for Nginx using the sidecar container pattern in Kubernetes. By following this pattern, you can view Nginx logs without accessing the main container directly, enhancing observability and modularity.

![alt text](./images/sidecar-container.svg)

## Architecture Components

### 1. Main Container (Nginx)
- **Purpose**: Serves web content and generates logs.
- **Image**: `nginx:latest`
- **Log Location**: `/var/log/nginx/`
- **Generated Logs**:
  - **access.log**: Records all HTTP requests.
  - **error.log**: Records all error events.

### 2. Sidecar Container (Log Monitor)
- **Purpose**: Streams Nginx logs in real-time for easy viewing.
- **Image**: `alpine:latest`
- **Monitored Logs**: `access.log` and `error.log`
- **Output**: Streams logs to `stdout`, accessible via `kubectl logs`.

## Implementation Steps

### Step 1: Create a Custom Nginx Configuration

Define a custom Nginx configuration file to enable structured logging in JSON format.

#### Content of `nginx-config.conf`:
```nginx
http {
    log_format json_combined escape=json
        '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"remote_user":"$remote_user",'
        '"request":"$request",'
        '"status":"$status",'
        '"body_bytes_sent":"$body_bytes_sent",'
        '"request_time":"$request_time",'
        '"http_referrer":"$http_referer",'
        '"http_user_agent":"$http_user_agent"'
        '}';

    access_log /var/log/nginx/access.log json_combined;
    error_log /var/log/nginx/error.log;
}
```

### Step 2: Create a Kubernetes ConfigMap
Store the custom Nginx configuration in a Kubernetes ConfigMap for use in the Pod.

#### ConfigMap Manifest (`configmap.yaml`):

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  labels:
    app: nginx
    environment: dev
    team: devops
    tier: backend
    version: v1.0
data:
  default.conf: |
    events {
        worker_connections 1024;
    }
    
    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;

        log_format json_combined escape=json
            '{'
            '"time_local":"$time_local",'
            '"remote_addr":"$remote_addr",'
            '"remote_user":"$remote_user",'
            '"request":"$request",'
            '"status":"$status",'
            '"body_bytes_sent":"$body_bytes_sent",'
            '"request_time":"$request_time",'
            '"http_referrer":"$http_referer",'
            '"http_user_agent":"$http_user_agent"'
            '}';

        access_log /var/log/nginx/access.log json_combined;
        error_log /var/log/nginx/error.log;

        sendfile on;
        keepalive_timeout 65;

        server {
            listen 80;
            server_name localhost;

            location / {
                root   /usr/share/nginx/html;
                index  index.html index.htm;
            }
        }
    }
```

Apply the ConfigMap to your Kubernetes cluster:
```bash
kubectl apply -f configmap.yaml
```

### Step 3: Define the Pod Manifest
Create a Pod that includes both the Nginx container and the sidecar container for log monitoring.

#### Pod Manifest (`pod.yaml`):
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-with-log-viewer
  labels:
    app: nginx
    environment: dev
    team: devops
    tier: backend
    version: v1.0
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
    volumeMounts:
    - name: nginx-config
      mountPath: /etc/nginx/nginx.conf
      subPath: default.conf
    - name: log-volume
      mountPath: /var/log/nginx

  - name: log-viewer
    image: alpine:latest
    command: ["/bin/sh", "-c"]
    args:
    - |
      while true; do
        if [ -f /var/log/nginx/access.log ] && [ -f /var/log/nginx/error.log ]; then
          tail -f /var/log/nginx/access.log /var/log/nginx/error.log
        else
          sleep 1
        fi
      done
    volumeMounts:
    - name: log-volume
      mountPath: /var/log/nginx

  volumes:
  - name: nginx-config
    configMap:
      name: nginx-config
  - name: log-volume
    emptyDir: {}
```

Apply the Pod manifest to your cluster:
```bash
kubectl apply -f pod.yaml
```

## Deployment Verification

### Verify Pod Deployment
Check the status of the Pod:
```bash
kubectl get pods nginx-with-log-viewer
```
Ensure the Pod is running, and both containers (nginx and log-viewer) are healthy.

### View Real-time Logs
Stream logs from the sidecar container:
```bash
kubectl logs nginx-with-log-viewer -c log-viewer -f
```

### Filter Logs by Type
- **Access Logs**:
  ```bash
  kubectl logs nginx-with-log-viewer -c log-viewer | grep access.log
  ```
- **Error Logs**:
  ```bash
  kubectl logs nginx-with-log-viewer -c log-viewer | grep error.log
  ```

## Testing the Setup

### Generate Test Traffic
Forward the Nginx service to your local machine:
```bash
kubectl port-forward nginx-with-log-viewer 8080:80
```
Access the service:
```bash
curl http://localhost:8080
```

### Verify Logs
Check the sidecar container logs to confirm the traffic is recorded:
```bash
kubectl logs nginx-with-log-viewer -c log-viewer
```

## Troubleshooting

### Logs Not Appearing
- **Verify Nginx Container**:
  ```bash
  kubectl describe pod nginx-with-log-viewer
  ```
- **Check Volume Mounts**:
  ```bash
  kubectl exec nginx-with-log-viewer -c nginx -- ls -l /var/log/nginx
  ```

### Incorrect Log Format
- **Inspect ConfigMap Content**:
  ```bash
  kubectl get configmap nginx-config -o yaml
  ```
- **Validate Nginx Configuration**:
  ```bash
  kubectl exec nginx-with-log-viewer -c nginx -- cat /etc/nginx/nginx.conf
  ```

## Maintenance Considerations

### Log Rotation
To prevent excessive disk usage:
- Use a separate init container to configure log rotation using `logrotate`.

### Resource Limits
- Set CPU and memory limits for both containers.
- Monitor the size of logs periodically.

### Security Enhancements
- Apply proper RBAC permissions to limit access.
- Use non-root users for containers.
- Enable network policies to restrict communication.

## Best Practices

1. **Container Configuration**:
   - Use specific image tags instead of `latest`.
   - Configure resource requests and limits.
   - Implement liveness and readiness probes.

2. **Logging**:
   - Use structured logging (e.g., JSON).
   - Include relevant metadata for better insights.
   - Rotate logs regularly to manage storage.

3. **Security**:
   - Run containers with non-root privileges.
   - Use a read-only root filesystem whenever possible.
   - Apply network policies for added security.

## Additional Notes
- The sidecar container pattern can be extended to forward logs to external systems like ELK or Fluentd.
- For production environments, consider using a centralized logging solution.
- Regularly monitor log volumes and adjust configurations as needed.

By following this guide, you can effectively monitor Nginx logs in real-time while maintaining modularity and security. For advanced use cases, integrate this solution with your existing logging infrastructure to further enhance observability.

