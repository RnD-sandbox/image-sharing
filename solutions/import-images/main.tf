locals {
  pi_image_manager_script = "../../scripts/pi_image_manager.py"
  pi_image_operation_log  = "pi_image_manager_log.json"
  pi_image_status_log     = "pi_image_status_log.json"
}

resource "terraform_data" "pi_image_manager_exec" {
  provisioner "local-exec" {
    command = "bash ../../scripts/init.sh ${local.pi_image_manager_script}"
    environment = {
      IBMCLOUD_API_KEY               = var.ibmcloud_api_key
      IBMCLOUD_ENTERPRISE_ACCOUNT_ID = var.enterprise_id
      IBMCLOUD_ACCOUNT_GROUP_NAME    = var.account_group_name
      COS_IMAGE_FILE_NAME            = var.cos_image_file_name
      COS_REGION                     = var.cos_data.cos_region
      COS_BUCKET_NAME                = var.cos_data.cos_bucket_name
      COS_ACCESS_KEY                 = var.cos_data.access_key
      COS_SECRET_KEY                 = var.cos_data.secret_key
      COS_STORAGE_TYPE               = var.cos_data.storage_type
      POWERVS_IMAGE_OPERATION        = var.image_operation
      POWERVS_IMAGE_NAME             = var.image_name
    }
  }
}

locals {
  pi_image_operation_results = jsondecode(file(local.pi_image_operation_log))
  pi_image_status_results    = jsondecode(file(local.pi_image_status_log))
}

data "local_file" "python_code_exec_log" {
  filename = "app.log"
}





