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


def get_enterprise_bearer_token(api_key):
    """
    Generate a bearer token using the provided API key.
    Args:
        api_key: IBM Cloud API key.
    Returns:
        access_token: Bearer token if authentication is successful, otherwise None.
    """

    pi_logger.info("Start: Generating bearer token for enterprise account using IBMCLOUD API Key...")
    response, error = generate_bearer_token(api_key)
    if response:
        pi_logger.info("End: Generated bearer token for enterprise account using IBMCLOUD API Key.")
        return response.json()["access_token"]
    else:
        pi_logger.error(f"Error generating bearer token for enterprise account. Invalid IBMCLOUD API Key for enterprise account: {error}")
        sys.exit(1)


def create_account_identity_map(access_token, account_list):
    """
    Creates an (id, name) map using the data from account groups for the accounts mentioned in account_list
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


def image_ops_on_child_accounts(action, account_list, enterprise_access_token, log_file):
    """
    Deploys/Deletes images to /from child accounts using multiprocessing.
    Args:
        action: delete, import. Tells what operation to perform.
        account_list: List of account dictionaries containing account details.
        enterprise_access_token: Enterprise account access token.
        log_file: Filename to store logs.
    """
    operation = {
        "delete": {"err_message": "Delete image failed for following accounts", "sleep": 180},
        "import": {"err_message": "Import image failed for following accounts", "sleep": 600},
    }

    if account_list:
        args = [(action, account, enterprise_access_token) for account in account_list]
        with multiprocessing.Pool(processes=5) as pool:
            results = pool.starmap(image_ops_on_child_account, args)

        final_log = merge_image_op_logs(results)
        write_logs_to_file(final_log, log_file)
        fetch_status(final_log, operation[action]["sleep"])
        if final_log is not None and final_log["failed"]:
            pi_logger.error(f"{operation[action]['err_message']} '{final_log['failed']}'.")
            sys.exit(1)


def image_ops_on_child_account(action, account, enterprise_access_token):
    """
    Deletes/Imports image from/to a single child account.

    Args:
        action: delete, import. Tells what operation to perform.
        account: Dictionary containing account details.
        enterprise_access_token: Enterprise account access token.
    Returns:
        account_logger
    """
    account_logger = ImageShareLogger()
    access_token_response, _error = get_child_account_access_token(account["profile_id"], account["account_id"], enterprise_access_token)
    if access_token_response:
        bearer_token = f"Bearer {access_token_response.json()['access_token']}"
        workspace_logger = image_ops_on_workspaces(action, account, bearer_token)
        return log_account_level_image_op(account_logger, workspace_logger, account)
    else:
        account_logger.log_other(account, f"Failed to retrieve access token for account - {account['id']}")
        return account_logger


def image_ops_on_workspaces(action, account, bearer_token):
    """
    Deletes/Imports image to all workspaces under an account.

    Args:
        action: delete, import. Tells what operation to perform.
        account: Dictionary containing account details.
        bearer_token: Bearer token for the account.
    Returns:
        logger
    """
    operation = {
        "delete": {"function": delete_image_from_workspace},
        "import": {"function": import_image_to_workspace},
    }
    logger = ImageShareLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()["workspaces"]
        for workspace in power_workspaces:
            operation[action]["function"](workspace, bearer_token, logger)
    else:
        logger.log_other(account, f"Failed to fetch the Power Virtual Server workspaces for {account}, {_error}")
    return logger


def import_image_to_workspace(workspace, bearer_token, logger):
    """
    Imports image to a single workspace.

    Args:
        workspace: Dictionary containing workspace details.
        bearer_token: Bearer token for the account.
        logger
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        # check if the image already exists
        image_found, is_active = process_image(CONFIG.get("image_details")["image_name"], boot_images_response.json()["images"])

        # check if there is already an image import job running
        latest_job_status, _error = get_cos_image_import_status(
            {
                "name": workspace["name"],
                "id": workspace["id"],
                "crn": workspace["details"]["crn"],
                "base_url": workspace["location"]["url"],
            },
            bearer_token,
        )

        if image_found and is_active:
            logger.log_skipped(workspace, "Image with the same name exists in this workspace.")
        elif (latest_job_status and latest_job_status.json()["status"]["state"]) == "running":
            logger.log_skipped(workspace, "Another import job already running.")
        else:
            # Import boot image
            response, _error = import_boot_image(workspace, bearer_token)
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)


def delete_image_from_workspace(workspace, bearer_token, logger):
    """
    Deletes image from a single workspace.

    Args:
        workspace: Dictionary containing workspace details.
        bearer_token: Bearer token for the account.
    """
    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if boot_images_response:
        # check if the image exists
        image_found, is_active = process_image(CONFIG.get("image_details")["image_name"], boot_images_response.json()["images"])
        if image_found and is_active:
            # Delete boot image
            response, _error = delete_boot_image(image_found["imageID"], workspace, bearer_token)
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)
        else:
            logger.log_skipped(workspace, "The image does not exist.")


def process_image(boot_image_name, boot_images):
    """
    Filter the concerned image from the list of boot images and checks if it's status is active.

    :param boot_image_name: Name of the boot image to be imported or deleted.
    :param boot_images: List of boot images.
    :return: The concerned image dictionary or None.
    """
    concerned_image = list(filter(lambda image: image.get("name", "") == boot_image_name, boot_images))
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
        pi_logger.info(f"Initiating sleep for {sleep_duration} seconds before status check.")
        time.sleep(sleep_duration)
        pi_logger.info(f"Initiating status checks ...")
        count = 0
        while count < 7:
            status_list = []
            for account in log_obj["success"]:
                for workspace in account["workspaces"]:
                    response, _err = get_cos_image_import_status(workspace, enterprise_access_token)
                    if response:
                        if response.json()["status"]["state"] != "completed":
                            status_list.append(workspace)
            if not status_list:
                pi_logger.info(f"INFO: Status check completed.")
                pi_logger.info(f"INFO: Complete log file written to {CONFIG.get('log_operation_file_name')}")
                break
            count = +1
            pi_logger.info(f"INFO: Initiating sleep for 5 mins. ({count}/6 times)")
            time.sleep(300)
    else:
        pi_logger.info(f"INFO: No active requests found.")
        pi_logger.info(f"INFO: Complete log file written to {CONFIG.get('log_operation_file_name')}")


def write_logs_to_file(logger, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(logger, f, ensure_ascii=False, indent=4)
