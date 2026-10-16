# ArgoCD GitOps Continuous Deployment

This directory contains the declarative GitOps Application manifest for continuous delivery of the Campus Resource Hub into Kubernetes via ArgoCD.

## GitOps Architecture & Delivery Loop

```
Developer Push ──▶ GitHub Actions CI (Test + Scan + Publish Image)
                         │
                         ▼ (Auto-updates values.yaml image tag)
               GitHub Repository (Single Source of Truth)
                         │
                         ▼ (Polls or Webhook triggers)
               ArgoCD Controller (In-Cluster)
                         │
                         ▼ (helm upgrade --install reconciliation)
               Amazon EKS Cluster (Zero-Downtime Rollout)
```

## Step-by-Step ArgoCD Setup on Kubernetes

### 1. Install ArgoCD
```bash
# Create dedicated namespace
kubectl create namespace argocd

# Apply official ArgoCD installation manifests
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD server and controllers to be ready
kubectl wait --for=condition=available deployment/argocd-server -n argocd --timeout=300s
```

### 2. Retrieve Initial Admin Password
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
echo ""
```

### 3. Access ArgoCD Web UI
Forward the ArgoCD UI port locally:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Open your browser to: `https://localhost:8080` (Username: `admin`, Password from Step 2).

### 4. Deploy Campus Resource Hub Application
Apply the GitOps manifest:
```bash
kubectl apply -f argocd/application.yaml
```

### 5. Verify Synchronization & Health Status
```bash
# Check application status
kubectl get application campus-resource-hub -n argocd

# Check live workload resources created in target namespace
kubectl get pods,svc,ingress,hpa -n campus-resource-hub
```

## Troubleshooting ArgoCD Out-of-Sync
- **Repo Access**: If the repository is private, register credentials via `argocd repo add`.
- **Manual Sync**: Run `argocd app sync campus-resource-hub` or click **SYNC** in the UI.
- **Diff Inspection**: Run `argocd app diff campus-resource-hub` to view differences between Git and Cluster.
