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
  name = "finance-app"
  build {
    context = "../"
  }
}

resource "docker_container" "finance_container" {
  name  = "finance-container"
  image = docker_image.finance_app.image_id

  ports {
    internal = 3000
    external = 3000
  }
}