import json
import multiprocessing
import sys
import time

from src.custom_logger import (
    ImageShareLogger,
    log_account_level_image_op,
    merge_image_op_logs,
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


def image_ops_on_child_accounts(action, account_list, enterprise_access_token, ops_log_file, ops_status_log_file):
    """
    Deploys/Deletes images to /from child accounts using multiprocessing.
    Args:
        action: delete, import. Tells what operation to perform.
        account_list: List of account dictionaries containing account details.
        enterprise_access_token: Enterprise account access token.
        ops_log_file: Filename to store logs.
    """
    operation = {
        "delete": {"err_message": "ERROR: Delete image failed for following accounts", "sleep": 180},
        "import": {"err_message": "ERROR: Import image failed for following accounts", "sleep": 600},
    }

    if account_list:
        args = [(action, account, enterprise_access_token) for account in account_list]
        with multiprocessing.Pool(processes=CONFIG.get("processes")) as pool:
            results = pool.starmap(image_ops_on_child_account, args)

        image_ops_log = merge_image_op_logs(results)
        write_logs_to_file(image_ops_log, ops_log_file)

        if image_ops_log and image_ops_log["success"]:
            pi_logger.info(f"Initiating sleep for {operation[action]['sleep']} seconds before status check.")
            time.sleep(operation[action]["sleep"])
            pi_logger.info(f"Initiating status checks ...")
            count = 0
            while count < 7:
                with multiprocessing.Pool(processes=CONFIG.get("processes")) as pool:
                    status_results = pool.starmap(
                        image_ops_on_child_account, [("status", account, enterprise_access_token) for account in account_list]
                    )
                    image_ops_status_log = merge_image_op_logs(status_results)
                if not image_ops_status_log["failed"]:
                    pi_logger.info(f"INFO: Status Check Completed.")
                    pi_logger.info(f"INFO: Log file written to {CONFIG.get('log_operation_file_name')}.")
                    break
                count += 1
                pi_logger.info(f"INFO: Initiating sleep for 5 mins. Retrying {count} of 6 times....")
                time.sleep(300)
            if image_ops_status_log is not None and image_ops_status_log["failed"]:
                pi_logger.error(f"{operation[action]['err_message']} '{image_ops_status_log['failed']}'.")
            write_logs_to_file(image_ops_status_log, ops_status_log_file)
        else:
            pi_logger.info(f"No active request/changes done.")

        if image_ops_log is not None and image_ops_log["failed"]:
            pi_logger.error(f"{operation[action]['err_message']} '{image_ops_log['failed']}'.")
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
    logger = ImageShareLogger()
    powervs_workspaces_response, _error = get_powervs_workspaces(bearer_token)
    if powervs_workspaces_response:
        power_workspaces = powervs_workspaces_response.json()["workspaces"]
        for workspace in power_workspaces:
            image_ops_on_workspace(action, workspace, bearer_token, logger)
    else:
        logger.log_other(account, f"Failed to fetch the Power Virtual Server workspaces for {account}, {_error}")
    return logger


def image_ops_on_workspace(action, workspace, bearer_token, logger):
    """
    Manages image in a single workspace by importing or deleting it.

    Args:
        workspace: Dictionary containing workspace details.
        bearer_token: Bearer token for the account.
        logger: Logger object for logging operations.
        operation: String specifying the operation ('import' or 'delete').
    """
    workspace_details = {
        "name": workspace["name"],
        "id": workspace["id"],
        "crn": workspace["details"]["crn"],
        "base_url": workspace["location"]["url"],
    }

    boot_images_response, _error = get_boot_images(workspace, bearer_token)
    if not boot_images_response:
        logger.log_failure(workspace, _error)
        return

    # Check image status in a workspace
    image_found, is_active = process_image(CONFIG.get("image_details")["image_name"], boot_images_response.json()["images"])

    if action == "import":
        # check if there is already an image import job running
        latest_job_status, _error = get_cos_image_import_status(workspace_details, bearer_token)

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

    elif action == "delete":
        if image_found and is_active:
            # Delete boot image from workspace
            response, _error = delete_boot_image(image_found["imageID"], workspace, bearer_token)
            if response:
                logger.log_success(workspace)
            else:
                logger.log_failure(workspace, _error)
        else:
            logger.log_skipped(workspace, "The image does not exist.")

    elif action == "status":
        response, _err = get_cos_image_import_status(workspace_details, bearer_token)
        if response:
            if response.json()["status"]["state"] != "completed":
                pi_logger.error(f"Status: Image Operation not completed for workspace: {workspace_details}")
                logger.log_failure(workspace, _error)
            elif response.json()["status"]["state"] == "completed":
                pi_logger.info(f"Status: Image Operation completed for workspace: {workspace_details}")
                logger.log_success(workspace)
        else:
            pi_logger.error(f"Error fetching status: {_err}")
    else:
        logger.log_failure(workspace, "Invalid operation specified.")


def process_image(boot_image_name, boot_images):
    """
    Filter the concerned image from the list of boot images and checks if it's status is active.

    Args:
        boot_image_name: Name of the boot image to be imported or deleted.
        boot_images: List of boot images.
    Returns:
        The concerned image dictionary or None.
    """
    concerned_image = list(filter(lambda image: image.get("name", "") == boot_image_name, boot_images))
    if concerned_image:
        if concerned_image[0]["state"] == "active":
            return concerned_image[0], True
        else:
            return concerned_image[0], False
    else:
        return None, False


def write_logs_to_file(logger, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(logger, f, ensure_ascii=False, indent=4)
