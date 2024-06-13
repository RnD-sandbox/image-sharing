locals {
  image_import_script = "../../scripts/import_images.py"
  image_delete_script = "../../scripts/delete_images.py"
}

resource "terraform_data" "example2" {
  provisioner "local-exec" {
    command = "bash ../../scripts/init.sh"
    environment = {
      ACCESS_KEY = var.cos_data.access_key
      SECRET_KEY = var.cos_data.secret_key
      API_KEY = var.ibmcloud_api_key
    }
  }
}


