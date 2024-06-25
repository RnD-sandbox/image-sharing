import argparse
from src.ibmcloud_utils import *
from src.log_utils import *

pi_logger = logging.getLogger("logger")


def main():

    # Authenticate and get the bearer token
    ibmcloud_api_key = os.getenv("IBMCLOUD_API_KEY")
    access_token = get_enterprise_bearer_token(ibmcloud_api_key)
    if not access_token:
        return

    # Fetch the list of account groups
    enterprise_id = os.getenv("IBMCLOUD_ENTERPRISE_ACCOUNT_ID")
    account_group_list_response, error = get_account_group_list(
        enterprise_id, access_token
    )
    if not account_group_list_response:
        pi_logger.error(f"Failed to get the enterprise account group list: {error}")
        return

    account_group_list = account_group_list_response.json()["resources"]

    # Find the relevant account group ID
    account_group_name = os.getenv("IBMCLOUD_ACCOUNT_GROUP_NAME")
    account_group_id = get_relevant_account_group_id(
        account_group_list, account_group_name
    )
    if not account_group_id:
        return

    print(f"Relevant group id: {account_group_id}")

    # Fetch the list of relevant accounts
    relevant_accounts = fetch_relevant_accounts(
        args.enterprise_id, account_group_id, access_token
    )
    if not relevant_accounts:
        pi_logger.error(
            f"The child account list for the provided account group is empty."
        )
        return

    # Create a dictionary of relevant accounts for quick lookup
    relevant_accounts_dict = {
        account["id"]: account["name"] for account in relevant_accounts
    }

    # Fetch the list of trusted profiles
    trusted_profiles = fetch_trusted_profiles(access_token)
    if not trusted_profiles:
        pi_logger.error(f"The trusted profiles list returned is empty.")
        return

    # Filter the trusted profiles to include account ID, profile ID, and account name
    filtered_trusted_profiles = filter_trusted_profiles(
        trusted_profiles, relevant_accounts_dict
    )
    image_operation = os.getenv("POWERVS_IMAGE_OPERATION")
    if image_operation == "IMPORT":
        pi_logger.info(
            f"Initiating provided PowerVS boot image {image_operation} operation."
        )
        deploy_image_to_child_accounts(filtered_trusted_profiles, access_token)
        fetch_status(1800, filtered_trusted_profiles, access_token)
    elif image_operation == "DELETE":
        pi_logger.info(
            f"Initiating provided PowerVS boot image {image_operation} operation."
        )
        delete_image_from_child_accounts(filtered_trusted_profiles, access_token)
        fetch_status(300, filtered_trusted_profiles, access_token)
    elif image_operation == "STATUS":
        pi_logger.info(
            f"Initiating provided PowerVS boot image {image_operation} operation."
        )
        get_image_import_status_from_accounts(filtered_trusted_profiles, access_token)
    else:
        pi_logger.error(
            f"Unindentified action '{image_operation}' passed. Supported operations are IMPORT and DELETE."
        )


if __name__ == "__main__":
    main()
