import requests
import logging
from requests.exceptions import HTTPError

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_request(url, headers=None, params=None):
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        logging.info(f"GET request to {url} successful. Status code: {response.status_code}")
        return response, None
    except HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        logging.error(f"Error during GET request to {url}: {err}")
        return None, f"Error during GET request to {url}: {err}"

def post_request(url, headers=None, data=None):
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        logging.info(f"POST request to {url} successful. Status code: {response.status_code}")
        return response, None
    except HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        logging.error(f"Error during GET request to {url}: {err}")
        return None, f"Error during GET request to {url}: {err}"

def delete_request(url, headers=None, data=None):
    try:
        response = requests.delete(url, headers=headers, data=data)
        response.raise_for_status()
        logging.info(f"DELETE request to {url} successful. Status code: {response.status_code}")
        return response, None
    except HTTPError as http_err:
        return None, f"HTTP error occurred: {http_err}"
    except Exception as err:
        logging.error(f"Error during GET request to {url}: {err}")
        return None, f"Error during GET request to {url}: {err}"

