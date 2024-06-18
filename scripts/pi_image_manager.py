import logging
import argparse
from src.ibmcloud_utils import *
import time

def parse_arguments():
    """
    Parse command-line arguments.
    Returns:
        args: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--api_key', help='IBM Cloud API key for authentication')
    parser.add_argument('-e', '--enterprise_id', help='Enterprise ID for the IBM Cloud account')
    parser.add_argument('-i', '--image', help='Image file name')
    parser.add_argument('-o', '--operation', help='Action to be performed. IMPORT or DELETE')
    parser.add_argument('-c', '--cos_credentials', help='COS credentials to download the image file from COS bucket')
    parser.add_argument('-g', '--account_group_name', help='Name of the account group to list the concerned child accounts')
    return parser.parse_args()

def fetch_status(sleep_duration, filtered_trusted_profiles, access_token):
    logging.info(f"Initiating sleep for {sleep_duration} seconds before status check.")
    time.sleep(sleep_duration)
    get_image_import_status_from_accounts(filtered_trusted_profiles, access_token)
    
def main():
    """
    Main function to coordinate the script execution.
    """
    args = parse_arguments()
    
    # Authenticate and get the bearer token
    ibmcloud_api_key = os.getenv('IBMCLOUD_API_KEY')
    access_token = get_enterprise_bearer_token(ibmcloud_api_key)
    if not access_token:
        return

    # Fetch the list of account groups
    enterprise_id = os.getenv('IBMCLOUD_ENTERPRISE_ACCOUNT_ID')
    account_group_list_response, error = get_account_group_list(enterprise_id, access_token)
    if not account_group_list_response:
        logging.error(f"Failed to get the enterprise account group list: {error}")
        return

    account_group_list = account_group_list_response.json()['resources']

    # Find the relevant account group ID
    account_group_name = os.getenv('IBMCLOUD_ACCOUNT_GROUP_NAME')
    account_group_id = get_relevant_account_group_id(account_group_list, account_group_name)
    if not account_group_id:
        return

    print(f"Relevant group id: {account_group_id}")

    # Fetch the list of relevant accounts
    relevant_accounts = fetch_relevant_accounts(args.enterprise_id, account_group_id, access_token)
    if not relevant_accounts:
        return

    # Create a dictionary of relevant accounts for quick lookup
    relevant_accounts_dict = {account['id']: account['name'] for account in relevant_accounts}

    # Fetch the list of trusted profiles
    trusted_profiles = fetch_trusted_profiles(access_token)
    if not trusted_profiles:
        return

    # Filter the trusted profiles to include account ID, profile ID, and account name
    filtered_trusted_profiles = filter_trusted_profiles(trusted_profiles, relevant_accounts_dict)
    image_operation = os.getenv('POWERVS_IMAGE_OPERATION')
    if image_operation == 'IMPORT':
        logging.info(f"Initiating provided PowerVS boot image {image_operation} operation.")
        deploy_image_to_child_accounts(filtered_trusted_profiles, access_token)
        fetch_status(1800, filtered_trusted_profiles, access_token)
    elif image_operation == 'DELETE':
        logging.info(f"Initiating provided PowerVS boot image {image_operation} operation.")
        delete_image_from_child_accounts(filtered_trusted_profiles, access_token)
        fetch_status(300, filtered_trusted_profiles, access_token)
    elif image_operation == 'STATUS':
        logging.info(f"Initiating provided PowerVS boot image {image_operation} operation.")
        get_image_import_status_from_accounts(filtered_trusted_profiles, access_token)
    else:
        logging.error(f"Unindentified action '{image_operation}' passed. Supported operations are IMPORT and DELETE.")

if __name__ == "__main__":
    main()
