locals {
  log_operation_file_name    = "pi_image_manager_log.json"
  log_image_status_file_name = "pi_image_status_log.json"
}

provider "local" {}

resource "local_file" "config_yaml" {
  content = templatefile("${path.module}/config.yaml.tpl", {
    enterprise_id              = var.enterprise_id
    account_group_id           = var.account_group_id
    account_list               = var.account_list
    image_operation            = var.image_operation
    image_name                 = var.image_import_details.image_name
    license_type               = var.image_import_details.license_type
    product                    = var.image_import_details.product
    vendor                     = var.image_import_details.vendor
    cos_region                 = var.cos_data != null ? var.cos_data.cos_region : ""
    cos_bucket                 = var.cos_data != null ? var.cos_data.cos_bucket_name : ""
    cos_image_file_name        = var.cos_image_file_name
    log_operation_file_name    = local.log_operation_file_name
    log_image_status_file_name = local.log_image_status_file_name
  })

  filename = "${path.module}/scripts/config.yaml"
}


resource "terraform_data" "trigger_vars" {
  depends_on = [resource.local_file.config_yaml]
  input = {
    IBMCLOUD_API_KEY           = var.ibmcloud_api_key
    COS_ACCESS_KEY             = var.cos_data != null ? var.cos_data.access_key : ""
    COS_SECRET_KEY             = var.cos_data != null ? var.cos_data.secret_key : ""
    enterprise_id              = var.enterprise_id
    account_group_id           = var.account_group_id
    account_list               = var.account_list
    image_operation            = var.image_operation
    image_name                 = var.image_import_details.image_name
    license_type               = var.image_import_details.license_type
    product                    = var.image_import_details.product
    vendor                     = var.image_import_details.vendor
    cos_region                 = var.cos_data != null ? var.cos_data.cos_region : ""
    cos_bucket                 = var.cos_data != null ? var.cos_data.cos_bucket_name : ""
    cos_image_file_name        = var.cos_image_file_name
    log_operation_file_name    = local.log_operation_file_name
    log_image_status_file_name = local.log_image_status_file_name
  }
}

resource "terraform_data" "pi_image_manager_exec" {

  triggers_replace = terraform_data.trigger_vars
  provisioner "local-exec" {

    # main.py requires inputs as env vars:
    # IBMCLOUD_API_KEY, IBMCLOUD_ENTERPRISE_ACCOUNT_ID, IBMCLOUD_ACCOUNT_GROUP_NAME, COS_IMAGE_FILE_NAME, COS_REGION, COS_BUCKET_NAME, COS_ACCESS_KEY, COS_SECRET_KEY, COS_STORAGE_TYPE, POWERVS_IMAGE_OPERATION, POWERVS_IMAGE_NAME, LOG_OPERATION_FILE_NAME, LOG_IMAGE_STATUS_FILE_NAME

    command = <<-EOT
      pip3 install requests
      pip3 install boto3
      pip3 install pyyaml
      python3 ./scripts/main.py
    EOT

    environment = {
      IBMCLOUD_API_KEY = var.ibmcloud_api_key
      COS_ACCESS_KEY   = var.cos_data != null ? var.cos_data.access_key : ""
      COS_SECRET_KEY   = var.cos_data != null ? var.cos_data.secret_key : ""
    }
  }
}

data "local_file" "console_log_file" {
  depends_on = [resource.terraform_data.pi_image_manager_exec]
  filename   = "console.log"
}

data "local_file" "pi_image_operation_log_file" {
  depends_on = [resource.terraform_data.pi_image_manager_exec]
  filename   = local.log_operation_file_name
}

data "local_file" "pi_image_status_log_file" {
  count      = fileexists("${path.module}/${local.log_image_status_file_name}") ? 1 : 0
  depends_on = [resource.terraform_data.pi_image_manager_exec]
  filename   = local.log_image_status_file_name
}

locals {
  pi_image_operation_results = jsondecode(data.local_file.pi_image_operation_log_file.content)
  pi_image_status_results    = fileexists("${path.module}/${local.log_image_status_file_name}") ? jsondecode(data.local_file.pi_image_status_log_file[0].content) : {}
}

