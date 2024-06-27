from src.ibmcloud_cos import *
from src.ibmcloud_utils import *
from src.log_utils import *
from src.constants import CONFIG

pi_logger = logging.getLogger("logger")

## get env vars
ibmcloud_api_key = os.getenv("IBMCLOUD_API_KEY")
access_key = os.getenv("COS_ACCESS_KEY")
secret_key = os.getenv("COS_SECRET_KEY")

if __name__ == "__main__":
    """
    Main function to coordinate the script execution.
    """

    enterprise_id = CONFIG.get("enterprise_id")
    # Authenticate and get the bearer token
    access_token = get_enterprise_bearer_token(ibmcloud_api_key)

    # Fetch the list of account groups
    account_groups = get_account_group_list(enterprise_id, access_token)
    
    # Fetch the list of trusted profiles
    trusted_profiles = get_trusted_profiles(access_token)

    # Find the relevant account group ID
    if CONFIG.get("account_group_id"):
#        account_group_id = get_relevant_account_group_id(
#            account_groups, CONFIG.get("target_value")[0]
#        )
        
        # Fetch the list accounts in the respective account group
        relevant_accounts = get_account_list(enterprise_id, CONFIG.get("account_group_id"), access_token)
        
        # Create a dictionary of relevant accounts for quick lookup
        relevant_accounts_dict = {
            account["id"]: account["name"] for account in relevant_accounts
        }
        
        # Filter the trusted profiles to include account ID, profile ID, and account name
        filtered_trusted_profiles = filter_trusted_profiles(
            trusted_profiles, relevant_accounts_dict
        )
        
    elif CONFIG.get("account_list"):
        relevant_accounts = create_account_identity_map(enterprise_id, access_token, CONFIG.get("account_list"))
        print(relevant_accounts)
        #relevant_accounts = CONFIG.get("account_list")
         # Filter the trusted profiles to include account ID, profile ID, and account name
        filtered_trusted_profiles = filter_trusted_profiles(
            trusted_profiles, relevant_accounts
        )
        
    if filtered_trusted_profiles:
        image_operation = CONFIG.get("image_operation")
        log_operation_file_name = CONFIG.get("log_operation_file_name")
        log_image_status_file_name = CONFIG.get("log_image_status_file_name")
        pi_logger.info(
            f"Initiating provided PowerVS boot image {image_operation} operation."
        )
        if image_operation == "IMPORT":
            # Check if cos credentials and image exists in bucket
            object_exists_in_ibm_cos(
                access_key,
                secret_key,
                CONFIG.get("cos_bucket_details")["cos_region"],
                CONFIG.get("cos_bucket_details")["cos_bucket"],
                CONFIG.get("cos_bucket_details")["cos_image_file_name"],
            )

            deploy_image_to_child_accounts(
                filtered_trusted_profiles, access_token, log_operation_file_name
            )
            fetch_status(1800, filtered_trusted_profiles, access_token, log_operation_file_name)

        elif image_operation == "DELETE":
            delete_image_from_child_accounts(
                filtered_trusted_profiles, access_token, log_operation_file_name
            )
            fetch_status(300, filtered_trusted_profiles, access_token, log_operation_file_name)

        elif image_operation == "STATUS":
            get_image_import_status_from_accounts(
                filtered_trusted_profiles, access_token, log_image_status_file_name
            )
        else:
            pi_logger.error(
                f"Unidentified action '{image_operation}' passed. Supported operations are IMPORT and DELETE."
            )
    else:
        pi_logger.error(
            f"Could not find relevant trusted profiles."
        )