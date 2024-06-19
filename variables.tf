variable "ibmcloud_api_key" {
  description = "IBM Cloud enterprise API key created within Service ID"
  type        = string
  sensitive   = true
}

variable "enterprise_id" {
  description = "The ID of the enterprise account"
  type        = string
}

variable "account_group_name" {
  description = "Name of the parent account group."
  type        = string
}

variable "cos_image_file_name" {
  description = "The name of the image file to be downloaded from COS bucket."
  type        = string
  default     = ""
}

variable "cos_data" {
  description = "The COS credentials to download the image file."
  type = object({
    cos_region      = string
    cos_bucket_name = string
    access_key      = string
    secret_key      = string
    storage_type    = string
  })
  default   = null
  sensitive = true
}

variable "image_operation" {
  description = "Select the import or delete operation to be performed for the PowerVS boot image."
  type        = string
  validation {
    condition     = var.image_operation == "IMPORT" || var.image_operation == "DELETE" || var.image_operation == "STATUS"
    error_message = "Supported values are IMPORT and DELETE"
  }
}

variable "image_name" {
  description = "The name under which the boot image is visible on PowerVS workspace."
  type        = string
}
