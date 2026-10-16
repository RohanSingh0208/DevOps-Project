# Monitoring & Observability Stack

This directory contains configuration files, custom Helm values, and dashboard specifications for monitoring the Campus Resource Hub using Prometheus and Grafana.

## Overview

- **Application Metrics Endpoint**: `GET /metrics` exposed by FastAPI via `prometheus-fastapi-instrumentator`.
- **Metrics Scraper**: Prometheus Operator via custom `ServiceMonitor` resource.
- **Visualizer**: Grafana with custom dashboard JSON (`dashboard.json`).

## Step-by-Step Installation on Kubernetes

### 1. Add Prometheus Community Helm Repository
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### 2. Deploy kube-prometheus-stack
```bash
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yaml
```

### 3. Verify Prometheus Discovery
Forward the Prometheus web console:
```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
```
Open `http://localhost:9090/targets` in your browser. Verify that `campus-resource-hub-backend` appears in the list with state **UP**.

### 4. Access Grafana and Import Dashboard
Forward the Grafana web console:
```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```
- **URL**: `http://localhost:3000`
- **Username**: `admin`
- **Password**: `admin_campus_metrics_2026`

**Importing the Dashboard:**
1. Navigate to **Dashboards** > **New** > **Import**.
2. Click **Upload JSON file** and select `monitoring/dashboard.json`.
3. Select the default `Prometheus` datasource and click **Import**.

## Core PromQL Queries

| Metric / Panel | PromQL Expression | Purpose |
| :--- | :--- | :--- |
| **Request Rate** | `sum(rate(http_requests_total[1m])) by (handler, method)` | Tracks throughput per API route |
| **p95 Latency** | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[2m])) by (le))` | 95th percentile API response time |
| **Error Rate** | `sum(rate(http_requests_total{status=~"[45].."}[1m])) by (status)` | Monitors 4xx client and 5xx server errors |
| **CPU Usage** | `sum(rate(container_cpu_usage_seconds_total{namespace="campus-resource-hub", pod=~"campus-resource-hub-backend.*"}[1m])) by (pod)` | Pod-level compute load |
| **Memory (RSS)**| `sum(container_memory_working_set_bytes{namespace="campus-resource-hub", pod=~"campus-resource-hub-backend.*"}) by (pod)` | Pod-level memory footprint |
| **Ready Pods** | `sum(kube_deployment_status_replicas_ready{namespace="campus-resource-hub", deployment=~"campus-resource-hub-backend.*"})` | High availability & replica health |

## Troubleshooting Scenarios

### Target is DOWN in Prometheus Targets
1. **Verify Backend Pod Logs**:
   ```bash
   kubectl logs -n campus-resource-hub -l app.kubernetes.io/component=backend
   ```
2. **Verify `/metrics` responds inside cluster**:
   ```bash
   kubectl exec -it -n campus-resource-hub deployment/campus-resource-hub-backend -- curl -s http://localhost:8000/metrics | head -n 15
   ```
3. **Verify Service & ServiceMonitor Selector Match**:
   Ensure `Service.metadata.labels` match `ServiceMonitor.spec.selector.matchLabels`.
