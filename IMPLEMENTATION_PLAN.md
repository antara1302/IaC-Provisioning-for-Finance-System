# ─────────────────────────────────────────────────────────────────────────────
# IMPLEMENTATION PLAN: AWS CI/CD Pipeline Automation for FinOps AI
# ─────────────────────────────────────────────────────────────────────────────

## 📌 EXECUTIVE SUMMARY

This document outlines the complete CI/CD automation strategy to replace your manual AWS deployment process with a fully automated GitHub Actions pipeline integrated with Terraform infrastructure as code.

---

## 🎯 OBJECTIVES

✅ Automate Docker image building and testing
✅ Push images to Amazon ECR (Elastic Container Registry)
✅ Provision AWS infrastructure using Terraform
✅ Deploy containerized application to EC2
✅ Implement health checks and monitoring
✅ Enable rollback capabilities
✅ Reduce manual intervention and deployment time

---

## 📊 CURRENT STATE vs. DESIRED STATE

### Current State (Manual Deployment)
```
Developer pushes code → Manual build of Docker image → 
Manual push to AWS → Manual Terraform deployment → 
Manual SSH to verify → Application running
```

### Desired State (Automated Deployment)
```
Developer pushes to main → GitHub Actions triggers → 
Build & Test → Push to ECR → Terraform Plan & Apply → 
Health Checks → Notification → Application running
```

---

## 🏗️ IMPLEMENTATION ARCHITECTURE

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     GitHub Repository (main branch)                    │
└────────────────────────┬────────────────────────────────────────────────┘
                         │ (push event)
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│         STAGE 1: BUILD & TEST (Ubuntu Latest)                          │
├─────────────────────────────────────────────────────────────────────────┤
│ • Checkout code                                                          │
│ • Setup Python environment                                              │
│ • Install dependencies                                                  │
│ • Run unit tests (pytest)                                               │
│ • Build Docker image                                                    │
│ • Test Docker container locally                                         │
└────────────────────────┬────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         │ (if main branch)              │
         ▼                               ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   STAGE 2: PUSH TO ECR                                          │
    ├─────────────────────────────────────────────────────────────────┤
    │ • Authenticate with AWS                                         │
    │ • Login to ECR                                                  │
    │ • Build image with BuildX                                       │
    │ • Push image to ECR with tags (commit SHA + latest)             │
    │ • Enable layer caching                                          │
    └────────────┬──────────────────────────────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   STAGE 3: TERRAFORM PLAN                                       │
    ├─────────────────────────────────────────────────────────────────┤
    │ • Validate Terraform code                                       │
    │ • Check code formatting                                         │
    │ • Generate execution plan                                       │
    │ • Upload plan artifact                                          │
    └────────────┬──────────────────────────────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   STAGE 4: TERRAFORM APPLY & DEPLOY                             │
    ├─────────────────────────────────────────────────────────────────┤
    │ • Download plan artifact                                        │
    │ • Apply infrastructure changes                                  │
    │ • Provision AWS resources:                                      │
    │   - VPC with public/private subnets                             │
    │   - Security Groups                                             │
    │   - EC2 instance                                                │
    │   - IAM roles and policies                                      │
    │ • Execute user data script to deploy application                │
    │ • Output infrastructure details                                 │
    └────────────┬──────────────────────────────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   STAGE 5: HEALTH CHECKS & VALIDATION                           │
    ├─────────────────────────────────────────────────────────────────┤
    │ • Wait 30 seconds for application startup                       │
    │ • HTTP health check to Streamlit app                            │
    │ • Retry logic (5 attempts, 15 sec intervals)                    │
    │ • Verify EC2 instance status                                    │
    │ • Check CloudWatch logs integration                             │
    └────────────┬──────────────────────────────────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │   STAGE 6: NOTIFICATIONS                                        │
    ├─────────────────────────────────────────────────────────────────┤
    │ • Generate deployment summary                                   │
    │ • Output access URLs                                            │
    │ • Display deployment metadata                                   │
    │ • Success/Failure status                                        │
    └─────────────────────────────────────────────────────────────────┘
```

---

## 📁 FILE STRUCTURE

Files created/modified:

```
IaC-FinOps/
├── .github/
│   └── workflows/
│       └── deploy.yml                 ← UPDATED (complete pipeline)
├── terraform/
│   ├── main.tf                        ← UPDATED (AWS provider setup)
│   ├── aws.tf                         ← NEW (VPC, EC2, networking)
│   ├── ecr.tf                         ← NEW (ECR repository)
│   ├── user_data.sh                   ← NEW (EC2 bootstrap script)
│   ├── terraform.tfvars               ← NEW (configuration)
│   └── BACKEND_SETUP.md               ← NEW (S3 backend setup)
├── scripts/
│   └── setup_aws.sh                   ← NEW (one-time AWS setup)
├── AWS_DEPLOYMENT_GUIDE.md            ← NEW (comprehensive guide)
├── IMPLEMENTATION_PLAN.md             ← NEW (this file)
└── CI_CD_OPERATIONS.md                ← NEW (operations reference)
```

---

## 🔧 TECHNICAL COMPONENTS

### 1. GitHub Actions Workflow
- **File**: `.github/workflows/deploy.yml`
- **Triggers**: Push to main branch
- **Stages**: 6 parallel/sequential stages
- **Total Runtime**: ~15-20 minutes

### 2. Terraform Configuration
- **Provider**: AWS (v5.0+)
- **Resources**:
  - VPC with public/private subnets
  - Internet Gateway and Route Tables
  - EC2 instance (t3.medium default)
  - Security Groups (HTTP, HTTPS, Streamlit port)
  - IAM roles and policies
  - CloudWatch Log Group
  - ECR repository with lifecycle policies

### 3. Infrastructure Components
- **Compute**: EC2 instance running Docker
- **Container Registry**: Amazon ECR
- **Networking**: Custom VPC with security controls
- **Logging**: CloudWatch Logs integration
- **State Management**: S3 backend with encryption (optional)

### 4. Application Deployment
- **Container Runtime**: Docker on EC2
- **Application**: Streamlit (Python)
- **Port**: 8501
- **Auto-restart**: Enabled via Docker restart policy
- **Logging**: CloudWatch integration

---

## ⚙️ DETAILED IMPLEMENTATION STEPS

### STEP 1: Create AWS IAM User (One-time)

```bash
# Create IAM user for GitHub Actions
aws iam create-user --user-name github-actions-finops

# Create custom policy for minimal permissions
# (see AWS_DEPLOYMENT_GUIDE.md for full policy)

# Attach policy
aws iam put-user-policy --user-name github-actions-finops \
  --policy-name GitHubActionsPolicy \
  --policy-document file://policy.json

# Generate access keys
aws iam create-access-key --user-name github-actions-finops
```

### STEP 2: Add GitHub Secrets

Navigate to: **Repository Settings > Secrets and variables > Actions**

Add these secrets:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### STEP 3: Setup Terraform Backend (Optional but Recommended)

```bash
# Create S3 bucket
aws s3 mb s3://finops-terraform-state-XXXXXXXXX --region us-east-1

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Update terraform/main.tf backend configuration
```

### STEP 4: Configure Terraform Variables

Edit `terraform/terraform.tfvars`:
```hcl
aws_region     = "us-east-1"
environment    = "production"
app_name       = "finops-ai"
instance_type  = "t3.medium"
container_port = 8501
```

### STEP 5: Initialize Terraform (Local)

```bash
cd terraform
terraform init
terraform fmt -recursive
terraform validate
```

### STEP 6: Push to GitHub

```bash
git add .
git commit -m "feat: Add AWS CI/CD pipeline automation"
git push origin main
```

### STEP 7: Monitor Pipeline Execution

Go to: **GitHub > Actions > FinOps CI/CD Pipeline - AWS Deployment**

Each stage will show:
- Build logs
- Terraform plan details
- Infrastructure outputs
- Health check results

### STEP 8: Access Deployed Application

After successful deployment:
```
Application URL: http://<PUBLIC_IP>:8501
```

Access URL is provided in:
- Pipeline logs (Stage 4 output)
- Deployment artifact (`deployment_info.json`)

---

## 🔐 SECURITY CONSIDERATIONS

### 1. IAM Permissions
- Use minimal required permissions (not AdministratorAccess)
- Separate policy for GitHub Actions user
- Regular key rotation (every 90 days recommended)

### 2. Secrets Management
- Store AWS credentials only in GitHub Secrets
- Never commit `.env` or credentials files
- Use IAM roles for EC2 instance access

### 3. Network Security
- VPC isolation for resources
- Security Group rules restrict unnecessary ports
- SSH access available but should be restricted in production

### 4. State Management
- Enable S3 encryption for Terraform state
- Enable versioning for state files
- Use DynamoDB locking to prevent concurrent modifications

### 5. Container Security
- ECR image scanning enabled
- Regular base image updates
- Remove sensitive data from images

---

## 📈 PERFORMANCE METRICS

### Deployment Time Breakdown
| Stage | Duration | Notes |
|-------|----------|-------|
| Build & Test | 3-5 min | Depends on dependencies |
| Push to ECR | 2-3 min | Image size dependent |
| Terraform Plan | 1-2 min | Cloud API calls |
| Terraform Apply | 3-5 min | Resource creation |
| Health Checks | 2-3 min | Wait + retries |
| Notifications | 1 min | Final summary |
| **Total** | **12-19 min** | End-to-end |

### Cost Estimation (AWS)
- **EC2 t3.medium**: ~$0.0416/hour (~$30/month)
- **ECR**: $0.10 per GB stored (~$1-5/month for app)
- **CloudWatch Logs**: ~$0.50/GB ingested (~$2-5/month)
- **Total Monthly**: ~$40-45 (may vary by region)

---

## 🔄 OPERATIONAL WORKFLOWS

### Deploy New Version
```
1. Make code changes
2. Commit and push to main
3. Pipeline triggers automatically
4. Monitor in GitHub Actions
5. Application updates within 15-20 minutes
```

### Manual Deployment (if needed)
```bash
cd terraform
terraform apply -var="docker_image_uri=XXXXX"
```

### Rollback Procedure
```bash
# Check previous version in ECR
aws ecr describe-images --repository-name finops-ai

# Update Terraform variable with previous image
terraform apply -var="docker_image_uri=<PREVIOUS_IMAGE_URI>"
```

### Monitor Logs
```bash
# Real-time logs
aws logs tail /aws/ec2/finops-ai --follow

# Specific time range
aws logs filter-log-events \
  --log-group-name /aws/ec2/finops-ai \
  --start-time $(date -d '1 hour ago' +%s)000
```

---

## 🧪 TESTING THE PIPELINE

### Test 1: Verify Build Stage
- Push a simple change (e.g., README update)
- Verify Docker image builds successfully
- Check image is testable locally

### Test 2: Verify ECR Push
- Confirm image is pushed to ECR
- Check image tags match commit SHA
- Verify image scanning results

### Test 3: Verify Infrastructure
- Confirm VPC is created
- Check Security Groups rules
- Verify EC2 instance is running

### Test 4: Verify Application
- Access application URL
- Test Streamlit interface
- Check CloudWatch logs

---

## 📊 MONITORING & ALERTING

### Key Metrics to Monitor
1. **Pipeline Success Rate**: Target 100%
2. **Deployment Duration**: Monitor for increases
3. **Application Uptime**: Track via health checks
4. **Error Rates**: Monitor CloudWatch metrics
5. **Cost Tracking**: Monitor AWS billing

### Setup Alerts
```bash
# Email alerts for pipeline failures
# Slack integration for instant notifications
# CloudWatch alarms for instance health
```

---

## 🐛 TROUBLESHOOTING GUIDE

### Issue: Pipeline fails at "Push to ECR"
**Solution**: 
- Verify AWS credentials in GitHub Secrets
- Check IAM permissions include ECR access
- Verify ECR repository exists

### Issue: Application not accessible after deployment
**Solution**:
- Wait 2-3 minutes for Docker to start
- Check Security Group allows port 8501
- Verify EC2 instance status: `aws ec2 describe-instance-status`
- Check logs: `aws logs tail /aws/ec2/finops-ai --follow`

### Issue: Terraform apply times out
**Solution**:
- Check AWS service quotas in region
- Verify IAM permissions are sufficient
- Check network connectivity

### Issue: Health check fails
**Solution**:
- Check application logs in CloudWatch
- Verify Docker container is running: SSH to instance and run `docker ps`
- Check Security Group ingress rules

---

## 🚀 FUTURE ENHANCEMENTS

1. **Auto-scaling**: Add ASG for multiple instances
2. **Load Balancing**: Implement ALB/NLB
3. **Database**: Add RDS for persistent data
4. **Monitoring**: Integrate CloudWatch dashboards
5. **Notifications**: Add Slack/Email alerts
6. **Blue-Green Deployment**: Zero-downtime updates
7. **Multi-region**: Replicate across AWS regions
8. **Cost Optimization**: Reserved instances, spot instances

---

## 📞 SUPPORT & RESOURCES

- **GitHub Actions Docs**: https://docs.github.com/actions
- **Terraform AWS Provider**: https://registry.terraform.io/providers/hashicorp/aws
- **AWS ECR Guide**: https://docs.amazon.com/ecr/latest/userguide/
- **Streamlit Deployment**: https://docs.streamlit.io/deploy/overview

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Create GitHub Secrets (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- [ ] Run setup_aws.sh script
- [ ] Update terraform.tfvars with your settings
- [ ] Configure S3 backend (optional)
- [ ] Test pipeline with code push
- [ ] Verify application deployment
- [ ] Set up monitoring and alerts
- [ ] Document any customizations

---

**Document Version**: 1.0
**Last Updated**: 2024
**Status**: Ready for Implementation
