import json
import multiprocessing
import os
import sys
import time

from src.custom_logger import (
    ImageShareLogger,
    ImageStatusLogger,
    log_account_level_image_op,
    log_account_level_status,
    merge_image_op_logs,
    merge_status_logs,
)
from src.ibmcloud_iam import *
from src.ibmcloud_powervs import *
from src.log_utils import *
from src.constants import CONFIG

pi_logger = logging.getLogger("logger")
account_workspaces_map = {}


def get_enterprise_bearer_token(api_key):
    """
    Generate a bearer token using the provided API key.
    Args:
        api_key: IBM Cloud API key.
    Returns:
        access_token: Bearer token if authentication is successful, otherwise None.
    """

    pi_logger.info(
        "Start: Generating bearer token for enterprise account using IBMCLOUD API Key..."
    )
    response, error = generate_bearer_token(api_key)
    if response:
        pi_logger.info(
            "End: Generated bearer token for enterprise account using IBMCLOUD API Key."
        )
        return response.json()["access_token"]
    else:
        pi_logger.error(
            f"Error generating bearer token for enterprise account. Invalid IBMCLOUD API Key for enterprise account: {error}"
        )
        sys.exit(1)


def get_relevant_account_group_id(account_groups, target_name):
    """
    Find the relevant account group ID based on the target name.
    Args:
        account_groups: List of account groups.
        target_name: Name of the target account group.
    Returns:
        relevant_account_group_id: ID of the relevant account group, or None if not found.
    """

    pi_logger.info(
        f"Start: Fetching Account Group ID for {os.getenv('IBMCLOUD_ACCOUNT_GROUP_NAME')} in Enterprise account..."
    )
    for account_group in account_groups:
        if account_group["name"] == target_name:
            pi_logger.info(
                f"End: Fetched Account group ID {account_group['id']} for Account group name {os.getenv('IBMCLOUD_ACCOUNT_GROUP_NAME')} in Enterprise account."
            )
            return account_group["id"]

    pi_logger.error(
        f"Error Account group name {os.getenv('IBMCLOUD_ACCOUNT_GROUP_NAME')} doesn't exist in the provided Enterprise account : {target_name}"
    )
    sys.exit(1)


def create_account_identity_map(access_token, account_list):
    """
    Creates an (id, name) map using the data from account groups  for the accounts mentioned in account_list
    Args:
        enterprise_id: Enterprise id
        access_token: Access token created using the service id api key of the enterprise account
        account_list: The list of account from config.yaml
    Returns:
        account_identity_map: Map of account id and their names.
    """
    relevant_account_info = {}
    for account_id in account_list:
        response = get_account_details(account_id, access_token)
        relevant_account_info[account_id] = response["name"]

    return relevant_account_info


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
            "name": relevant_accounts_dict.get(profile["account_id"], "Unknown"),
        }
        for profile in trusted_profiles
        if profile["account_id"] in relevant_accounts_dict
    ]


def deploy_image_to_child_accounts(account_list, enterprise_access_token, log_file):
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
            write_logs_to_file(final_log, log_file)
    return final_log


def deploy_image_to_account(account, enterprise_access_token):
    """
    Deploys image to a single child account.

    :param account: Dictionary containing account details.
    :param enterprise_access_token: Enterprise account access token.
    """
    account_logger = ImageShareLogger()
    access_token_response, _error = get_child_account_access_token(
        account["profile_id"], account["account_id"], enterprise_access_token
    )
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = import_image_to_workspaces(account, bearer_token)
        return log_account_level_image_op(account_logger, workspace_logger, account)
    else:
        account_logger.log_other(
            account,
            f"Failed to retrieve access token for account - {account['id']}",
        )


def import_image_to_workspaces(account, bearer_token):
    """
    Imports image to all workspaces under an account.

    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    logger = ImageShareLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()["workspaces"]
        account_workspaces_map[account["id"]] = power_workspaces
        for workspace in power_workspaces:
            import_image_to_workspace(workspace, bearer_token, logger)
    else:
        logger.log_other(
            account,
            f"Failed to fetch the Power Virtual Server workspaces for {account}, {_error}",
        )
    return logger


def import_image_to_workspace(workspace, bearer_token, logger):
    """
    Imports image to a single workspace.

    :param workspace: Dictionary containing workspace details.
    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        image_found, is_active = process_image(
            CONFIG.get("image_details")["image_name"],
            boot_images_response.json()["images"],
        )
        active_job = get_image_status({ "name": workspace["name"],
                "id": workspace["id"],
                "crn": workspace["details"]["crn"],
                "base_url": workspace["location"]["url"]}, bearer_token)
            
        if (image_found and is_active):
            logger.c(workspace, "Image with the same name exists in this workspace.")
        elif active_job.json()["status"]["state"] == "running":
            logger.log_skipped(workspace, "Another import job already running.")
        else:
            response, _error = import_boot_image(workspace, bearer_token)
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)


def delete_image_from_child_accounts(account_list, enterprise_access_token, log_operation_file_name):
    """
    Deletes image from child accounts using multiprocessing.

    :param account_list: List of account dictionaries containing account details.
    :param enterprise_access_token: Enterprise access token.
    """

    args = [(account, enterprise_access_token) for account in account_list]
    with multiprocessing.Pool(processes=5) as pool:
        results = pool.starmap(delete_image_from_account, args)
        final_log = merge_image_op_logs(results)
        write_logs_to_file(final_log, log_operation_file_name)
    return final_log


def delete_image_from_account(account, enterprise_access_token):
    """
    Deletes image from a single child account.

    :param account: Dictionary containing account details.
    :param enterprise_access_token: Enterprise access token.
    """
    account_logger = ImageShareLogger()
    access_token_response, _error = get_child_account_access_token(
        account["profile_id"], account["account_id"], enterprise_access_token
    )
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = delete_image_from_workspaces(account, bearer_token)
        return log_account_level_image_op(account_logger, workspace_logger, account)
    else:
        account_logger.log_other(account, f"Failed to retrieve access token for account - {account['name']}")


def delete_image_from_workspaces(account, bearer_token):
    """
    Deletes image from all workspaces under an account.

    :param account: Dictionary containing account details.
    :param bearer_token: Bearer token for the account.
    """
    logger = ImageShareLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()["workspaces"]
        for workspace in power_workspaces:
            delete_image_from_workspace(workspace, bearer_token, logger)
    else:
        logger.log_other(
            account,
            f"Failed to fetch the Power Virtual Server workspaces for {account['name']}. {_error}",
        )
    return logger


def delete_image_from_workspace(workspace, bearer_token, logger):
    """
    Deletes image from a single workspace.

    :param workspace: Dictionary containing workspace details.
    :param bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        image_found, is_active = process_image(
            CONFIG.get("image_details")["image_name"],
            boot_images_response.json()["images"],
        )
        if image_found and is_active:
            response, _error = delete_boot_image(
                image_found["imageID"], workspace, bearer_token
            )
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)
        else:
            logger.log_skipped(workspace, "The image does not exist.")


def get_image_import_status_from_accounts(
    account_list, enterprise_access_token, log_file
):
    if account_list:
        args = [(account, enterprise_access_token) for account in account_list]
        with multiprocessing.Pool(processes=5) as pool:
            results = pool.starmap(status_check_from_account, args)
            final_log = merge_status_logs(results)
            write_logs_to_file(final_log, log_file)


def status_check_from_account(account, enterprise_access_token):
    """
    Check status of image from a single child account.
    :param account: Dictionary containing account details.
    :param enterprise_access_token: Enterprise access token.
    """
    account_logger = ImageStatusLogger()
    access_token_response, _error = get_child_account_access_token(
        account["profile_id"], account["account_id"], enterprise_access_token
    )
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = status_check_from_workspaces(bearer_token)
        return log_account_level_status(account_logger, workspace_logger, account)
    else:
        pi_logger.error(
            f"Failed to retrieve access token for account - {account['name']}"
        )


def status_check_from_workspaces(bearer_token):
    """
    Check status of image from all workspaces under an account.
    :param account: Dictionary containing account details.
    """
    logger = ImageStatusLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()["workspaces"]
        for workspace in power_workspaces:
            status_check_from_workspace(workspace, bearer_token, logger)
    else:
        logger.other.append(
            {"id": workspace["id"], "name": workspace["name"], "error": _error}
        )
    return logger


def status_check_from_workspace(workspace, bearer_token, logger):
    """
    Checks if image active in a single workspace.
    :param workspace: Dictionary containing workspace details.
    :param bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        image_found, is_active = process_image(
            CONFIG.get("image_details")["image_name"],
            boot_images_response.json()["images"],
        )
        if image_found and is_active:
            logger.active.append({"id": workspace["id"], "name": workspace["name"]})
        else:
            logger.inactive.append({"id": workspace["id"], "name": workspace["name"]})


def process_image(boot_image_name, boot_images):
    """
    Filter the concerned image from the list of boot images and checks if it's status is active.

    :param boot_image_name: Name of the boot image to be imported or deleted.
    :param boot_images: List of boot images.
    :return: The concerned image dictionary or None.
    """
    concerned_image = list(
        filter(lambda image: image.get("name", "") == boot_image_name, boot_images)
    )
    if concerned_image:
        if concerned_image[0]["state"] == "active":
            return concerned_image[0], True
        else:
            return concerned_image[0], False
    else:
        return None, False


def fetch_status(log_obj, sleep_duration):
    enterprise_access_token = get_enterprise_bearer_token(os.getenv("IBMCLOUD_API_KEY"))

    if log_obj and log_obj["success"]:
        pi_logger.info(
            f"Initiating sleep for {sleep_duration} seconds before status check."
        )
        time.sleep(sleep_duration)
        count = 0
        while count < 7:
            for account in log_obj["success"]:
                for workspace in account["workspaces"]:
                    status_list = []
                    response, _err = get_image_status(
                        workspace, enterprise_access_token
                    )
                    if response:
                        if response.json()["status"]["state"] != "completed":
                            status_list.append(workspace)
            if not status_list:
                break
            count = +1
            pi_logger.info(f"INFO: Initiating sleep for 5 mins. ({count}/6 times)")
            time.sleep(300)
    else:
        pi_logger.info(f"INFO: No active requests found.")


def write_logs_to_file(logger, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(logger, f, ensure_ascii=False, indent=4)
