import os
import json
from src.api_requests import *
import logging


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
        "imageName": os.getenv("POWERVS_IMAGE_NAME"),
        "region": os.getenv("COS_REGION"),
        "imageFilename": os.getenv("COS_IMAGE_FILE_NAME"),
        "bucketName": os.getenv("COS_BUCKET_NAME"),
        "accessKey": os.getenv("COS_ACCESS_KEY"),
        "secretKey": os.getenv("COS_SECRET_KEY"),
        "storageType": os.getenv("COS_STORAGE_TYPE"),
    }
    response, _err = post_request(
        request_url, request_headers, json.dumps(request_data)
    )
    return response, _err


def delete_boot_image(boot_image_id, workspace, bearer_token):
    workspace_id = workspace["id"]
    base_url = workspace["location"]["url"]
    request_url = (
        f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/images/{boot_image_id}"
    )
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace["details"]["crn"],
    }
    response, _err = delete_request(request_url, request_headers, None)
    return response, _err
