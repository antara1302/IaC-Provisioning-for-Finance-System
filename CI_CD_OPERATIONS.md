# CI/CD Operations & Troubleshooting Reference

## 🎯 Quick Reference Commands

### AWS CLI Operations

```bash
# Check deployment status
aws ec2 describe-instances --instance-ids i-xxxxx --region us-east-1

# View application logs
aws logs tail /aws/ec2/finops-ai --follow --region us-east-1

# Get EC2 instance details
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=finops-ai-instance" \
  --region us-east-1

# List ECR images
aws ecr describe-images \
  --repository-name finops-ai \
  --region us-east-1

# SSH into EC2 instance
ssh -i your-key.pem ubuntu@<PUBLIC_IP>

# View Terraform state
aws s3 cp s3://finops-terraform-state-xxxxx/finops/terraform.tfstate ./

# Get instance metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --instance-id i-xxxxx \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

### Terraform Commands

```bash
cd terraform

# Initialize
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Plan deployment
terraform plan -var="docker_image_uri=ACCOUNT.dkr.ecr.REGION.amazonaws.com/finops-ai:TAGS"

# Apply changes
terraform apply -auto-approve

# Destroy infrastructure (CAUTION)
terraform destroy -auto-approve

# View outputs
terraform output

# View specific output
terraform output public_ip

# Refresh state
terraform refresh

# Show resources
terraform show
```

### Docker Operations (on EC2)

```bash
# SSH to instance first
ssh -i key.pem ubuntu@<PUBLIC_IP>

# View running containers
docker ps

# View container logs
docker logs -f finops-container

# Check container stats
docker stats finops-container

# Restart container
docker restart finops-container

# Stop container
docker stop finops-container

# Remove container
docker rm finops-container

# Pull new image manually
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

docker pull ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/finops-ai:latest
```

### GitHub Actions Operations

```bash
# View workflow runs
gh run list --workflow deploy.yml

# View specific run details
gh run view RUN_ID

# Download artifacts
gh run download RUN_ID --name deployment_info

# Cancel workflow run
gh run cancel RUN_ID

# View logs
gh run view RUN_ID --log
```

---

## 🔍 Troubleshooting Matrix

| Problem | Cause | Solution |
|---------|-------|----------|
| Pipeline fails at "Configure AWS Credentials" | Invalid AWS keys in GitHub Secrets | Regenerate keys via AWS IAM, update GitHub Secrets |
| "Permission denied" during Terraform apply | IAM user lacks required permissions | Add EC2, VPC, IAM policies to GitHub Actions user |
| ECR push fails | Invalid ECR repository or auth | Create ECR repo via `terraform apply` or AWS console |
| EC2 instance not starting | Insufficient AWS quota or permissions | Check account quotas, verify IAM permissions |
| Application not accessible | Container not running or port blocked | SSH to instance, check `docker ps`, verify Security Group |
| Health check times out | Application startup delay | Increase timeout in deploy.yml, check CloudWatch logs |
| Terraform state conflicts | Concurrent modifications | Enable S3 backend with DynamoDB locking |
| Image scanning fails | Vulnerabilities in base image | Update Python base image, rebuild |
| Cost higher than expected | Unused resources or wrong instance type | Review running instances, consider spot instances |

---

## 📝 Logs & Debugging

### CloudWatch Logs

```bash
# Tail logs in real-time
aws logs tail /aws/ec2/finops-ai --follow

# Get logs from last hour
aws logs filter-log-events \
  --log-group-name /aws/ec2/finops-ai \
  --start-time $(($(date +%s000) - 3600000))

# Search for errors
aws logs filter-log-events \
  --log-group-name /aws/ec2/finops-ai \
  --filter-pattern "ERROR"

# Export logs to S3
aws logs create-export-task \
  --log-group-name /aws/ec2/finops-ai \
  --from $(date -d '7 days ago' +%s)000 \
  --to $(date +%s)000 \
  --destination my-bucket \
  --destination-prefix logs
```

### GitHub Actions Logs

Access directly in GitHub UI:
- Go to Repository > Actions
- Click on the workflow run
- Expand each job to see detailed logs

Or via CLI:
```bash
gh run view <RUN_ID> --log > logs.txt
```

### EC2 Application Logs

```bash
# SSH to instance
ssh -i key.pem ubuntu@<PUBLIC_IP>

# Check Docker logs
docker logs finops-container
docker logs --tail 50 --follow finops-container

# Check system logs
sudo tail -f /var/log/syslog
sudo tail -f /var/log/finops/startup.log

# Check Docker daemon logs
sudo journalctl -u docker -f
```

---

## 🆘 Common Issues & Solutions

### Issue 1: "Docker: Image not found"
```bash
# Solution: Ensure image URI is correct
# Check ECR for available images
aws ecr describe-images --repository-name finops-ai

# Verify in terraform/terraform.tfvars that docker_image_uri is correct
```

### Issue 2: "Streamlit: Connection refused"
```bash
# SSH to instance
ssh -i key.pem ubuntu@<PUBLIC_IP>

# Check container is running
docker ps

# Check port binding
docker port finops-container

# If not running, check why
docker logs finops-container

# Restart
docker restart finops-container
```

### Issue 3: "Terraform: ResourceInUseException"
```bash
# Likely an instance or security group is in use
# Option 1: Wait a few minutes and retry
terraform apply -auto-approve

# Option 2: Remove and recreate (will lose data)
terraform destroy -auto-approve
terraform apply -auto-approve
```

### Issue 4: "GitHub: Insufficient permissions"
```bash
# Update IAM policy for the GitHub Actions user
# Add missing permissions, then regenerate access keys
aws iam list-user-policies --user-name github-actions-finops
aws iam get-user-policy --user-name github-actions-finops \
  --policy-name GitHubActionsPolicy
```

### Issue 5: "Health check: Request timeout"
```bash
# SSH to instance and check application
ssh -i key.pem ubuntu@<PUBLIC_IP>
docker logs -f finops-container

# If startup is slow, increase timeout in deploy.yml:
# Change "sleep 30" to "sleep 60"
# Increase retry interval from 15 to 30 seconds
```

---

## 📊 Performance Optimization

### Reduce Build Time
```yaml
# Enable layer caching in GitHub Actions
cache:
  - type: registry
    ref: ${{ steps.login-ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:buildcache
```

### Optimize Terraform
```hcl
# Parallelize resource creation
terraform apply -parallelism=10
```

### Reduce Container Size
```dockerfile
# In app/Dockerfile
FROM python:3.11-slim  # Instead of full image
RUN pip install --no-cache-dir -r requirements.txt  # Skip pip cache
```

---

## 🔒 Security Hardening

### Restrict SSH Access
```bash
# In terraform/aws.tf, change security group rule:
ingress {
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["YOUR_IP/32"]  # Replace with your IP
}
```

### Rotate AWS Keys Regularly
```bash
# Every 90 days:
aws iam create-access-key --user-name github-actions-finops
# Update GitHub Secrets with new key
aws iam delete-access-key --user-name github-actions-finops --access-key-id OLD_KEY_ID
```

### Enable VPC Flow Logs
```bash
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-xxxxx \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/vpc/flowlogs
```

---

## 💰 Cost Optimization

### Monitor Costs
```bash
# View cost by service
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity DAILY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Use Spot Instances (Production Ready)
```hcl
# In terraform/aws.tf
resource "aws_instance" "app" {
  instance_market_options {
    market_type = "spot"
  }
}
```

### Schedule Instances
```bash
# Stop instance during off-hours
aws ec2 stop-instances --instance-ids i-xxxxx

# Start instance when needed
aws ec2 start-instances --instance-ids i-xxxxx
```

---

## 🎯 Best Practices Checklist

- [ ] Use environment-specific configurations (dev, staging, prod)
- [ ] Implement automated backups of data volumes
- [ ] Enable CloudTrail for audit logging
- [ ] Use AWS Backup for disaster recovery
- [ ] Implement budget alerts in AWS Billing
- [ ] Regular security group audits
- [ ] Update base Docker image monthly
- [ ] Rotate AWS credentials quarterly
- [ ] Test disaster recovery procedures
- [ ] Monitor for unused resources weekly

---

## 📞 Support Resources

- **AWS Support**: https://console.aws.amazon.com/support
- **GitHub Actions Support**: https://support.github.com
- **Terraform Community**: https://discuss.hashicorp.com
- **Streamlit Community**: https://discuss.streamlit.io

---

**Last Updated**: 2024
**Status**: Reference Document
