#import logging
import multiprocessing
import json
from src.ibmcloud_iam import *
from src.ibmcloud_powervs import *
from src.log_utils import *
from src.custom_logger import ImageShareLogger, ImageStatusLogger, merge_status_logs, log_account_level_status, merge_image_op_logs, log_account_level_image_op

pi_logger = logging.getLogger('my_logger')

def get_enterprise_bearer_token(api_key):
    """
    Generate a bearer token using the provided API key.
    Args:
        api_key: IBM Cloud API key.
    Returns:
        access_token: Bearer token if authentication is successful, otherwise None.
    """
    pi_logger.info("Enterprise account authentication:")
    response, error = generate_bearer_token(api_key)
    if response:
        return response.json()['access_token']
    else:
        pi_logger.error(f"Error while authenticating using IBM Cloud enterprise account API key: {error}")
        return None

def get_relevant_account_group_id(account_groups, target_name):
    """
    Find the relevant account group ID based on the target name.
    Args:
        account_groups: List of account groups.
        target_name: Name of the target account group.
    Returns:
        relevant_account_group_id: ID of the relevant account group, or None if not found.
    """
    for account_group in account_groups:
        if account_group['name'] == target_name:
            return account_group['id']
    pi_logger.error(f"No account group found with the name: {target_name}")
    return None

def fetch_relevant_accounts(enterprise_id, account_group_id, access_token):
    """
    Fetch the list of accounts under the specified account group.
    Args:
        enterprise_id: ID of the enterprise.
        account_group_id: ID of the account group.
        access_token: Bearer token for authentication.
    Returns:
        relevant_accounts: List of relevant accounts, or None if fetching fails.
    """
    response, error = get_account_list(enterprise_id, account_group_id, access_token)
    if response:
        return response.json()['resources']
    else:
        pi_logger.error(f"Failed to get the accounts under the account group id {account_group_id}: {error}")
        return None

def fetch_trusted_profiles(access_token):
    """
    Fetch the list of trusted profiles.
    Args:
        access_token: Bearer token for authentication.
    Returns:
        trusted_profiles: List of trusted profiles, or None if fetching fails.
    """
    response, error = get_trusted_profiles(access_token)
    if response:
        return response.json()['profiles']
    else:
        pi_logger.error(f"Failed to get trusted profiles: {error}")
        return None

def filter_trusted_profiles(trusted_profiles, relevant_accounts_dict):
    """
    Filter trusted profiles to include account ID, profile ID, and account name.
    Args:
        trusted_profiles: List of trusted profiles.
        relevant_accounts_dict: Dictionary mapping account IDs to account names of all accounts in an Account Group.
    Returns:
        filtered_profiles: List of filtered trusted profiles.
    """
    return [
        {
            "account_id": profile["account_id"],
            "profile_id": profile["id"],
            "name": relevant_accounts_dict.get(profile["account_id"], "Unknown")
        }
        for profile in trusted_profiles if profile["account_id"] in relevant_accounts_dict
    ]

def deploy_image_to_child_accounts(account_list, enterprise_access_token):
    """
    Deploys image to child accounts using multiprocessing.

    :param account_list: List of account dictionaries containing account details.
    :param enterprise_access_token: Enterprise account access token.
    """
    if account_list:
        args = [(account, enterprise_access_token) for account in account_list]
        with multiprocessing.Pool(processes=5) as pool:
            results = pool.starmap(deploy_image_to_account, args)
            final_log = merge_image_op_logs(results)
            write_logs_to_file(final_log, 'pi_image_manager_log.json')
            #print(final_log.get_log())
            #print(json.dumps(final_log, indent=2))

def deploy_image_to_account(account, enterprise_access_token):
    """
    Deploys image to a single child account.

    :param account: Dictionary containing account details.
    :param enterprise_access_token: Enterprise account access token.
    """
    account_logger = ImageShareLogger()
    access_token_response, _error = get_child_account_access_token(account['profile_id'], account['account_id'], enterprise_access_token)
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = import_images_to_workspaces(account, bearer_token)
        return log_account_level_image_op(account_logger, workspace_logger, account) 
    else:
        account_logger.log_other(account, None, f"Failed to retrieve access token for account - {account['name']}")

def import_images_to_workspaces(account, bearer_token):
    """
    Imports image to all workspaces under an account.

    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    logger = ImageShareLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
            power_workspaces = powervs_workspaces_response.json()['workspaces']
            for workspace in power_workspaces:
                import_images_to_workspace(workspace, account, bearer_token, logger)
    else:
        logger.log_other(account, workspace, f"Failed to fetch the Power Virtual Server workspaces for {account['name']}. {_error}")
        #pi_logger.error(f"Failed to fetch the Power Virtual Server workspaces for {account['name']}")
    return logger

def import_images_to_workspace(workspace, account, bearer_token, logger):
    """
    Imports image to a single workspace.

    :param workspace: Dictionary containing workspace details.
    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        image_found, is_active = process_image('my-image-catalog-name', boot_images_response.json()['images']) # TODO remove hard coded value
        if image_found and is_active:
            logger.log_skipped(workspace)
            #print(f"The boot image to be imported already in the workspace {workspace['name']} under account {account['name']}. Aborting the operation")
        else:
            response, _error = import_boot_image(workspace, bearer_token)
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)

def delete_image_from_child_accounts(account_list, enterprise_access_token):
    """
    Deletes image from child accounts using multiprocessing.

    :param account_list: List of account dictionaries containing account details.
    :param enterprise_access_token: Enterprise access token.
    """
    if account_list:
        args = [(account, enterprise_access_token) for account in account_list]
        with multiprocessing.Pool(processes=5) as pool:
            results = pool.starmap(delete_image_from_account, args)
            final_log = merge_image_op_logs(results)
            write_logs_to_file(final_log, 'pi_image_manager_log.json')
            #print(json.dumps(final_log, indent=2))

def delete_image_from_account(account, enterprise_access_token):
    """
    Deletes image from a single child account.

    :param account: Dictionary containing account details.
    :param enterprise_access_token: Enterprise access token.
    """
    account_logger = ImageShareLogger()
    access_token_response, _error = get_child_account_access_token(account['profile_id'], account['account_id'], enterprise_access_token)
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = delete_image_from_workpsaces(account, bearer_token)
        return log_account_level_image_op(account_logger, workspace_logger, account)      
    else:
        account_logger.log_other(account, None, f"Failed to retrieve access token for account - {account['name']}")

def delete_image_from_workpsaces(account, bearer_token):
    """
    Deletes image from all workspaces under an account.

    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    logger = ImageShareLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()['workspaces']
        for workspace in power_workspaces:
            delete_image_from_workpsace(workspace, account, bearer_token, logger)
    else:
        logger.log_other(account, workspace, f"Failed to fetch the Power Virtual Server workspaces for {account['name']}. {_error}")
    return logger
        
def delete_image_from_workpsace(workspace, account, bearer_token, logger):
    """
    Deletes image from a single workspace.

    :param workspace: Dictionary containing workspace details.
    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        image_found, is_active = process_image('my-image-catalog-name', boot_images_response.json()['images']) # TODO remove hard coded value
        if image_found and is_active:
            response, _error = delete_boot_image(image_found['imageID'], workspace, bearer_token)
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)
        else:
            logger.log_skipped(workspace)
            
def get_image_import_status_from_accounts(account_list, enterprise_access_token):
    if account_list:
        args = [(account, enterprise_access_token) for account in account_list]
        with multiprocessing.Pool(processes=5) as pool:
            results = pool.starmap(status_check_from_account, args)
            final_log = merge_status_logs(results)
            write_logs_to_file(final_log, 'pi_image_status_log.json')
            #print(json.dumps(final_log, indent=2))
            
def status_check_from_account(account, enterprise_access_token):
    """
    Deletes image from a single child account.

    :param account: Dictionary containing account details.
    :param enterprise_access_token: Enterprise access token.
    """
    account_logger = ImageStatusLogger()
    access_token_response, _error = get_child_account_access_token(account['profile_id'], account['account_id'], enterprise_access_token)
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = status_check_from_workpsaces(account, bearer_token)
        return log_account_level_status(account_logger, workspace_logger, account)
    else:
        pi_logger.error(f"Failed to retrieve access token for account - {account['name']}")
        
def status_check_from_workpsaces(account, bearer_token):
    """
    Deletes image from all workspaces under an account.

    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    logger = ImageStatusLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()['workspaces']
        for workspace in power_workspaces:
            status_check_from_workpsace(workspace, account, bearer_token, logger)
    else:
        logger.other.append({
                "id": workspace['id'],
                "name":  workspace['name'],
                "error": _error
            })
    return logger
        
def status_check_from_workpsace(workspace, account, bearer_token, logger):
    """
    Checks if image active in a single workspace.

    :param workspace: Dictionary containing workspace details.
    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        image_found, is_active = process_image(os.getenv('POWERVS_IMAGE_NAME'), boot_images_response.json()['images'])
        if image_found and is_active:
            logger.active.append({
                "id": workspace['id'],
                "name":  workspace['name']
            })
        else:
            logger.inactive.append({
                "id": workspace['id'],
                "name":  workspace['name']
            }) 

def process_image(boot_image_name, boot_images):
    """
    Filter the concerned image from the list of boot images and checks if it's status is active.

    :param boot_image_name: Name of the boot image to be imported or deleted.
    :param boot_images: List of boot images.
    :return: The concerned image dictionary or None.
    """
    concerned_image = list(filter(lambda image: image.get('name', '')==boot_image_name, boot_images))
    if concerned_image:
        if concerned_image[0]['state'] == 'active':
            return concerned_image[0], True
        else:
            return concerned_image[0], False
    else:
        return None, False

def write_logs_to_file(logger, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(logger, f, ensure_ascii=False, indent=4)
