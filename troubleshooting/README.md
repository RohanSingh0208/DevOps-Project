# DevSecOps Kubernetes Troubleshooting Lab

This lab provides hands-on diagnostic scenarios with deliberately broken Kubernetes manifests for classroom demonstration and grading defense.

> [!NOTE]
> Run these scenarios in the `default` or a sandbox namespace. Never apply them to the production `campus-resource-hub` namespace.

---

## Scenario 1: Image Pull Failure (`ImagePullBackOff`)

### 1. Apply Broken Manifest
```bash
kubectl apply -f troubleshooting/broken-image.yaml
```

### 2. Diagnose Symptoms
Check the pod status:
```bash
kubectl get pods -l lab.devsecops.io/scenario=broken-image
```
*Expected Output:*
```
NAME                                READY   STATUS             RESTARTS   AGE
lab-broken-image-7b98d9c57f-kpx8n   0/1     ImagePullBackOff   0          45s
```

### 3. Root Cause Investigation
Inspect pod lifecycle events and error details:
```bash
kubectl describe pod -l lab.devsecops.io/scenario=broken-image
kubectl get events --sort-by=.lastTimestamp
```
*Key Diagnostic Line:*
```
Failed to pull image "ghcr.io/rohansingh0208/campus-resource-hub-backend:non-existent-tag-99999": rpc error: code = NotFound
```

### 4. Resolution
Edit `troubleshooting/broken-image.yaml` to point to a valid tag (e.g., `latest` or valid SHA), then re-apply:
```bash
kubectl set image deployment/lab-broken-image web=ghcr.io/rohansingh0208/campus-resource-hub-backend:latest
kubectl rollout status deployment/lab-broken-image
```

### 5. Cleanup
```bash
kubectl delete -f troubleshooting/broken-image.yaml
```

---

## Scenario 2: Service Selector Mismatch (`Empty Endpoints`)

### 1. Apply Broken Manifest
```bash
kubectl apply -f troubleshooting/broken-service.yaml
```

### 2. Diagnose Symptoms
Check service status and endpoints:
```bash
kubectl get svc lab-broken-service
kubectl get endpoints lab-broken-service
```
*Expected Output:*
```
NAME                 ENDPOINTS
lab-broken-service   <none>
```
Notice that the endpoints column shows `<none>` even though 2 application pods are running!

### 3. Root Cause Investigation
Compare Service selector labels with Pod actual labels:
```bash
# View labels on running target pods
kubectl get pods --show-labels -l lab.devsecops.io/scenario=broken-service

# View selector configured on the service
kubectl get svc lab-broken-service -o jsonpath='{.spec.selector}'
```
*Diagnostic Finding:*
- Pod Label: `app=correct-target-app`
- Service Selector: `app=wrong-selector-target`
Because the labels don't match, Kubernetes Endpoints controller cannot associate the pods with the service.

### 4. Resolution
Patch the service selector to match the pod labels:
```bash
kubectl patch svc lab-broken-service -p '{"spec":{"selector":{"app":"correct-target-app"}}}'

# Verify endpoints are now populated
kubectl get endpoints lab-broken-service
```
*Output after fix:*
```
NAME                 ENDPOINTS
lab-broken-service   10.244.1.14:80,10.244.2.18:80
```

### 5. Cleanup
```bash
kubectl delete -f troubleshooting/broken-service.yaml
```
