variable "ibmcloud_api_key" {
    description = "Name of IBM Cloud PowerVS workspace which will be created."
    type        = string
}

variable "enterprise_id" {
  description = "The ID of the enterprise account"
  type = string
}

variable "account_group_name" {
  description = "The account group with all target child accounts under the enterprise account."
  type = string
}

variable "cos_data" {
    description = "The COS credentials to download the image file."
    type = object({
      cos_region = string
      cos_bucket_name = string
      image_file_name = string
      access_key = string
      secret_key = string
      storage_type = string
    })
}

variable "image_action" {
  type = string
  validation {
    condition = var.image_action == "IMPORT" || var.image_action == "DELETE"
    error_message = "Supported values are IMPORT and DELETE"
  }
}

variable "image_name" {
  description = "The name under which the boot image is visible on PowerVS workspace."
  type = string
}
