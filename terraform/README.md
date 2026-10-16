# Terraform AWS Infrastructure for Campus Resource Hub

This module defines and provisions the cloud infrastructure required for running the Campus Resource Hub on Amazon EKS.

## Architecture

- **AWS Region**: `ap-south-1` (Mumbai)
- **VPC**: 10.0.0.0/16 with DNS hostnames and resolution enabled
- **Public Subnets**: 2 Availability Zones (`10.0.1.0/24`, `10.0.2.0/24`) with Internet Gateway and `kubernetes.io/role/elb = 1`
- **Private Subnets**: 2 Availability Zones (`10.0.11.0/24`, `10.0.12.0/24`) with `kubernetes.io/role/internal-elb = 1`
- **NAT Gateway**: Outbound internet egress for worker nodes in private subnets
- **EKS Cluster**: Kubernetes 1.30 managed control plane with public and private endpoint access
- **Managed Node Group**: 2x `t3.medium` worker nodes with auto-scaling (1–4)
- **OIDC Provider**: Enabled for IAM Roles for Service Accounts (IRSA)

## Prerequisites

1. AWS CLI installed and configured:
   ```bash
   aws configure
   # Enter AWS Access Key ID, Secret Access Key, and Default region (ap-south-1)
   ```
2. Terraform CLI (>= 1.5.0):
   ```bash
   terraform version
   ```
3. `kubectl` installed for interacting with the cluster after provisioning:
   ```bash
   kubectl version --client
   ```

## Workflow & Step-by-Step Execution

### 1. Initialize Terraform
Downloads the AWS and TLS provider plugins:
```bash
cd terraform
terraform init
```

### 2. Format and Validate Code
```bash
terraform fmt -check
terraform validate
```

### 3. Generate and Inspect Plan
```bash
# Copy example variables
cp terraform.tfvars.example terraform.tfvars

# Review proposed changes
terraform plan -out=tfplan
```

### 4. Apply Infrastructure (Requires User Approval)
> [!WARNING]
> Running `terraform apply` provisions real AWS resources (EKS, NAT Gateway, EC2 instances) which will incur charges under your AWS account until destroyed.
```bash
terraform apply tfplan
```

### 5. Configure `kubectl` to Access EKS
After `terraform apply` completes:
```bash
aws eks --region ap-south-1 update-kubeconfig --name campus-resource-hub-eks

# Verify connected worker nodes
kubectl get nodes -o wide
```

### 6. Clean Up and Teardown
To avoid unwanted AWS charges after your evaluation or presentation:
```bash
terraform destroy
```

## Production State Note
In production team workflows, configure an S3 remote backend with DynamoDB locking in `versions.tf` to avoid state drift and concurrency issues.
