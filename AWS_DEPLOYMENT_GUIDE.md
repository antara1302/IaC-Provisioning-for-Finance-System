# AWS CI/CD Pipeline Configuration
# This file contains setup instructions and best practices

## 🔐 GitHub Secrets Setup

Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions):

### Required AWS Credentials:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

### Optional Secrets for Enhanced Monitoring:
```
SLACK_WEBHOOK_URL      # For Slack notifications
PAGERDUTY_API_KEY      # For incident management
```

## 📋 Setup Instructions

### 1. Create IAM User for GitHub Actions

```bash
# Create IAM user
aws iam create-user --user-name github-actions-finops

# Attach policy for deployment
aws iam attach-user-policy --user-name github-actions-finops \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# For production, create a custom policy with minimal permissions
```

### 2. Generate Access Keys

```bash
aws iam create-access-key --user-name github-actions-finops
```

### 3. Add Credentials to GitHub

1. Go to your repository on GitHub
2. Navigate to Settings > Secrets and variables > Actions
3. Add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### 4. Initialize Terraform State Backend (Optional but Recommended)

```bash
# Create S3 bucket for state
aws s3 mb s3://finops-terraform-state-$(date +%s) --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket finops-terraform-state-XXXXX \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Enable encryption on S3 bucket
aws s3api put-bucket-encryption \
  --bucket finops-terraform-state-XXXXX \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Update terraform/main.tf with backend configuration
```

## 🚀 Pipeline Stages

### Stage 1: Build & Test
- Checks out code
- Installs Python dependencies
- Runs unit tests
- Builds Docker image
- Tests container locally

### Stage 2: Push to ECR
- Authenticates with AWS
- Builds and pushes Docker image to Amazon ECR
- Tags with commit SHA and 'latest'

### Stage 3: Terraform Plan
- Validates Terraform code
- Checks code formatting
- Creates and uploads deployment plan

### Stage 4: Terraform Apply
- Deploys infrastructure to AWS
- Provisions VPC, Security Groups, EC2, ECR
- Outputs instance details

### Stage 5: Health Checks
- Waits for application to start
- Verifies application is responding
- Checks EC2 instance status

### Stage 6: Notifications
- Sends deployment summary
- Provides access URLs and credentials

## 📊 Architecture Overview

```
GitHub Repository
       ↓
   Triggers on push to main
       ↓
   Build & Test (Ubuntu Latest)
       ↓
   Push Docker Image to ECR
       ↓
   Terraform Plan (validate + plan)
       ↓
   Terraform Apply (provision infrastructure)
       ↓
   Health Checks (verify deployment)
       ↓
   Notifications (send results)
       ↓
   Accessible at: http://<public_ip>:8501
```

## 🛡️ Security Best Practices

1. **Minimal IAM Permissions**: Use a custom IAM policy instead of AdministratorAccess
2. **Encrypted Terraform State**: Store state in S3 with encryption
3. **State Locking**: Use DynamoDB to prevent concurrent modifications
4. **Security Groups**: Restrict SSH and HTTP/HTTPS access in production
5. **Secrets Management**: Never commit AWS credentials to Git
6. **VPC Isolation**: Resources are deployed in private/public subnets

## 🔧 Customization

### Change AWS Region
Edit `terraform/terraform.tfvars`:
```hcl
aws_region = "us-west-2"  # Change region
```

### Change Instance Type
Edit `terraform/terraform.tfvars`:
```hcl
instance_type = "t3.large"  # For more resources
```

### Change Application Port
Edit `terraform/terraform.tfvars`:
```hcl
container_port = 8501  # Streamlit port
```

## 📝 Monitoring & Logs

### CloudWatch Logs
```bash
# View application logs
aws logs tail /aws/ec2/finops-ai --follow

# View specific log stream
aws logs tail /aws/ec2/finops-ai --stream-name ecs-agent --follow
```

### EC2 Status
```bash
# Check instance status
aws ec2 describe-instance-status --instance-ids i-xxxxxxxxx

# View instance details
aws ec2 describe-instances --instance-ids i-xxxxxxxxx
```

## 🔄 Rollback Procedure

```bash
# Revert to previous Terraform state
aws s3 cp s3://finops-terraform-state-XXXXX/finops/terraform.tfstate.backup \
  s3://finops-terraform-state-XXXXX/finops/terraform.tfstate

# Re-initialize and apply
cd terraform
terraform init
terraform apply -auto-approve
```

## 🐛 Troubleshooting

### Pipeline fails at "Push to ECR"
- Verify AWS credentials in GitHub Secrets
- Check IAM permissions for ECR

### Application not responding after deployment
- Wait 2-3 minutes for Docker to start
- Check CloudWatch logs: `aws logs tail /aws/ec2/finops-ai --follow`
- Verify Security Group allows port 8501

### Terraform plan fails
- Ensure `docker_image_uri` variable is set correctly
- Check AWS quota limits in the region
- Verify IAM permissions

## 📚 Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECR Best Practices](https://docs.aws.amazon.com/AmazonECR/latest/userguide/best-practices.html)
- [Streamlit Deployment Guide](https://docs.streamlit.io/deploy/overview)
