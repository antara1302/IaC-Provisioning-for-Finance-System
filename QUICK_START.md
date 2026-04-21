# ✅ QUICK START CHECKLIST

## Pre-Deployment Setup (5-10 minutes)

### 1. AWS Account Prerequisites
- [ ] AWS account with credentials configured locally
- [ ] AWS CLI installed (`aws --version`)
- [ ] Appropriate IAM permissions (Admin access initially, then restrict)
- [ ] Selected AWS region (default: us-east-1)

### 2. GitHub Setup
- [ ] Repository cloned locally
- [ ] Write access to the repository
- [ ] GitHub CLI installed (optional: `gh --version`)

### 3. Local Tools
- [ ] Terraform installed (`terraform --version` ≥ 1.0)
- [ ] Docker installed (`docker --version`)
- [ ] Git installed (`git --version`)

---

## Deployment Setup (10-15 minutes)

### Step 1: Create GitHub Secrets ⚙️

**Location**: Repository Settings > Secrets and variables > Actions

```bash
# Generate AWS credentials
# Save these TWO values as GitHub Secrets:
1. AWS_ACCESS_KEY_ID = your-access-key-id
2. AWS_SECRET_ACCESS_KEY = your-secret-access-key
```

**How to get credentials:**
```bash
# Run the setup script (Linux/Mac)
bash scripts/setup_aws.sh

# Or manually:
aws iam create-user --user-name github-actions-finops
aws iam create-access-key --user-name github-actions-finops
```

### Step 2: Configure Terraform ⚙️

Edit `terraform/terraform.tfvars`:
```hcl
# Required customizations:
aws_region       = "us-east-1"              # Change if needed
environment      = "production"             # dev/staging/production
app_name         = "finops-ai"              # Application name
instance_type    = "t3.medium"              # t3.small for cost savings
container_port   = 8501                     # Streamlit port
```

### Step 3: Validate Locally (Optional) ✅

```bash
cd terraform
terraform init
terraform validate
terraform fmt -recursive
terraform plan -var="docker_image_uri=ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finops-ai:latest"
```

### Step 4: Push to GitHub 🚀

```bash
git add .
git commit -m "feat: Add AWS CI/CD automation"
git push origin main
```

---

## Deployment Execution (15-20 minutes)

### Step 5: Monitor Pipeline

**GitHub Actions Dashboard:**
1. Go to: **GitHub Repository > Actions**
2. Click on: **FinOps CI/CD Pipeline - AWS Deployment**
3. Watch the pipeline progress through stages:
   - ✅ Build & Test (3-5 min)
   - ✅ Push to ECR (2-3 min)
   - ✅ Terraform Plan (1-2 min)
   - ✅ Terraform Apply (3-5 min)
   - ✅ Health Checks (2-3 min)
   - ✅ Notifications (1 min)

### Step 6: Access Application 🎉

**After successful deployment:**

```bash
# Option 1: From pipeline logs
# Stage 4 output shows: "Application URL: http://<PUBLIC_IP>:8501"

# Option 2: From deployment artifact
gh run download <RUN_ID> --name deployment_info
cat deployment_info.json

# Option 3: From AWS CLI
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=finops-ai-instance" \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

**Access URL:**
```
http://<PUBLIC_IP>:8501
```

---

## Post-Deployment Verification (5 minutes)

### Verify Deployment Success ✅

- [ ] GitHub Actions pipeline shows all green checkmarks
- [ ] No errors in pipeline logs
- [ ] Deployment info artifact available
- [ ] Application responds at URL
- [ ] Streamlit interface loads

### Verify Infrastructure ✅

```bash
# Check EC2 instance
aws ec2 describe-instances --instance-ids <INSTANCE_ID> \
  --query 'Reservations[0].Instances[0].[State.Name,PublicIpAddress,InstanceType]'

# Check ECR image
aws ecr describe-images --repository-name finops-ai \
  --query 'imageDetails[-1].[imageTags,imageSizeInBytes,imagePushedAt]'

# Check CloudWatch logs
aws logs tail /aws/ec2/finops-ai --follow --max-items 10
```

### Verify Application ✅

```bash
# Test application endpoint
curl -I http://<PUBLIC_IP>:8501

# Check container logs
ssh -i your-key.pem ubuntu@<PUBLIC_IP>
docker logs finops-container
```

---

## Troubleshooting Quick Guide 🆘

### Pipeline Fails

**Check logs:**
```bash
# Failed stage shows error details
# Common issues:
1. Invalid AWS credentials → Update GitHub Secrets
2. Insufficient IAM permissions → Add policies
3. Invalid Terraform syntax → Run terraform validate locally
4. Docker image not found → Verify docker_image_uri
```

### Application Not Accessible

**Diagnose:**
```bash
# Check if instance is running
aws ec2 describe-instance-status --instance-ids <INSTANCE_ID>

# SSH to instance and debug
ssh -i your-key.pem ubuntu@<PUBLIC_IP>
docker ps
docker logs finops-container
curl http://localhost:8501
```

### Cost Higher Than Expected

**Optimize:**
```bash
# Check running instances
aws ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]'

# Stop idle instances
aws ec2 stop-instances --instance-ids i-xxxxx

# Use smaller instance type in terraform.tfvars
instance_type = "t3.small"
```

---

## Important Credentials & URLs

### Save These After Deployment:

```
AWS Account ID:          ___________________________
AWS Region:              ___________________________
EC2 Instance ID:         ___________________________
EC2 Public IP:           ___________________________
Application URL:         ___________________________
ECR Repository URL:      ___________________________
S3 State Bucket:         ___________________________ (if using)
```

### AWS Credentials (GitHub Secrets):

```
AWS_ACCESS_KEY_ID:       [SAVED IN GITHUB]
AWS_SECRET_ACCESS_KEY:   [SAVED IN GITHUB]
```

⚠️ **NEVER share these credentials!**

---

## Common Tasks

### Re-deploy Application (without changing infrastructure)

```bash
# Update app code
# Commit and push to main
git push origin main

# Pipeline automatically triggers
# Monitor at GitHub Actions dashboard
```

### Update Application Configuration

```bash
# Edit terraform/terraform.tfvars
# Change instance_type, container_port, etc.
# Commit and push
git push origin main

# Pipeline re-creates infrastructure with new config
```

### SSH to EC2 Instance

```bash
# First, get instance details
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=finops-ai-instance" \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

# SSH to instance
ssh -i /path/to/your/key.pem ubuntu@<PUBLIC_IP>

# Create key if needed:
aws ec2 create-key-pair --key-name finops-key \
  --query 'KeyMaterial' --output text > finops-key.pem
chmod 400 finops-key.pem
```

### View Application Logs

```bash
# CloudWatch logs
aws logs tail /aws/ec2/finops-ai --follow

# SSH to instance and view container logs
ssh -i key.pem ubuntu@<PUBLIC_IP>
docker logs -f finops-container
```

### Destroy Infrastructure (when done)

```bash
cd terraform
terraform destroy -auto-approve

# Or via AWS console:
# 1. EC2 Dashboard > Instances > Select finops-ai-instance > Terminate
# 2. VPC Dashboard > VPCs > Delete finops-ai-vpc
```

---

## Estimated Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| AWS Setup | 5-10 min | ⏱️ One-time |
| Terraform Config | 2-3 min | ⏱️ One-time |
| First Deployment | 15-20 min | 🚀 Automated |
| Subsequent Deploys | 12-15 min | 🚀 Faster |

---

## Success Criteria ✅

- [ ] All GitHub Actions stages pass (green checkmarks)
- [ ] Application is accessible at http://<PUBLIC_IP>:8501
- [ ] Streamlit interface loads and is responsive
- [ ] CloudWatch shows application logs
- [ ] EC2 instance shows "running" status
- [ ] No errors in deployment logs

---

## Next Steps 🎯

1. **Set up monitoring**: Configure CloudWatch dashboards
2. **Enable alerts**: Get notified of failures
3. **Backup data**: Implement backup strategy
4. **Scale infrastructure**: Add load balancing
5. **Optimize costs**: Review and optimize resources

---

## Support Resources

- 📖 [Full Implementation Plan](./IMPLEMENTATION_PLAN.md)
- 📖 [AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)
- 📖 [CI/CD Operations](./CI_CD_OPERATIONS.md)
- 🔗 [GitHub Actions Docs](https://docs.github.com/en/actions)
- 🔗 [Terraform Docs](https://www.terraform.io/docs/)
- 🔗 [AWS Docs](https://docs.aws.amazon.com/)

---

**Ready to deploy? Start with Step 1! 🚀**
