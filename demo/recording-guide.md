# DevSecOps Capstone Presentation & Demo Video Recording Guide

This guide provides a step-by-step walkthrough, narration script, timing plan, and terminal commands to record the mandatory submission video (Target duration: 5 to 8 minutes).

---

## 1. Video Structure & Timing Plan

| Section | Topic | Format | Target Duration |
| :--- | :--- | :--- | :--- |
| **Part 1** | Slide Deck Presentation (`demo/presentation.pptx`) | Screen Share Slides | 2 min |
| **Part 2** | Codebase & Project Architecture Tour | VS Code / IDE | 1 min |
| **Part 3** | Automated Testing & Code Quality Gates | Terminal (`pytest`) | 45 sec |
| **Part 4** | Containerization, Trivy Scan & GitHub Actions | GitHub Actions UI | 1 min |
| **Part 5** | Terraform AWS EKS & Kubernetes Deployments | Terminal (`kubectl`) | 1.5 min |
| **Part 6** | ArgoCD GitOps Continuous Delivery & Self-Healing | ArgoCD Web UI | 1 min |
| **Part 7** | Live Application Walkthrough & Observability | Browser & Grafana | 1 min |

---

## 2. Part-by-Part Narration Script & Commands

### Part 1: Slide Deck Presentation (0:00 – 2:00)
- **Visual**: Full-screen PowerPoint presentation (`demo/presentation.pptx`).
- **Narration Script**:
  > *"Hello, my name is Rohan Singh, and this is my final DevSecOps capstone project: **Campus Resource Hub**. Today, I will walk you through the complete software delivery lifecycle, from full-stack development, automated testing, container security with Trivy, Infrastructure as Code using Terraform on AWS EKS, GitOps deployment via ArgoCD, and observability with Prometheus and Grafana."*
- Advance through Slides 1 through 8, highlighting:
  1. The problem of campus facility scheduling and maintenance tracking.
  2. The multi-stage Docker build with non-root security.
  3. The Terraform VPC & EKS cluster in `ap-south-1`.
  4. The ArgoCD GitOps synchronization loop.
  5. The Prometheus metrics and Grafana dashboard.

---

### Part 2: Codebase Structure & Architecture (2:00 – 3:00)
- **Visual**: VS Code showing the repository root.
- **Narration Script**:
  > *"Here is the project repository structure. In `backend/`, we have our FastAPI application structured into models, schemas, services, and routes, backed by PostgreSQL migrations via Alembic. In `frontend/`, we have our React 18 SPA built with Vite and Lucide icons. In `terraform/`, we have our modular AWS VPC and EKS infrastructure. In `helm/`, our production-grade Helm chart with HPA and Ingress."*

---

### Part 3: Automated Pytest Suite Execution (3:00 – 3:45)
- **Visual**: Terminal in `backend/`.
- **Command to run**:
  ```bash
  cd backend
  python -m pytest -v --cov=app
  ```
- **Narration Script**:
  > *"Our test suite executes 29 automated tests against isolated SQLite fixtures, achieving 80% statement coverage. Crucially, tests validate reservation conflict detection, ensuring double bookings are rejected with HTTP 409, and verify `/health`, `/ready`, and Prometheus `/metrics` endpoints."*

---

### Part 4: GitHub Actions & Trivy Container Security (3:45 – 4:45)
- **Visual**: Browser open to GitHub Repository > Actions tab: `https://github.com/RohanSingh0208/DevOps-Project/actions`.
- **Narration Script**:
  > *"On every commit to `main`, GitHub Actions triggers our three-stage pipeline. Job A runs pytest, Ruff linting, and Helm chart validation. Once passed, Job B builds the multi-stage Docker images and scans them with Aqua Security Trivy, configured with `--severity HIGH,CRITICAL --exit-code 1`. Clean images are then published to GitHub Container Registry tagged with the immutable commit SHA. Finally, Job C updates the desired image tag in Git, triggering GitOps deployment."*

---

### Part 5: Kubernetes, Helm & Terraform (4:45 – 6:15)
- **Visual**: Terminal executing cluster inspection commands.
- **Commands to run**:
  ```bash
  # 1. Verify Namespaces & Pods
  kubectl get pods -n campus-resource-hub -o wide

  # 2. Verify Services & Ingress
  kubectl get svc,ingress -n campus-resource-hub

  # 3. Verify Horizontal Pod Autoscaler
  kubectl get hpa -n campus-resource-hub

  # 4. Show Pod Non-Root Security Context
  kubectl get pod -n campus-resource-hub -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].spec.securityContext}'
  ```
- **Narration Script**:
  > *"In our Kubernetes cluster, we have our frontend and backend running with two replicas each for high availability, alongside a persistent PostgreSQL pod. Ingress-Nginx routes external traffic, and the Horizontal Pod Autoscaler monitors CPU consumption to scale up to 6 pods under load."*

---

### Part 6: ArgoCD GitOps Continuous Delivery (6:15 – 7:15)
- **Visual**: Browser at ArgoCD UI (`https://localhost:8080`).
- **Action**: Show `campus-resource-hub` application with status **Synced** and **Healthy**.
- **Demonstration**:
  > *"In ArgoCD, our application is continuously synchronized with the `main` branch. If someone modifies a pod or service directly in the cluster, ArgoCD detects the drift and immediately reconciles it back to our declarative Git configuration."*

---

### Part 7: Application Tour & Grafana Metrics (7:15 – 8:00)
- **Visual**: Browser showing Frontend UI (`http://localhost:3000`) and Grafana (`http://localhost:3000`).
- **Action**:
  1. Click **Resources** to show classrooms, labs, and equipment cards.
  2. Click **Reservations** to show active bookings.
  3. Click **Maintenance** to show open tickets.
  4. Switch to Grafana dashboard tab: show live HTTP request rate, latency, and CPU graphs.
- **Closing Statement**:
  > *"This concludes the demonstration of Campus Resource Hub. Thank you for your time and evaluation."*

---

## 3. Pre-Recording Checklist
- [ ] Screen recorder configured (OBS Studio / Loom / Camtasia) at 1080p 30/60fps.
- [ ] Microphone tested with clear audio and minimal background noise.
- [ ] Browser tabs pre-opened:
  - Slide deck in Presentation Mode.
  - GitHub Repository Actions page.
  - ArgoCD Console (`https://localhost:8080`).
  - Campus Resource Hub Web UI (`http://localhost:3000`).
  - Grafana Dashboard (`http://localhost:3000`).
- [ ] Terminal open with clean prompt and font size enlarged (16–18pt) for video legibility.
