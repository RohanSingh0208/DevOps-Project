terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.30"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }

  # Local state by default. For production team collaboration,
  # configure S3 backend and DynamoDB state locking below:
  # backend "s3" {
  #   bucket         = "campus-resource-hub-tf-state-YOUR_ACCOUNT_ID"
  #   key            = "eks/terraform.tfstate"
  #   region         = "ap-south-1"
  #   dynamodb_table = "campus-resource-hub-tf-locks"
  #   encrypt        = true
  # }
}
