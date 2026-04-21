#!/bin/bash
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Add ubuntu user to docker group
usermod -aG docker ubuntu

# Install CloudWatch Logs agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

# Create logs directory
mkdir -p /var/log/finops

# Log startup
echo "FinOps AI application starting..." >> /var/log/finops/startup.log

# Login to ECR
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${aws_region}.amazonaws.com

# Pull and run the Docker image
docker pull ${docker_image_uri}
docker run -d \
  --name ${app_name} \
  -p ${container_port}:${container_port} \
  --restart always \
  --log-driver awslogs \
  --log-opt awslogs-group=/aws/ec2/${app_name} \
  --log-opt awslogs-region=${aws_region} \
  --log-opt awslogs-stream=ecs-agent \
  ${docker_image_uri}

# Log successful startup
echo "FinOps AI application started successfully at $(date)" >> /var/log/finops/startup.log
