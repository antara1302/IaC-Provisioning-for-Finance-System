# Docker resources are handled by GitHub Actions CI/CD pipeline
# No local Docker provider needed for AWS infrastructure 
#hello
terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "finance_app" {
  name = "finance-ai"

  build {
    context = "../app"
  }
}

resource "docker_container" "finance_container" {
  name  = "finance-container"
  image = docker_image.finance_app.image_id

  ports {
    internal = 8501
    external = 8501
  }
}