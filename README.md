# Summary

Image sharing solution across PowerVS workspaces across single parent account group from an enterprise account.

### Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3 |
| <a name="requirement_ibm"></a> [ibm](#requirement\_ibm) | =1.66.0 |
| <a name="requirement_time"></a> [time](#requirement\_time) | >= 0.9.1 |

### Modules

No modules.

### Resources

| Name | Type |
|------|------|
| [local_file.config_yaml](https://registry.terraform.io/providers/hashicorp/local/latest/docs/resources/file) | resource |
| [terraform_data.display_logs](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.pi_image_manager_exec](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.trigger_vars](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_group_id"></a> [account\_group\_id](#input\_account\_group\_id) | ID of the parent account group. Keep the string empty to use the account list. | `string` | `""` | no |
| <a name="input_account_list"></a> [account\_list](#input\_account\_list) | List of account IDs to target. Keep the list empty to target child accounts using account group id. | `list(string)` | `[]` | no |
| <a name="input_cos_data"></a> [cos\_data](#input\_cos\_data) | IBM Cloud Object Storage bucket name, region and file access credentials. Keep the default value if selected operation is 'Delete image'. | <pre>object({<br>    cos_region      = string<br>    cos_bucket_name = string<br>    access_key      = string<br>    secret_key      = string<br>  })</pre> | <pre>{<br>  "access_key": "",<br>  "cos_bucket_name": "",<br>  "cos_region": "",<br>  "secret_key": ""<br>}</pre> | no |
| <a name="input_cos_image_file_name"></a> [cos\_image\_file\_name](#input\_cos\_image\_file\_name) | Name of the file in IBM Cloud Object Storage. Required only when 'image\_operation' is set to IMPORT. | `string` | `""` | no |
| <a name="input_enterprise_id"></a> [enterprise\_id](#input\_enterprise\_id) | The ID of the enterprise account. | `string` | n/a | yes |
| <a name="input_ibmcloud_api_key"></a> [ibmcloud\_api\_key](#input\_ibmcloud\_api\_key) | IBM Cloud enterprise API key created for Service ID. | `string` | n/a | yes |
| <a name="input_image_details"></a> [image\_details](#input\_image\_details) | The name under which the boot image is visible in the PowerVS workspace. When 'image\_operation' is IMPORT Additional details like the license\_type, product, and vendor details for images are required. If not can be left empty. License type supported values: 'byol'; product supported values: 'Hana', 'Netweaver'; vendor allowable value: 'SAP'. | <pre>object({<br>    image_name   = string<br>    license_type = optional(string)<br>    product      = optional(string)<br>    vendor       = optional(string)<br>  })</pre> | <pre>{<br>  "image_name": "",<br>  "license_type": "",<br>  "product": "",<br>  "vendor": ""<br>}</pre> | no |
| <a name="input_image_operation"></a> [image\_operation](#input\_image\_operation) | Select the import or delete operation to be performed for the custom PowerVS boot image. | `string` | n/a | yes |

### Outputs

No outputs.
