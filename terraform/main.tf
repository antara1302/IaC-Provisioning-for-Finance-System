provider "docker" {}

resource "docker_image" "finance_app" {
  name = "finance-ai"

  build {
    context = "../app" # ✅ correct folder
  }
}

resource "docker_container" "finance_container" {
  name  = "finance-container"
  image = docker_image.finance_app.image_id

  ports {
    internal = 8501 # ✅ Streamlit port
    external = 8501
  }
}