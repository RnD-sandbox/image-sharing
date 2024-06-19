locals {
  log_operation_file_name    = "pi_image_manager_log.json"
  log_image_status_file_name = "pi_image_status_log.json"
}

resource "terraform_data" "trigger_vars" {
  input = {
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
    LOG_OPERATION_FILE_NAME        = local.log_operation_file_name
    LOG_IMAGE_STATUS_FILE_NAME     = local.log_image_status_file_name
  }

}


resource "terraform_data" "pi_image_manager_exec" {

  triggers_replace = terraform_data.trigger_vars
  provisioner "local-exec" {

    # pi_image_manager.py requires inputs as env vars:
    # IBMCLOUD_API_KEY, IBMCLOUD_ENTERPRISE_ACCOUNT_ID, IBMCLOUD_ACCOUNT_GROUP_NAME, COS_IMAGE_FILE_NAME, COS_REGION, COS_BUCKET_NAME, COS_ACCESS_KEY, COS_SECRET_KEY, COS_STORAGE_TYPE, POWERVS_IMAGE_OPERATION, POWERVS_IMAGE_NAME, LOG_OPERATION_FILE_NAME, LOG_IMAGE_STATUS_FILE_NAME

    command = <<-EOT
      pip3 install requests
      pip3 install hmac
      pip3 install hashlib
      python3 ./scripts/pi_image_manager.py
    EOT

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
      LOG_OPERATION_FILE_NAME        = local.log_operation_file_name
      LOG_IMAGE_STATUS_FILE_NAME     = local.log_image_status_file_name
    }
  }
}

data "local_file" "console_log_file" {
  depends_on = [resource.terraform_data.pi_image_manager_exec]
  filename   = "console.log"
}

/*
data "local_file" "pi_image_operation_log_file" {
  depends_on = [resource.terraform_data.pi_image_manager_exec]
  filename   = local.log_operation_file_name
}

data "local_file" "pi_image_status_log_file" {
  depends_on = [resource.terraform_data.pi_image_manager_exec]
  filename   = local.log_image_status_file_name
}


locals {
  pi_image_operation_results = jsondecode(data.local_file.pi_image_operation_log_file.content)
  pi_image_status_results    = jsondecode(data.local_file.pi_image_status_log_file.content)
}

*/




