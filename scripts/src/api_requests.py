import requests
from src.log_utils import *
from requests.exceptions import HTTPError

pi_logger = logging.getLogger('my_logger')

def get_request(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        pi_logger.info(f"GET request to {url} successful. Status code: {response.status_code}")
        return response, None
    except HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        pi_logger.error(f"Error during GET request to {url}: {err}")
        return None, f"Error during GET request to {url}: {err}"

def post_request(url, headers=None, data=None):
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        pi_logger.info(f"POST request to {url} successful. Status code: {response.status_code}")
        return response, None
    except HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        pi_logger.error(f"Error during GET request to {url}: {err}")
        return None, f"Error during GET request to {url}: {err}"

def delete_request(url, headers=None, data=None):
    try:
        response = requests.delete(url, headers=headers, data=data)
        response.raise_for_status()
        pi_logger.info(f"DELETE request to {url} successful. Status code: {response.status_code}")
        return response, None
    except HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        pi_logger.error(f"Error during GET request to {url}: {err}")
        return None, f"Error during GET request to {url}: {err}"

