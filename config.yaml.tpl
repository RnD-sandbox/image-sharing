# The enterprise account id
enterprise_id: "${enterprise_id}"

# IMPORTANT
# You can target the accounts with either account_group_id or account_list
# To share across account group with a list of accounts, provide account_group_id
# To share a specific list of accounts, provide account ids as a list in account_list
# Do not provide both account_group_id & account_list

# ID of the parent account group.
account_group_id: "${account_group_id}"

# List of account IDs to target.
account_list:
%{ for value in account_list ~}
  - "${value}"
%{ endfor ~}

# The import or delete operation to be performed for the custom PowerVS boot image. Accepted values are: IMPORT & DELETE.
image_operation: "${image_operation}"

# The name under which the boot image is visible in the PowerVS workspace, along with the license_type, product, and vendor details for SAP images. License type supported values: 'byol'; product supported values: 'Hana', 'Netweaver'; vendor allowable value: 'SAP'.
image_details:
  image_name: "${image_name}"
  license_type: "${license_type}"
  product: "${product}"
  vendor: "${vendor}"

# Cloud Object Storage bucket name, region and file name.
cos_bucket_details:
  cos_region: "${cos_region}"
  cos_bucket: "${cos_bucket}"
  cos_image_file_name: "${cos_image_file_name}"

# File names for logs
log_operation_file_name: "${log_operation_file_name}"
