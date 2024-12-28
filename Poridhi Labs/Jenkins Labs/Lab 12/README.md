## CI/CD Pipeline using Jenkins and Monitoring Tools

## Monitoring the Kubernetes Cluster

1. Install helm

```sh
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

![alt text](image.png)


```
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
chmod 600 ~/.kube/config
export KUBECONFIG=~/.kube/config
```

![alt text](image-1.png)


```sh
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --set service.type=NodePort \
  --set service.nodePort=30080
```

![alt text](image-2.png)


```sh
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
```

![alt text](image-3.png)

![alt text](image-4.png)

![alt text](image-5.png)


## Data source

```
http://prometheus-server.prometheus.svc.cluster.local
```

![alt text](image-6.png)

![alt text](image-7.png)

## Dashboard

15282

![alt text](image-9.png)