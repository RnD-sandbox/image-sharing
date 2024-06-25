import os
from src.api_requests import get_request, post_request


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
    response, _err = post_request(req_url, req_headers, req_params)
    return response, _err


def get_trusted_profiles(access_token):
    req_url = "https://iam.cloud.ibm.com/identity/profiles"
    req_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    req_params = {"access_token": access_token}
    response, _err = get_request(req_url, req_headers, req_params)
    return response, _err


def get_account_group_list(enterprise_id, iam_token):
    req_url = "https://enterprise.cloud.ibm.com/v1/account-groups"
    req_headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json",
    }
    req_params = {"enterprise_id": enterprise_id, "include_deleted": "false"}
    response, _err = get_request(req_url, req_headers, req_params)
    return response, _err


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
    response, _err = get_request(req_url, req_headers, req_params)
    return response, _err


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
    response, _err = post_request(req_url, req_headers, data=req_data)
    return response, _err
