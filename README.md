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
| [terraform_data.pi_image_manager_exec](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [terraform_data.trigger_vars](https://registry.terraform.io/providers/hashicorp/terraform/latest/docs/resources/data) | resource |
| [local_file.console_log_file](https://registry.terraform.io/providers/hashicorp/local/latest/docs/data-sources/file) | data source |

### Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_account_group_name"></a> [account\_group\_name](#input\_account\_group\_name) | Name of the parent account group. | `string` | n/a | yes |
| <a name="input_cos_data"></a> [cos\_data](#input\_cos\_data) | The COS credentials to download the image file. | <pre>object({<br>    cos_region      = string<br>    cos_bucket_name = string<br>    access_key      = string<br>    secret_key      = string<br>    storage_type    = string<br>  })</pre> | `null` | no |
| <a name="input_cos_image_file_name"></a> [cos\_image\_file\_name](#input\_cos\_image\_file\_name) | The name of the image file to be downloaded from COS bucket. | `string` | `null` | no |
| <a name="input_enterprise_id"></a> [enterprise\_id](#input\_enterprise\_id) | The ID of the enterprise account | `string` | n/a | yes |
| <a name="input_ibmcloud_api_key"></a> [ibmcloud\_api\_key](#input\_ibmcloud\_api\_key) | IBM Cloud enterprise API key created within Service ID | `string` | n/a | yes |
| <a name="input_image_name"></a> [image\_name](#input\_image\_name) | The name under which the boot image is visible on PowerVS workspace. | `string` | n/a | yes |
| <a name="input_image_operation"></a> [image\_operation](#input\_image\_operation) | Select the import or delete operation to be performed for the PowerVS boot image. | `string` | n/a | yes |

### Outputs

| Name | Description |
|------|-------------|
| <a name="output_console_log"></a> [console\_log](#output\_console\_log) | The console logs from python script execution. |