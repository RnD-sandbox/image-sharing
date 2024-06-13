import os
import json
from src.api_requests import *
import logging

def get_powervs_workspaces(bearer_token):
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json"
    }
    request_url = "https://us-east.power-iaas.cloud.ibm.com/v1/workspaces"
    response, _err = get_request(request_url, request_headers, None)
    return response, _err

def get_boot_images(workspace, bearer_token):
    #print(f"Workspace - {workspace['name']}, Account - {account['name']}")
    workspace_id = workspace['id']
    base_url = workspace['location']['url']
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/images"
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace['details']['crn']
    }
    response, _err = get_request(request_url, request_headers, None)
    return response, _err

def import_boot_image(workspace, bearer_token):
    #print(f"Workspace - {workspace['name']}, Account - {account['name']}")
    workspace_id = workspace['id']
    base_url = workspace['location']['url']
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/cos-images"
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace['details']['crn']
    }
    request_data = {
        "imageName": "my-image-catalog-name",         # TODO - change to var
        "region": "eu-de",                            # TODO - change to var
        "imageFilename": "rh-9-2-sap-2703.ova.gz",    # TODO - change to var
        "bucketName": "sap-hyperscalar",              # TODO - change to var
        "accessKey": os.getenv('ACCESS_KEY'),
        "secretKey": os.getenv('SECRET_KEY'),
        "storageType": "tier0"
    }
    response, _err = post_request(request_url, request_headers, json.dumps(request_data))
    return response, _err

def delete_boot_image(boot_image_id, workspace, bearer_token):
    workspace_id = workspace['id']
    base_url = workspace['location']['url']
    request_url = f"{base_url}/pcloud/v1/cloud-instances/{workspace_id}/images/{boot_image_id}" 
    request_headers = {
        "Authorization": bearer_token,
        "Content-Type": "application/json",
        "CRN": workspace['details']['crn']
    }
    response, _err = delete_request(request_url, request_headers, None)
    return response, _err
