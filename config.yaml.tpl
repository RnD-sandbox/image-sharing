# The enterprise account id
enterprise_id: "${enterprise_id}"

# IMPORTANT
# You can target the accounts with either account_group_id or account_list
# To share across account group with a list of accounts, provide account_group_id
# To share a specific list of accounts, provide account ids as a list in account_list
# Do not provide both account_group_id & account_list

account_group_id: "${account_group_id}"

# The list of account pr
account_list:
%{ for value in account_list ~}
  - "${value}"
%{ endfor ~}

image_operation: "${image_operation}"

image_import_details:
  image_name: "${image_name}"
  license_type: "${license_type}"
  product: "${product}"
  vendor: "${vendor}"

cos_bucket_details:
  cos_region: "${cos_region}"
  cos_bucket: "${cos_bucket}"
  cos_image_file_name: "${cos_image_file_name}"

log_operation_file_name: "${log_operation_file_name}"

log_image_status_file_name: "${log_image_status_file_name}"
