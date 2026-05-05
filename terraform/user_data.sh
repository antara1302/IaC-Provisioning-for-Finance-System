#!/bin/bash
set -e

apt-get update -y
apt-get upgrade -y

apt-get install -y unzip curl docker.io

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

systemctl start docker
systemctl enable docker

usermod -aG docker ubuntu

wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb

mkdir -p /var/log/finops
echo "FinOps AI application starting..." >> /var/log/finops/startup.log

aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.${aws_region}.amazonaws.com

docker pull ${docker_image_uri}
docker run -d \
  --name ${app_name} \
  -p ${container_port}:${container_port} \
  -e GROQ_API_KEY="${groq_api_key}" \
  --restart always \
  ${docker_image_uri}

echo "FinOps AI application started successfully at $(date)" >> /var/log/finops/startup.log