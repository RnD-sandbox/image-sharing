variable "ibmcloud_api_key" {
  description = "IBM Cloud enterprise API key created for Service ID."
  type        = string
  sensitive   = true
}

variable "enterprise_id" {
  description = "The ID of the enterprise account."
  type        = string
}

variable "account_group_id" {
  description = "ID of the parent account group. leave empty to use account list."
  type        = string
  default     = ""
}

variable "account_list" {
  description = "List of account IDs to target; leave empty to use account groups."
  type        = list(string)
  default     = []
}

variable "image_operation" {
  description = "Select the import or delete operation to be performed for the custom PowerVS boot image."
  type        = string
  validation {
    condition     = var.image_operation == "IMPORT" || var.image_operation == "DELETE" || var.image_operation == "STATUS"
    error_message = "Supported values are IMPORT and DELETE"
  }
}

variable "image_import_details" {
  description = "The name under which the boot image is visible in the PowerVS workspace, along with the license_type, product, and vendor details for SAP images. License type supported values: 'byol'; product supported values: 'Hana', 'Netweaver'; vendor allowable value: 'SAP'."
  type = object({
    image_name   = string
    license_type = optional(string)
    product      = optional(string)
    vendor       = optional(string)
  })
}

variable "cos_image_file_name" {
  description = "Cloud Object Storage image filename."
  type        = string
  default     = null
}

variable "cos_data" {
  description = "Cloud Object Storage bucket name, region and file access credentials. Leave the default value for 'Delete image' operation."
  type = object({
    cos_region      = string
    cos_bucket_name = string
    access_key      = string
    secret_key      = string
  })
  default   = null
  sensitive = true
}


