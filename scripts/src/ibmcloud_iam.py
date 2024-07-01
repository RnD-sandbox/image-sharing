import os
import sys

from src.api_requests import get_request, post_request
from src.log_utils import *

pi_logger = logging.getLogger("logger")


def generate_bearer_token(ibmcloud_api_key):
    req_url = "https://iam.cloud.ibm.com/identity/token"
    req_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    req_params = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": ibmcloud_api_key,
    }
    response, error = post_request(req_url, req_headers, req_params)
    return response, error


def get_trusted_profiles(access_token):
    req_url = "https://iam.cloud.ibm.com/identity/profiles"
    req_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    req_params = {"access_token": access_token}
    pi_logger.info(f"Start: Fetching the trusted profiles ...")
    response, error = get_request(req_url, req_headers, req_params)

    if response:
        pi_logger.info(f"End: Fetched all trusted profiles.")
        return response.json()["profiles"]
    else:
        pi_logger.error(f"Error Failed to get trusted profiles: {error}")
        sys.exit(1)


def get_account_group_list(enterprise_id, iam_token):
    req_url = "https://enterprise.cloud.ibm.com/v1/account-groups"
    req_headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json",
    }
    req_params = {"enterprise_id": enterprise_id, "include_deleted": "false"}
    pi_logger.info(
        f"Start: Fetching account groups in Enterprise account with ID {enterprise_id} ..."
    )
    response, error = get_request(req_url, req_headers, req_params)

    if response:
        pi_logger.info(
            f"End: Fetched account groups in Enterprise account with ID {enterprise_id}"
        )
        return response.json()["resources"]
    else:
        pi_logger.error(
            f"Error fetching the account groups for account ID {enterprise_id}. Invalid Enterprise account ID for the API key provided: {error}"
        )
        sys.exit(1)


def get_account_list(enterprise_id, account_group_id, iam_token):
    req_url = "https://enterprise.cloud.ibm.com/v1/accounts"
    req_headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json",
    }
    req_params = {
        "enterprise_id": enterprise_id,
        "account_group_id": account_group_id,
        "include_deleted": "false",
    }

    pi_logger.info(
        f"Start: Fetching list of accounts under the account group id {account_group_id} ..."
    )
    response, error = get_request(req_url, req_headers, req_params)
    if response:
        pi_logger.info(
            f"End: Fetched list of accounts under the account group id {account_group_id} ..."
        )
        return response.json()["resources"]
    else:
        pi_logger.error(
            f"Error fetching list of accounts under the account group id {account_group_id}: {error}"
        )
        sys.exit(1)


def get_child_account_access_token(profile_id, account_id, enterprise_access_token):
    req_url = "https://iam.cloud.ibm.com/identity/token"
    req_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    req_data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:assume",
        "access_token": enterprise_access_token,
        "profile_id": profile_id,
        "account_id": account_id,
    }
    response, error = post_request(req_url, req_headers, data=req_data)
    return response, error
