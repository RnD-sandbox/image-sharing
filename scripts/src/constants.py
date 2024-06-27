import yaml
import os.path

CONFIG = {}
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Open and read the YAML file
with open(parent_dir + "/config.yaml") as file:
    CONFIG = yaml.safe_load(file)

# enterprise_id = data["enterprise_id"]
# account_group_name = data["account_group_name"]
# image_operation = data["image_operation"]
# cos_access_key = data["cos_bucket_details"]["cos_access_key"]
# cos_secret_key = data["cos_bucket_details"]["cos_secret_key"]
# cos_region = data["cos_bucket_details"]["cos_region"]
# cos_bucket = data["cos_bucket_details"]["cos_bucket"]
# cos_image_file_name = data["cos_bucket_details"]["cos_image_file_name"]
# log_operation_file_name = data["log_operation_file_name"]
# log_image_status_file_name = data["log_image_status_file_name"]
