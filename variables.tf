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
  description = "ID of the parent account group. Keep the string empty to use the account list."
  type        = string
  default     = ""
}

variable "account_list" {
  description = "List of account IDs to target. Keep the list empty to target child accounts using account group id."
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

variable "image_details" {
  description = "The name under which the boot image is visible in the PowerVS workspace. When 'image_operation' is IMPORT Additional details like the license_type, product, and vendor details for images are required. If not can be left empty. License type supported values: 'byol'; product supported values: 'Hana', 'Netweaver'; vendor allowable value: 'SAP'."
  type = object({
    image_name   = string
    license_type = optional(string)
    product      = optional(string)
    vendor       = optional(string)
  })
  default = {
    image_name   = ""
    license_type = ""
    product      = ""
    vendor       = ""
  }
}

variable "cos_image_file_name" {
  description = "Name of the file in IBM Cloud Object Storage. Required only when 'image_operation' is set to IMPORT."
  type        = string
  default     = ""
}

variable "cos_data" {
  description = "IBM Cloud Object Storage bucket name, region and file access credentials. Keep the default value if selected operation is 'Delete image'."
  type = object({
    cos_region      = string
    cos_bucket_name = string
    access_key      = string
    secret_key      = string
  })
  default = {
    "cos_region" : "",
    "cos_bucket_name" : "",
    "access_key" : "",
    "secret_key" : ""
  }
  sensitive = true
}

variable "processes" {
  description = "Number of parallel processes to operate on accounts"
  type        = number
  default     = 10
}
