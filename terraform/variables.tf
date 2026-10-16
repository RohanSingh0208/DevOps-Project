variable "aws_region" {
  description = "Target AWS Region for infrastructure deployment"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Base project name used in resource names and tags"
  type        = string
  default     = "campus-resource-hub"
}

variable "project_owner" {
  description = "Owner of the project (e.g. GitHub handle or student name)"
  type        = string
  default     = "RohanSingh0208"
}

variable "vpc_cidr" {
  description = "CIDR block for the dedicated VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets across availability zones"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets across availability zones"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "cluster_version" {
  description = "Kubernetes version for Amazon EKS cluster"
  type        = string
  default     = "1.30"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS managed worker node group (cost-conscious)"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "node_desired_capacity" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 2
}

variable "node_min_capacity" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "node_max_capacity" {
  description = "Maximum number of worker nodes for autoscaling"
  type        = number
  default     = 4
}

variable "enable_nat_gateway" {
  description = "Whether to provision NAT Gateway for private subnets (set to true for full private egress, false to economize in lab)"
  type        = bool
  default     = true
}
