import time

from src.ibmcloud_cos2 import *
from src.ibmcloud_utils import *
from src.log_utils import *

pi_logger = logging.getLogger("my_logger")

## get env vars
ibmcloud_api_key = os.getenv("IBMCLOUD_API_KEY")
enterprise_id = os.getenv("IBMCLOUD_ENTERPRISE_ACCOUNT_ID")
account_group_name = os.getenv("IBMCLOUD_ACCOUNT_GROUP_NAME")
image_operation = os.getenv("POWERVS_IMAGE_OPERATION")
log_operation_file_name = os.getenv("LOG_OPERATION_FILE_NAME")
log_image_status_file_name = os.getenv("LOG_IMAGE_STATUS_FILE_NAME")
access_key = os.getenv("COS_ACCESS_KEY")
secret_key = os.getenv("COS_SECRET_KEY")
region = os.getenv("COS_REGION")
bucket = os.getenv("COS_BUCKET_NAME")
object_key = os.getenv("COS_IMAGE_FILE_NAME")


def fetch_status(sleep_duration, filtered_trusted_profiles, access_token):
    pi_logger.info(
        f"Initiating sleep for {sleep_duration} seconds before status check."
    )
    time.sleep(sleep_duration)
    get_image_import_status_from_accounts(
        filtered_trusted_profiles, access_token, log_image_status_file_name
    )


def main():
    """
    Main function to coordinate the script execution.
    """

    # Authenticate and get the bearer token
    access_token = get_enterprise_bearer_token(ibmcloud_api_key)

    # Fetch the list of account groups
    account_groups = get_account_group_list(enterprise_id, access_token)

    # Find the relevant account group ID
    account_group_id = get_relevant_account_group_id(account_groups, account_group_name)

    # Fetch the list of relevant accounts
    relevant_accounts = get_account_list(enterprise_id, account_group_id, access_token)

    # Create a dictionary of relevant accounts for quick lookup
    relevant_accounts_dict = {
        account["id"]: account["name"] for account in relevant_accounts
    }

    # Fetch the list of trusted profiles
    trusted_profiles = get_trusted_profiles(access_token)

    # Filter the trusted profiles to include account ID, profile ID, and account name
    filtered_trusted_profiles = filter_trusted_profiles(
        trusted_profiles, relevant_accounts_dict
    )

    pi_logger.info(
        f"Initiating provided PowerVS boot image {image_operation} operation."
    )
    if image_operation == "IMPORT":
        # Check if cos credentials and image exists in bucket
        object_exists_in_ibm_cos(access_key, secret_key, region, bucket, object_key)


"""
        deploy_image_to_child_accounts(
            filtered_trusted_profiles, access_token, log_operation_file_name
        )
        fetch_status(1800, filtered_trusted_profiles, access_token)

    elif image_operation == "DELETE":
        delete_image_from_child_accounts(
            filtered_trusted_profiles, access_token, log_operation_file_name
        )
        fetch_status(300, filtered_trusted_profiles, access_token)

    elif image_operation == "STATUS":
        get_image_import_status_from_accounts(
            filtered_trusted_profiles, access_token, log_image_status_file_name
        )
    else:
        pi_logger.error(
            f"Unidentified action '{image_operation}' passed. Supported operations are IMPORT and DELETE."
        )
"""

if __name__ == "__main__":
    main()
