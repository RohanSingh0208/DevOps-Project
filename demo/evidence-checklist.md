# DevSecOps Capstone Evidence Checklist

This document catalogs verifiable evidence for all 10 modules required by the 100-point capstone grading rubric.

| Rubric Module | Points | Deliverable Location | Verification Command / Evidence | Status |
| :--- | :---: | :--- | :--- | :---: |
| **Module 1: Full-Stack App** | 10 | `backend/app/`, `frontend/src/` | REST APIs, PostgreSQL ORM, Alembic migrations, React SPA | **VERIFIED (LOCAL)** |
| **Module 2: Testing & QA** | 10 | `backend/tests/` | `python -m pytest` (29 passed, 80% coverage) | **VERIFIED (LOCAL)** |
| **Module 3: Git & GitHub** | 5 | `.gitignore`, Git commits | Repository: `https://github.com/RohanSingh0208/DevOps-Project` | **READY FOR PUSH** |
| **Module 4: Docker & Compose** | 10 | `Dockerfile`, `docker-compose.yml` | Multi-stage slim images, non-root users, Compose stack | **VERIFIED (CONFIG)** |
| **Module 5: GitHub Actions** | 15 | `.github/workflows/ci-cd.yaml` | Pytest gate, Vite build, SHA-tagged image push, GitOps update | **VERIFIED (CONFIG)** |
| **Module 6: Trivy DevSecOps** | 5 | `.github/workflows/ci-cd.yaml` | Aqua Trivy severity HIGH,CRITICAL gate with exit-code 1 | **VERIFIED (CONFIG)** |
| **Module 7: Terraform & AWS** | 15 | `terraform/` | VPC, 4 subnets, IGW, NAT, EKS 1.30, Node Group, IRSA | **VALIDATED (IAC CODE)** |
| **Module 8: Kubernetes & Helm**| 15 | `helm/campus-resource-hub/`, `k8s/` | 2 replicas, Ingress, HPA (70% CPU), probes, PVC | **VERIFIED (CHARTS)** |
| **Module 9: Observability** | 10 | `monitoring/` | Prometheus Operator, ServiceMonitor, Grafana Dashboard | **VERIFIED (CONFIG)** |
| **Module 10: Presentation** | 5 | `demo/presentation.pptx`, `README.md`| 8-Slide PowerPoint, Recording Guide, Master README | **VERIFIED (ASSETS)** |
| **Troubleshooting Lab** | Bonus | `troubleshooting/` | ImagePullBackOff & Empty Service Endpoints labs | **VERIFIED (MANIFESTS)**|
| **TOTAL SCORE POTENTIAL** | **100** | | | **READY FOR SUBMISSION** |

---

## Local Verification Evidence Log

### 1. Pytest Test Results
```text
tests/test_health.py::test_health_returns_ok PASSED                      [  3%]
tests/test_health.py::test_root_endpoint PASSED                          [  6%]
tests/test_health.py::test_metrics_endpoint_responds PASSED              [ 10%]
tests/test_maintenance.py::test_create_maintenance_request PASSED        [ 13%]
tests/test_maintenance.py::test_create_maintenance_invalid_priority PASSED [ 17%]
tests/test_maintenance.py::test_get_maintenance_not_found PASSED         [ 20%]
tests/test_maintenance.py::test_list_maintenance PASSED                  [ 24%]
tests/test_maintenance.py::test_update_maintenance_status_to_resolved PASSED [ 27%]
tests/test_maintenance.py::test_delete_maintenance_request PASSED        [ 31%]
tests/test_maintenance.py::test_filter_maintenance_by_priority PASSED    [ 34%]
tests/test_reservations.py::test_create_reservation_success PASSED       [ 37%]
tests/test_reservations.py::test_create_reservation_end_before_start PASSED [ 41%]
tests/test_reservations.py::test_overlapping_reservation_rejected PASSED [ 44%]
tests/test_reservations.py::test_non_overlapping_reservations_allowed PASSED [ 48%]
tests/test_reservations.py::test_get_reservation_not_found PASSED        [ 51%]
tests/test_reservations.py::test_list_reservations PASSED                [ 55%]
tests/test_reservations.py::test_update_reservation_status PASSED        [ 58%]
tests/test_reservations.py::test_delete_reservation PASSED               [ 62%]
tests/test_resources.py::test_create_resource_success PASSED             [ 65%]
tests/test_resources.py::test_create_resource_missing_required_field PASSED [ 68%]
tests/test_resources.py::test_create_resource_invalid_type PASSED        [ 72%]
tests/test_resources.py::test_get_resource_not_found PASSED              [ 75%]
tests/test_resources.py::test_list_resources_initially_empty PASSED      [ 79%]
tests/test_resources.py::test_list_and_retrieve_resource PASSED          [ 82%]
tests/test_resources.py::test_update_resource PASSED                     [ 86%]
tests/test_resources.py::test_update_nonexistent_resource PASSED         [ 89%]
tests/test_resources.py::test_delete_resource PASSED                     [ 93%]
tests/test_resources.py::test_delete_nonexistent_resource PASSED         [ 96%]
tests/test_resources.py::test_filter_resources_by_type PASSED            [100%]

============================= 29 passed in 1.71s ==============================
Coverage: 80% (524 statements, 103 missed)
```

### 2. Frontend Production Build Result
```text
> campus-resource-hub-frontend@1.0.0 build
> tsc --noEmit && vite build

vite v5.4.21 building for production...
transforming...
✓ 2686 modules transformed.
dist/index.html                   1.07 kB │ gzip:   0.54 kB
dist/assets/index-CXhux-b9.css   13.60 kB │ gzip:   3.16 kB
dist/assets/index-Dm8Lf5tE.js    68.61 kB │ gzip:  16.52 kB
dist/assets/vendor-wEA5KnES.js  163.39 kB │ gzip:  53.33 kB
dist/assets/charts-BAOT0y5P.js  393.24 kB │ gzip: 106.87 kB
✓ built in 20.33s
```
