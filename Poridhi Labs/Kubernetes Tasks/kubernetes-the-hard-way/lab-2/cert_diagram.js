// graph TD
//     %% Certificate Authority Node
//     subgraph CA["Certificate Authority"]
//         ca["ca.pem"]
//     end

//     %% Control Plane Components
//     subgraph Control_Plane["Control Plane"]
//         APIServer["Kubernetes API Server (kubernetes.pem)"]
//         Scheduler["Kube Scheduler (kube-scheduler.pem)"]
//         ControllerManager["Kube Controller Manager (kube-controller-manager.pem)"]
//         ServiceAccount["Service Account (service-account.pem)"]
//     end

//     %% Worker Nodes Components
//     subgraph Worker_Nodes["Worker Nodes"]
//         Kubelet0["Kubelet - Worker 0 (worker-0.pem)"]
//         Kubelet1["Kubelet - Worker 1 (worker-1.pem)"]
//         KubeProxy0["Kube Proxy - Worker 0 (kube-proxy.pem)"]
//         KubeProxy1["Kube Proxy - Worker 1 (kube-proxy.pem)"]
//     end

//     %% Users Node
//     subgraph Users
//         Admin["Admin Client (admin.pem)"]
//     end

//     %% etcd Cluster Nodes (Two Nodes)
//     %% subgraph etcd_Cluster["etcd Cluster"]
//     %%     etcd1["etcd Server 1 (etcd-1.pem)"]
//     %%     etcd2["etcd Server 2 (etcd-2.pem)"]
//     %% end

//     %% Certificate Distribution and Signing Relationships
//     ca -->|Signs| APIServer
//     ca -->|Signs| Scheduler
//     ca -->|Signs| ControllerManager
//     ca -->|Signs| ServiceAccount
//     ca -->|Signs| Kubelet0
//     ca -->|Signs| Kubelet1
//     ca -->|Signs| KubeProxy0
//     ca -->|Signs| KubeProxy1
//     ca -->|Signs| Admin
//     ca -->|Signs| etcd1
//     ca -->|Signs| etcd2

//     %% Secure Communication Paths
//     Admin --|Admin Client Cert|--> APIServer
//     APIServer --|Kubernetes API Server Cert|--> ControllerManager
//     APIServer --|Kubernetes API Server Cert|--> Scheduler
//     APIServer --|Kubernetes API Server Cert|--> Kubelet0
//     APIServer --|Kubernetes API Server Cert|--> Kubelet1
//     APIServer --|Kubernetes API Server Cert|--> KubeProxy0
//     APIServer --|Kubernetes API Server Cert|--> KubeProxy1
//     %% ControllerManager --|Controller Manager Cert|--> etcd1
//     %% ControllerManager --|Controller Manager Cert|--> etcd2
//     %% Scheduler --|Scheduler Cert|--> etcd1
//     %% Scheduler --|Scheduler Cert|--> etcd2
//     %% Kubelet0 --|Kubelet Cert|--> etcd1
//     %% Kubelet0 --|Kubelet Cert|--> etcd2
//     %% Kubelet1 --|Kubelet Cert|--> etcd1
//     %% Kubelet1 --|Kubelet Cert|--> etcd2
//     %% APIServer --|Kubernetes API Server Cert|--> etcd1
//     %% APIServer --|Kubernetes API Server Cert|--> etcd2
