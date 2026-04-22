# Terraform configuration for AWS deployment

aws_region     = "eu-north-1"
environment    = "production"
app_name       = "finops-ai"
instance_type  = "t3.micro"
container_port = 8501

tags = {
  Owner      = "DevOps"
  Project    = "FinOps-AI"
  CostCenter = "Engineering"
}
