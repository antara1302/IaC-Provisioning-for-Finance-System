# Create an S3 bucket for Terraform state (run this separately first)
# aws s3 mb s3://finops-terraform-state-$(date +%s) --region us-east-1
# Then update the backend configuration in main.tf

# Example backend configuration for remote state:
# backend "s3" {
#   bucket         = "finops-terraform-state-XXXXXXXXX"
#   key            = "finops/terraform.tfstate"
#   region         = "us-east-1"
#   encrypt        = true
#   dynamodb_table = "terraform-locks"
# }
