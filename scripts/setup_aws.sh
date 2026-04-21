#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# AWS Deployment Script
# This script helps set up the CI/CD pipeline on AWS
# ─────────────────────────────────────────────────────────────────────────────

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${1:-us-east-1}"
APP_NAME="finops-ai"
IAM_USER="github-actions-finops"

echo -e "${BLUE}🚀 FinOps AI - AWS Deployment Setup${NC}"
echo -e "${BLUE}─────────────────────────────────────${NC}\n"

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}❌ AWS CLI is not installed${NC}"
        echo "Please install AWS CLI: https://aws.amazon.com/cli/"
        exit 1
    fi
    echo -e "${GREEN}✅ AWS CLI is installed${NC}"
}

# Function to check AWS credentials
check_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}❌ AWS credentials are not configured${NC}"
        echo "Run: aws configure"
        exit 1
    fi
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    echo -e "${GREEN}✅ AWS credentials are configured${NC}"
    echo "Account ID: $ACCOUNT_ID"
}

# Function to create IAM user for GitHub Actions
create_iam_user() {
    echo -e "\n${BLUE}Creating IAM User...${NC}"
    
    if aws iam get-user --user-name $IAM_USER &> /dev/null; then
        echo -e "${YELLOW}⚠️  IAM user '$IAM_USER' already exists${NC}"
    else
        aws iam create-user --user-name $IAM_USER
        echo -e "${GREEN}✅ IAM user created${NC}"
    fi
}

# Function to attach policies
attach_policies() {
    echo -e "\n${BLUE}Attaching policies...${NC}"
    
    # Create custom policy for minimal permissions
    POLICY_DOCUMENT='{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "ecr:GetAuthorizationToken",
            "ecr:BatchGetImage",
            "ecr:GetDownloadUrlForLayer",
            "ecr:PutImage",
            "ecr:InitiateLayerUpload",
            "ecr:UploadLayerPart",
            "ecr:CompleteLayerUpload"
          ],
          "Resource": "*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "ec2:*",
            "vpc:*",
            "elasticloadbalancing:*",
            "autoscaling:*"
          ],
          "Resource": "*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource": "arn:aws:logs:*:*:*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "iam:PassRole",
            "iam:GetRole"
          ],
          "Resource": "*"
        }
      ]
    }'
    
    # Save policy to file
    echo "$POLICY_DOCUMENT" > /tmp/github-actions-policy.json
    
    aws iam put-user-policy --user-name $IAM_USER \
      --policy-name GitHubActionsPolicy \
      --policy-document file:///tmp/github-actions-policy.json
    
    echo -e "${GREEN}✅ Policies attached${NC}"
}

# Function to create access keys
create_access_keys() {
    echo -e "\n${BLUE}Creating access keys...${NC}"
    
    # Check if user already has access keys
    EXISTING_KEYS=$(aws iam list-access-keys --user-name $IAM_USER --query 'AccessKeyMetadata[].AccessKeyId' --output text)
    
    if [ ! -z "$EXISTING_KEYS" ]; then
        echo -e "${YELLOW}⚠️  User already has access keys${NC}"
        echo "Existing keys: $EXISTING_KEYS"
        echo "Delete old keys? (y/n)"
        read -r DELETE_KEYS
        
        if [ "$DELETE_KEYS" = "y" ]; then
            for KEY_ID in $EXISTING_KEYS; do
                aws iam delete-access-key --user-name $IAM_USER --access-key-id $KEY_ID
                echo "Deleted key: $KEY_ID"
            done
        fi
    fi
    
    # Create new access key
    CREDENTIALS=$(aws iam create-access-key --user-name $IAM_USER)
    ACCESS_KEY=$(echo $CREDENTIALS | jq -r '.AccessKey.AccessKeyId')
    SECRET_KEY=$(echo $CREDENTIALS | jq -r '.AccessKey.SecretAccessKey')
    
    echo -e "${GREEN}✅ Access keys created${NC}"
    echo -e "\n${YELLOW}⚠️  Save these credentials securely:${NC}"
    echo "AWS_ACCESS_KEY_ID: $ACCESS_KEY"
    echo "AWS_SECRET_ACCESS_KEY: $SECRET_KEY"
    echo -e "\n${YELLOW}Add these to GitHub Secrets:${NC}"
    echo "Repository Settings > Secrets and variables > Actions"
}

# Function to create S3 bucket for Terraform state
create_state_bucket() {
    echo -e "\n${BLUE}Creating S3 bucket for Terraform state...${NC}"
    
    BUCKET_NAME="finops-terraform-state-$(date +%s)"
    
    aws s3 mb "s3://$BUCKET_NAME" --region $AWS_REGION
    
    # Enable versioning
    aws s3api put-bucket-versioning \
      --bucket "$BUCKET_NAME" \
      --versioning-configuration Status=Enabled
    
    # Enable encryption
    aws s3api put-bucket-encryption \
      --bucket "$BUCKET_NAME" \
      --server-side-encryption-configuration '{
        "Rules": [{
          "ApplyServerSideEncryptionByDefault": {
            "SSEAlgorithm": "AES256"
          }
        }]
      }'
    
    echo -e "${GREEN}✅ S3 bucket created: $BUCKET_NAME${NC}"
    echo "Update terraform/main.tf with this bucket name"
}

# Function to create DynamoDB table for Terraform locking
create_state_lock_table() {
    echo -e "\n${BLUE}Creating DynamoDB table for Terraform state locking...${NC}"
    
    if aws dynamodb describe-table --table-name terraform-locks --region $AWS_REGION &> /dev/null; then
        echo -e "${YELLOW}⚠️  Table 'terraform-locks' already exists${NC}"
    else
        aws dynamodb create-table \
          --table-name terraform-locks \
          --attribute-definitions AttributeName=LockID,AttributeType=S \
          --key-schema AttributeName=LockID,KeyType=HASH \
          --billing-mode PAY_PER_REQUEST \
          --region $AWS_REGION
        
        echo -e "${GREEN}✅ DynamoDB table created${NC}"
    fi
}

# Function to create ECR repository
create_ecr_repository() {
    echo -e "\n${BLUE}Creating ECR repository...${NC}"
    
    if aws ecr describe-repositories --repository-names $APP_NAME --region $AWS_REGION &> /dev/null; then
        echo -e "${YELLOW}⚠️  Repository '$APP_NAME' already exists${NC}"
    else
        aws ecr create-repository \
          --repository-name $APP_NAME \
          --region $AWS_REGION \
          --image-scanning-configuration scanOnPush=true
        
        echo -e "${GREEN}✅ ECR repository created${NC}"
    fi
}

# Function to display final instructions
display_instructions() {
    echo -e "\n${GREEN}✅ AWS Setup Complete!${NC}"
    echo -e "\n${BLUE}Next Steps:${NC}"
    echo "1. Add GitHub Secrets:"
    echo "   - AWS_ACCESS_KEY_ID: $ACCESS_KEY"
    echo "   - AWS_SECRET_ACCESS_KEY: $SECRET_KEY"
    echo ""
    echo "2. Update terraform/main.tf with S3 bucket backend (optional)"
    echo ""
    echo "3. Push code to GitHub main branch to trigger deployment"
    echo ""
    echo "4. Monitor pipeline at: https://github.com/YOUR_REPO/actions"
}

# ─────────────────────────────────────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${BLUE}Checking prerequisites...${NC}"
check_aws_cli
check_aws_credentials

echo -e "\n${BLUE}Setting up AWS resources...${NC}"
create_iam_user
attach_policies
create_access_keys
create_state_bucket
create_state_lock_table
create_ecr_repository

display_instructions

echo -e "\n${GREEN}🎉 Setup complete! Happy deploying!${NC}\n"
