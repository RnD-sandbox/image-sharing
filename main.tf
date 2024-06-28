locals {
  log_operation_file_name    = "pi_image_manager_log.json"
  log_image_status_file_name = "pi_image_status_log.json"

  is_cos_data_valid                = (var.image_operation == "IMPORT" && var.cos_data != null) || var.image_operation == "DELETE" ? true : false
  cos_data_validate_msg            = "The cos_data is null. The import operation of custom images requires cos_data."
  cos_data_chk                     = regex("^${local.cos_data_validate_msg}$", (local.is_cos_data_valid ? local.cos_data_validate_msg : ""))
  is_cos_image_file_name_valid     = (var.image_operation == "IMPORT" && var.cos_image_file_name != null && var.cos_image_file_name != "") || var.image_operation == "DELETE" ? true : false
  cos_image_file_name_validate_msg = "The cos_image_file_name is null or empty. The import operation of custom images requires cos_image_file_name."
  cos_image_file_name_chk          = regex("^${local.cos_image_file_name_validate_msg}$", (local.is_cos_image_file_name_valid ? local.cos_image_file_name_validate_msg : ""))
}

provider "local" {}

resource "local_file" "config_yaml" {
  content = templatefile("${path.module}/config.yaml.tpl", {
    enterprise_id              = var.enterprise_id
    account_group_id           = var.account_group_id
    account_list               = var.account_list
    image_operation            = var.image_operation
    image_name                 = var.image_import_details.image_name
    license_type               = var.image_import_details.license_type != null ? var.image_import_details.license_type : ""
    product                    = var.image_import_details.product != null ? var.image_import_details.product : ""
    vendor                     = var.image_import_details.vendor != null ? var.image_import_details.vendor : ""
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
    license_type               = var.image_import_details.license_type != null ? var.image_import_details.license_type : ""
    product                    = var.image_import_details.product != null ? var.image_import_details.product : ""
    vendor                     = var.image_import_details.vendor != null ? var.image_import_details.vendor : ""
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
      pip3 install jsonschema
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

