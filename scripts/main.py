from src.ibmcloud_cos import *
from src.ibmcloud_utils import *
from src.log_utils import *
from src.constants import CONFIG, validate_config

pi_logger = logging.getLogger("logger")

## get env vars
ibmcloud_api_key = os.getenv("IBMCLOUD_API_KEY")
access_key = os.getenv("COS_ACCESS_KEY")
secret_key = os.getenv("COS_SECRET_KEY")

if __name__ == "__main__":
    """
    Main function to coordinate the script execution.
    """
    # Validate config.yaml
    validate_config()
    enterprise_id = CONFIG.get("enterprise_id")
    # Authenticate and get the bearer token
    enterprise_access_token = get_enterprise_bearer_token(ibmcloud_api_key)

    # Fetch the list of trusted profiles
    trusted_profiles = get_trusted_profiles(enterprise_access_token)

    # Find the relevant account group ID
    if CONFIG.get("account_group_id"):
        # Fetch the list accounts in the respective account group
        relevant_accounts = get_account_list(enterprise_id, CONFIG.get("account_group_id"), enterprise_access_token)
        # Create a dictionary of relevant accounts for quick lookup
        relevant_accounts_dict = {account["id"]: account["name"] for account in relevant_accounts}
        # Filter the trusted profiles to include account ID, profile ID, and account name
        filtered_trusted_profiles = filter_trusted_profiles(trusted_profiles, relevant_accounts_dict)

    elif CONFIG.get("account_list"):
        # Map all the account ids in account_list to their respective account name
        relevant_accounts = create_account_identity_map(enterprise_access_token, CONFIG.get("account_list"))
        print(relevant_accounts)
        # Filter the trusted profiles to include account ID, profile ID, and account name
        filtered_trusted_profiles = filter_trusted_profiles(trusted_profiles, relevant_accounts)

    if filtered_trusted_profiles:
        image_operation = CONFIG.get("image_operation")
        log_operation_file_name = CONFIG.get("log_operation_file_name")
        log_image_status_file_name = CONFIG.get("log_image_status_file_name")
        pi_logger.info(f"Initiating provided PowerVS boot image {image_operation} operation.")
        if image_operation == "IMPORT":
            # Check if cos credentials and image exists in bucket
            object_exists_in_ibm_cos(
                access_key,
                secret_key,
                CONFIG.get("cos_bucket_details")["cos_region"],
                CONFIG.get("cos_bucket_details")["cos_bucket"],
                CONFIG.get("cos_bucket_details")["cos_image_file_name"],
            )
            # Import the image
            result = deploy_image_to_child_accounts(filtered_trusted_profiles, enterprise_access_token, log_operation_file_name)

            fetch_status(result, 600)
            if result is not None and result["failed"]:
                pi_logger.error(f"Import image failed for following accounts '{result['failed']}'.")
                sys.exit(1)

        elif image_operation == "DELETE":
            # Delete the image
            result = delete_image_from_child_accounts(filtered_trusted_profiles, enterprise_access_token, log_operation_file_name)
            fetch_status(result, 180)
            if result is not None and result["failed"]:
                pi_logger.error(f"Delete image failed for following accounts '{result['failed']}'.")
                sys.exit(1)

        elif image_operation == "STATUS":
            get_image_import_status_from_accounts(
                filtered_trusted_profiles,
                enterprise_access_token,
                log_image_status_file_name,
            )
        else:
            pi_logger.error(f"Unidentified action '{image_operation}' passed. Supported operations are IMPORT and DELETE.")
            sys.exit(1)
    else:
        pi_logger.error(f"Could not find relevant trusted profiles.")
        sys.exit(1)
