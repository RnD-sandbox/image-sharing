import json
import os
from src.api_requests import *
from src.log_utils import *
from src.constants import CONFIG


def get_powervs_workspaces(bearer_token):
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
    }
    request_url = "https://us-east.power-iaas.cloud.ibm.com/v1/workspaces"
    response, _err = get_request(request_url, request_headers, None)
    return response, _err


def get_boot_images(workspace, bearer_token):
    workspace_id = workspace["id"]
    base_url = workspace["location"]["url"]
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/images"
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace["details"]["crn"],
    }
    response, _err = get_request(request_url, request_headers, None)
    return response, _err


def import_boot_image(workspace, bearer_token):
    workspace_id = workspace["id"]
    base_url = workspace["location"]["url"]
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/cos-images"
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace["details"]["crn"],
    }
    request_data = {
        "imageName": CONFIG.get("image_details")["image_name"],
        "region": CONFIG.get("cos_bucket_details")["cos_region"],
        "imageFilename": CONFIG.get("cos_bucket_details")["cos_image_file_name"],
        "bucketName": CONFIG.get("cos_bucket_details")["cos_bucket"],
        "accessKey": os.getenv("COS_ACCESS_KEY"),
        "secretKey": os.getenv("COS_SECRET_KEY"),
        "storageType": "tier3",
    }

    import_details = {
        "licenseType": CONFIG.get("image_details", {}).get("license_type", ""),
        "product": CONFIG.get("image_details", {}).get("product", ""),
        "vendor": CONFIG.get("image_details", {}).get("vendor", ""),
    }

    # Check if any of the import details are empty
    if all(import_details.values()):
        request_data["importDetails"] = import_details

    response, _err = post_request(request_url, request_headers, json.dumps(request_data))
    return response, _err


def delete_boot_image(boot_image_id, workspace, bearer_token):
    workspace_id = workspace["id"]
    base_url = workspace["location"]["url"]
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/images/{boot_image_id}"
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace["details"]["crn"],
    }
    response, _err = delete_request(request_url, request_headers, None)
    return response, _err


def get_cos_image_import_status(workspace_details, bearer_token):
    workspace_id = workspace_details["id"]
    base_url = workspace_details["base_url"]
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/cos-images"
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace_details["crn"],
    }
    response, _err = get_request(request_url, request_headers)
    return response, _err
