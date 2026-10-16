provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CampusResourceHub"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.project_owner
    }
  }
}
