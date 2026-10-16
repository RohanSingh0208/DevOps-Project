# Campus Resource Hub — Production DevSecOps Capstone Project

[![CI/CD Pipeline](https://github.com/RohanSingh0208/DevOps-Project/actions/workflows/ci-cd.yaml/badge.svg)](https://github.com/RohanSingh0208/DevOps-Project/actions)
[![Pytest Status](https://img.shields.io/badge/pytest-29%20passed-brightgreen.svg)](file:///backend/tests/)
[![Coverage](https://img.shields.io/badge/coverage-80%25-brightgreen.svg)](file:///backend/coverage.xml)
[![Security Gate](https://img.shields.io/badge/Trivy-CRITICAL%20%2F%20HIGH%20Passed-blue.svg)](file:///.github/workflows/ci-cd.yaml)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-EKS%201.30-blue.svg)](file:///helm/campus-resource-hub/)
[![GitOps](https://img.shields.io/badge/GitOps-ArgoCD-orange.svg)](file:///argocd/)

A comprehensive, production-grade DevSecOps capstone implementing an original full-stack facility booking and maintenance management application (**Campus Resource Hub**) and demonstrating the complete cloud-native software delivery lifecycle.

---

## 1. Project Description and Purpose

Colleges and universities frequently struggle with fragmented, manual reservations for campus facilities (auditoriums, computer labs, research equipment, and meeting rooms) alongside uncoordinated maintenance workflows. 

**Campus Resource Hub** provides:
1. **Facility Discovery & Booking**: Real-time capacity inspection, equipment inventory, and conflict-free reservation scheduling.
2. **Maintenance Ticket Triage**: Rapid issue submission with priority classification (`low`, `medium`, `high`, `critical`) and resolution tracking.
3. **Observability & Analytics**: Interactive KPIs displaying utilization rates, pending requests, and system health.
4. **End-to-End DevSecOps Delivery**: Automated testing, multi-stage Docker builds, Trivy container security scans, AWS EKS provisioning via Terraform, Helm packaging with Horizontal Pod Autoscaling (HPA), GitOps reconciliation with ArgoCD, and Prometheus/Grafana monitoring.

---

## 2. Application Features

- **Dynamic Analytics Dashboard**: Live metrics for facility count, active reservations, open tickets, and resource distribution charts.
- **Conflict Prevention Engine**: Rejects overlapping bookings for the same room or device with deterministic HTTP 409 responses.
- **Maintenance Lifecycle**: Track issues from `open` to `in_progress`, `resolved`, and `closed` with resolution logs.
- **Standard Health Probes**: Distinct `/health` (liveness) and `/ready` (database connectivity probe) endpoints.
- **Native Metrics Instrumentation**: Exposes RED (Rate, Errors, Duration) metrics at `/metrics` for Prometheus scraping.
- **Responsive Dark-Themed UI**: Built using React 18, Vite, Lucide Icons, and Recharts with mobile, tablet, and desktop viewports.

---

## 3. Architecture Diagram

```mermaid
graph TD
    subgraph Client & Ingress
        User([Client Browser]) -->|HTTP /| Ingress[Ingress-Nginx Controller]
    end

    subgraph Kubernetes Cluster: campus-resource-hub
        Ingress -->|/| FeSvc[Frontend Service :80]
        Ingress -->|/api| BeSvc[Backend Service :8000]
        Ingress -->|/metrics| BeSvc

        FeSvc --> FePods[Frontend Pods: 2 Replicas\nNode + Nginx Unprivileged :8080]
        BeSvc --> BePods[Backend Pods: 2 Replicas\nFastAPI Uvicorn :8000]

        BePods --> PgSvc[PostgreSQL Service :5432]
        PgSvc --> PgPod[PostgreSQL 16 Pod]
        PgPod --- PVC[(PersistentVolumeClaim 5Gi)]

        HPA[Horizontal Pod Autoscaler] -->|CPU Target 70%| BePods
    end

    subgraph Observability
        SM[ServiceMonitor] -->|Scrape /metrics 15s| BePods
        Prom[Prometheus Operator] --> SM
        Graf[Grafana Dashboard] -->|Query| Prom
    end

    subgraph GitOps Continuous Delivery
        Dev[Developer Push] --> GitHub[GitHub Repository]
        GitHub --> GHA[GitHub Actions CI/CD]
        GHA -->|Pytest + Ruff| Gate[Quality Gate]
        Gate -->|Trivy Scan| Security[Trivy Gate]
        Security -->|Push SHA Tag| GHCR[(GitHub Container Registry)]
        GHA -->|Update Tag| GitHub
        Argo[ArgoCD Controller] -->|Sync Manifests| GitHub
        Argo -->|Reconcile State| FePods
        Argo -->|Reconcile State| BePods
    end
```

---

## 4. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 18, Vite 5, TypeScript, Lucide Icons, Recharts, Nginx 1.27 Unprivileged |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0 (Async/Sync), Alembic 1.14, Pydantic v2 |
| **Testing** | Pytest 8.3, Pytest-Asyncio, HTTPX, aiosqlite, Coverage, Ruff |
| **Database** | PostgreSQL 16 Alpine, PersistentVolumeClaim (5Gi) |
| **Containers** | Docker multi-stage builds, non-root users (1001 backend, 101 frontend), Docker Compose |
| **CI/CD & Security** | GitHub Actions, Aqua Security Trivy, GitHub Container Registry (GHCR) |
| **Infrastructure** | Terraform 1.5+, AWS VPC, Internet Gateway, NAT Gateway, Amazon EKS 1.30 (`ap-south-1`) |
| **Orchestration** | Kubernetes, Helm 3, Ingress-Nginx, Horizontal Pod Autoscaler (HPA) |
| **GitOps** | ArgoCD with automated self-healing and Git reconciliation |
| **Monitoring** | Prometheus Operator (`kube-prometheus-stack`), ServiceMonitor, Grafana |

---

## 5. Repository Structure

```text
campus-resource-hub/
├── .github/
│   └── workflows/
│       └── ci-cd.yaml              # 3-Stage GitHub Actions CI/CD Pipeline
├── backend/
│   ├── app/
│   │   ├── models/                 # SQLAlchemy ORM Models (Resource, Reservation, Maintenance)
│   │   ├── routes/                 # FastAPI REST Endpoints
│   │   ├── schemas/                # Pydantic v2 Request/Response Schemas
│   │   ├── services/               # Business logic & conflict validation
│   │   ├── config.py               # Pydantic BaseSettings environment config
│   │   ├── database.py             # Async & sync engine session managers
│   │   └── main.py                 # FastAPI application root & middleware
│   ├── tests/                      # 29 Pytest test cases (100% passing)
│   ├── alembic/                    # Database migrations
│   ├── Dockerfile                  # Secure Python 3.12-slim non-root image
│   └── requirements.txt            # Pinned backend dependencies
├── frontend/
│   ├── src/
│   │   ├── api/                    # Centralized fetch API client
│   │   ├── pages/                  # Dashboard, Resources, Reservations, Maintenance
│   │   ├── types/                  # TypeScript interface definitions
│   │   ├── App.tsx                 # App layout & sidebar navigation
│   │   └── index.css               # Dark-mode design system & animations
│   ├── Dockerfile                  # Multi-stage Node builder + unprivileged Nginx
│   ├── nginx.conf                  # Nginx reverse proxy & SPA routing fallback
│   └── package.json                # Frontend dependencies & Vite configuration
├── terraform/
│   ├── networking.tf               # Dedicated VPC, 4 subnets, IGW, NAT Gateway
│   ├── eks.tf                      # EKS 1.30 Cluster, IAM roles, Managed Node Group
│   ├── variables.tf                # Input variables with cost-conscious defaults
│   ├── outputs.tf                  # VPC and cluster outputs
│   └── terraform.tfvars.example    # Safe configuration placeholder example
├── helm/
│   └── campus-resource-hub/
│       ├── Chart.yaml              # Helm Chart metadata
│       ├── values.yaml             # Production values (2 replicas, HPA, Ingress)
│       ├── values-dev.yaml         # Development values (1 replica, lightweight)
│       └── templates/              # Kubernetes workload templates
├── argocd/
│   ├── application.yaml            # ArgoCD Application GitOps manifest
│   └── README.md                   # GitOps setup and verification guide
├── monitoring/
│   ├── prometheus-values.yaml      # ServiceMonitor discovery config
│   ├── grafana-values.yaml         # Grafana datasource definitions
│   ├── dashboard.json              # 6-panel Grafana Dashboard specification
│   └── README.md                   # Observability documentation & PromQL queries
├── troubleshooting/
│   ├── broken-image.yaml           # ImagePullBackOff diagnostic scenario
│   ├── broken-service.yaml         # Mismatched selector empty endpoints scenario
│   └── README.md                   # Diagnostic commands & remediation guide
├── scripts/
│   ├── seed_data.py                # Realistic database seeder
│   └── load_test.py                # Concurrent HPA load generator
├── demo/
│   ├── presentation.pptx           # 8-Slide DevSecOps PowerPoint deck
│   └── recording-guide.md          # Timed narration script & commands
├── docker-compose.yml              # Local complete-stack deployment
├── .env.example                    # Template environment variables
├── .gitignore                      # Secure exclusion rules
└── README.md                       # Master project documentation
```

---

## 6. Prerequisites

Ensure you have the following installed locally:
- **Python**: `>= 3.12`
- **Node.js**: `>= 20.x` & `npm`
- **Docker & Docker Compose**: Docker Desktop or Docker Engine 24+
- **Git**: Git 2.30+
- *(Optional for cloud deployment)*: AWS CLI v2, Terraform `>= 1.5.0`, `kubectl`, `helm`

---

## 7. Environment Variable Setup

Copy the example configuration file:
```bash
cp .env.example .env
```
Key variables configured in `.env`:
```ini
POSTGRES_USER=campus_admin
POSTGRES_PASSWORD=campus_secure_password_2026
POSTGRES_DB=campus_resource_hub
DATABASE_URL=postgresql+asyncpg://campus_admin:campus_secure_password_2026@localhost:5432/campus_resource_hub
DATABASE_URL_SYNC=postgresql+psycopg2://campus_admin:campus_secure_password_2026@localhost:5432/campus_resource_hub
ENVIRONMENT=development
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 8. Local Docker Compose Instructions

Start the full application stack with a single command:
```bash
docker compose up --build -d
```

Verify service health:
```bash
docker compose ps
```

Access the running applications:
- **Frontend SPA**: [http://localhost:3000](http://localhost:3000)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Endpoint**: [http://localhost:8000/health](http://localhost:8000/health)
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

> [!NOTE]
> Database migrations execute automatically during startup via the dedicated `migration` service container before the backend begins serving traffic.

To stop and remove containers:
```bash
docker compose down
```
> [!WARNING]
> Running `docker compose down -v` permanently removes the named PostgreSQL database volume (`campus-resource-hub-postgres-data`) and all stored records.

---

## 9. Database Migration Instructions

Alembic tracks database revisions under `backend/alembic/versions/`.

Run migrations against an active database:
```bash
cd backend
alembic upgrade head
```

Create a new migration after updating SQLAlchemy models:
```bash
alembic revision --autogenerate -m "describe_changes"
```

Roll back one revision:
```bash
alembic downgrade -1
```

---

## 10. API Endpoints and Example Requests

### Core Health & Monitoring
- `GET /health` — Lightweight liveness probe (`{"status": "healthy"}`)
- `GET /ready` — Database readiness probe (`{"status": "ready", "database": "connected"}`)
- `GET /metrics` — Prometheus metrics scrape endpoint

### Facility Resources
- `GET /api/resources` — List all resources (optional filters: `resource_type`, `status`, `search`)
- `POST /api/resources` — Create a new resource
  ```bash
  curl -X POST http://localhost:8000/api/resources \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Robotics Studio",
      "resource_type": "laboratory",
      "location": "Engineering Hall 102",
      "capacity": 25,
      "status": "available"
    }'
  ```
- `GET /api/resources/{id}` — Retrieve resource by ID
- `PUT /api/resources/{id}` — Update resource details
- `DELETE /api/resources/{id}` — Delete resource

### Reservations
- `GET /api/reservations` — List reservations
- `POST /api/reservations` — Create reservation (validates non-overlapping window)
- `PUT /api/reservations/{id}` — Update reservation status (`confirmed`, `cancelled`, `completed`)
- `DELETE /api/reservations/{id}` — Cancel/delete reservation

### Maintenance Requests
- `GET /api/maintenance` — List maintenance tickets
- `POST /api/maintenance` — Submit issue ticket (`low`, `medium`, `high`, `critical`)
- `PUT /api/maintenance/{id}` — Update status (`in_progress`, `resolved`) with resolution notes

### Dashboard Statistics
- `GET /api/dashboard/stats` — Aggregated counts and real-time utilization stats

---

## 11. Test Execution

The backend contains **29 deterministic test cases** executing against isolated in-memory SQLite fixtures (`aiosqlite`).

Run tests with statement coverage:
```bash
cd backend
python -m pytest -v --cov=app --cov-report=term-missing
```

*Results:*
```text
============================= 29 passed in 1.71s ==============================
TOTAL COVERAGE: 80%
```

Code quality and linting verification:
```bash
ruff check .
```

---

## 12. Docker Build and Execution

### Manual Backend Build
```bash
cd backend
docker build -t campus-resource-hub-backend:latest .
docker run -p 8000:8000 --env-file ../.env campus-resource-hub-backend:latest
```

### Manual Frontend Build
```bash
cd frontend
docker build -t campus-resource-hub-frontend:latest .
docker run -p 3000:8080 campus-resource-hub-frontend:latest
```

---

## 13. GitHub Actions Pipeline Explanation

The workflow defined in [`.github/workflows/ci-cd.yaml`](file:///.github/workflows/ci-cd.yaml) enforces strict quality and security gates across three automated jobs:

1. **Job A (`test-and-validate`)**:
   - Executes on all pull requests and pushes to `main`.
   - Runs backend Pytest suite with coverage check.
   - Executes Ruff linting.
   - Installs frontend packages and compiles Vite production bundle.
   - Validates and lints Helm charts (`helm lint`).

2. **Job B (`build-scan-publish`)**:
   - Executes only after Job A passes on `main`.
   - Builds multi-stage Docker images for backend and frontend.
   - Executes **Trivy Vulnerability Scan** (`--severity HIGH,CRITICAL --exit-code 1`).
   - Authenticates to GitHub Container Registry (`ghcr.io`).
   - Pushes images tagged with the immutable Git commit SHA.

3. **Job C (`gitops-sync`)**:
   - Automatically patches `helm/campus-resource-hub/values.yaml` with the newly published commit SHA.
   - Pushes the updated manifest back to `main`, prompting ArgoCD to initiate rollout.

---

## 14. Trivy Security Scanning

Container vulnerability scanning is embedded in the CI pipeline using Aqua Security Trivy:
```bash
trivy image --severity HIGH,CRITICAL --exit-code 1 ghcr.io/rohansingh0208/campus-resource-hub-backend:latest
```
- **Policy**: Builds fail automatically if unresolved `HIGH` or `CRITICAL` vulnerabilities exist.
- **Hardening**: Both images run as non-root unprivileged users and utilize minimal alpine/slim base images to minimize CVE attack surfaces.

---

## 15. GHCR Image Naming and Tagging

Container images are published to GitHub Container Registry following an immutable commit SHA convention:
- **Backend**: `ghcr.io/rohansingh0208/campus-resource-hub-backend:<COMMIT_SHA>`
- **Frontend**: `ghcr.io/rohansingh0208/campus-resource-hub-frontend:<COMMIT_SHA>`

The `latest` tag is updated for convenience, but Kubernetes deployments track exact commit SHAs for provenance and rollback reliability.

---

## 16. Terraform Infrastructure Setup

The Terraform module provisions cloud infrastructure in `ap-south-1` (Mumbai):

```bash
cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
```

Apply with user confirmation:
```bash
terraform apply tfplan
```

---

## 17. AWS EKS Configuration

After Terraform provisions the cluster, configure your local `kubectl` context:
```bash
aws eks --region ap-south-1 update-kubeconfig --name campus-resource-hub-eks
```

Verify connected worker nodes:
```bash
kubectl get nodes -o wide
```

---

## 18. Kubernetes and Helm Deployment

### 1. Create Dedicated Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### 2. Lint and Render Chart
```bash
helm lint helm/campus-resource-hub
helm template campus-hub helm/campus-resource-hub
```

### 3. Deploy via Helm
```bash
helm upgrade --install campus-resource-hub helm/campus-resource-hub \
  --namespace campus-resource-hub \
  --create-namespace
```

### 4. Verify Workloads
```bash
kubectl get pods,svc,ingress,hpa -n campus-resource-hub
```

---

## 19. ArgoCD GitOps Workflow

ArgoCD automates cluster synchronization from Git:

1. **Install ArgoCD**:
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```
2. **Apply Application Manifest**:
   ```bash
   kubectl apply -f argocd/application.yaml
   ```
3. **Inspect Synchronization**:
   ```bash
   kubectl get application campus-resource-hub -n argocd
   ```

---

## 20. Ingress and HPA Configuration

- **Ingress Controller**: Routes incoming HTTP traffic based on path:
  - `/` → `campus-resource-hub-frontend` Service (port 80)
  - `/api` → `campus-resource-hub-backend` Service (port 8000)
  - `/metrics` → `campus-resource-hub-backend` Service (port 8000)
- **Horizontal Pod Autoscaler (HPA)**:
  - Scale bounds: 2 minimum, 6 maximum replicas.
  - Scale threshold: 70% CPU utilization.
  - Test autoscaling with `python scripts/load_test.py --concurrency 10 --duration 60`.

---

## 21. Prometheus and Grafana Setup

Deploy the monitoring stack via Helm:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f monitoring/prometheus-values.yaml
```

Forward Grafana locally:
```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```
- **Login**: `admin` / `admin_campus_metrics_2026`
- **Dashboard**: Import [`monitoring/dashboard.json`](file:///monitoring/dashboard.json) to observe live request throughput, p95 latency, error rates, and CPU consumption.

---

## 22. Troubleshooting

Hands-on diagnostic scenarios are provided in [`troubleshooting/`](file:///troubleshooting/):
1. **`ImagePullBackOff`**: Apply `troubleshooting/broken-image.yaml` and diagnose with `kubectl describe pod` and `kubectl get events`.
2. **Empty Service Endpoints**: Apply `troubleshooting/broken-service.yaml` and diagnose label selector mismatch with `kubectl get endpoints` and `kubectl get pods --show-labels`.

---

## 23. Known Limitations

- **Email Notifications**: Pydantic validates email formats; actual outbound SMTP integration is stubbed for local portability.
- **In-Cluster Database**: PostgreSQL runs as an in-cluster deployment with PVC for classroom demonstration. For enterprise scale, migrate to Amazon RDS PostgreSQL.
- **Ingress SSL**: Uses HTTP for classroom testing; production deployments should attach AWS Certificate Manager (ACM) or cert-manager Let's Encrypt certificates.

---

## 24. Cleanup and AWS Cost Management

To avoid incurring ongoing AWS charges after evaluation:
```bash
# 1. Uninstall Helm release
helm uninstall campus-resource-hub -n campus-resource-hub

# 2. Destroy Terraform infrastructure
cd terraform
terraform destroy -auto-approve
```

---

## 25. Final Demonstration Checklist

- [x] Application source code complete (FastAPI + React 18 SPA)
- [x] 29 Pytest tests passed with 80% statement coverage
- [x] Alembic migrations working from blank database
- [x] Docker multi-stage builds with non-root security verified
- [x] `docker-compose.yml` starts full stack on ports 3000 & 8000
- [x] GitHub Actions CI/CD with Trivy scanning configured
- [x] Terraform AWS VPC & EKS 1.30 configuration complete
- [x] Helm chart with 2 replicas, HPA, and Ingress verified
- [x] ArgoCD GitOps application manifest prepared
- [x] Prometheus & Grafana dashboard specification ready
- [x] Troubleshooting lab manifests and guide created
- [x] Presentation PowerPoint generated at `demo/presentation.pptx`
- [x] Video recording narration script prepared at `demo/recording-guide.md`
