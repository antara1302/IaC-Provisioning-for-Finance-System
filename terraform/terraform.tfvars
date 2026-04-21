# Terraform configuration for AWS deployment

aws_region     = "us-east-1"
environment    = "production"
app_name       = "finops-ai"
instance_type  = "t3.medium"
container_port = 8501

tags = {
  Owner      = "DevOps"
  Project    = "FinOps-AI"
  CostCenter = "Engineering"
}
