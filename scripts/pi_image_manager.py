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
    parser.add_argument('-a', '--api_key', required=True, help='IBM Cloud API key for authentication')
    parser.add_argument('-e', '--enterprise_id', required=True, help='Enterprise ID for the IBM Cloud account')
    parser.add_argument('-i', '--image', help='Image file name')
    parser.add_argument('-o', '--operation', help='Action to be performed. IMPORT or DELETE')
    parser.add_argument('-c', '--cos_credentials', help='COS credentials to download the image file from COS bucket')
    parser.add_argument('-g', '--account_group_name', required=True, help='Name of the account group to list the concerned child accounts')
    return parser.parse_args()

def main():
    """
    Main function to coordinate the script execution.
    """
    args = parse_arguments()
    
    # Authenticate and get the bearer token
    access_token = get_enterprise_bearer_token(args.api_key)
    if not access_token:
        return

    # Fetch the list of account groups
    account_group_list_response, error = get_account_group_list(args.enterprise_id, access_token)
    if not account_group_list_response:
        logging.error(f"Failed to get the enterprise account group list: {error}")
        return

    account_group_list = account_group_list_response.json()['resources']

    # Find the relevant account group ID
    account_group_id = get_relevant_account_group_id(account_group_list, args.account_group_name)
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

    if args.operation == 'IMPORT':
        logging.info(f"Initiating provided PowerVS boot image {args.operation} operation.")
        deploy_image_to_child_accounts(filtered_trusted_profiles, access_token)
        time.sleep(1800)
        get_image_import_status_from_accounts(filtered_trusted_profiles, access_token)
    elif args.operation == 'DELETE':
        logging.info(f"Initiating provided PowerVS boot image {args.operation} operation.")
        delete_image_from_child_accounts(filtered_trusted_profiles, access_token)
    elif args.operation == 'STATUS':
        logging.info(f"Initiating provided PowerVS boot image {args.operation} operation.")
        get_image_import_status_from_accounts(filtered_trusted_profiles, access_token)
    else:
        logging.error(f"Unindentified action '{args.operation}' passed. Supported operations are IMPORT and DELETE.")
        
    #for profile in filtered_trusted_profiles:
    #    print(profile)

if __name__ == "__main__":
    main()
