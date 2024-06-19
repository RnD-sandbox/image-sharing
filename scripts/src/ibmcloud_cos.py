import datetime
import hashlib
import hmac
import requests
from src.log_utils import *
import sys

pi_logger = logging.getLogger("my_logger")


def object_exists_in_ibm_cos(access_key, secret_key, region, bucket, object_key):
    # hashing and signing methods
    def hash(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    # region is a wildcard value that takes the place of the AWS region value
    # as COS doesn't use the same conventions for regions, this parameter can accept any string
    def createSignatureKey(key, datestamp, region, service):

        keyDate = hash(("AWS4" + key).encode("utf-8"), datestamp)
        keyString = hash(keyDate, region)
        keyService = hash(keyString, service)
        keySigning = hash(keyService, "aws4_request")
        return keySigning

    # assemble the standardized request
    time = datetime.datetime.utcnow()
    timestamp = time.strftime("%Y%m%dT%H%M%SZ")
    datestamp = time.strftime("%Y%m%d")
    host = f"s3.{region}.cloud-object-storage.appdomain.cloud"
    endpoint = f"https://s3.{region}.cloud-object-storage.appdomain.cloud"
    http_method = "GET"

    standardized_resource = f"/{bucket}/{object_key}"
    standardized_querystring = ""
    standardized_headers = "host:" + host + "\n" + "x-amz-date:" + timestamp + "\n"
    signed_headers = "host;x-amz-date"
    payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()

    standardized_request = (
        f"{http_method}\n"
        f"{standardized_resource}\n"
        f"{standardized_querystring}\n"
        f"{standardized_headers}\n"
        f"{signed_headers}\n"
        f"{payload_hash}"
    ).encode("utf-8")

    # assemble string-to-sign
    hashing_algorithm = "AWS4-HMAC-SHA256"
    credential_scope = f"{datestamp}/{region}/s3/aws4_request"
    sts = (
        f"{hashing_algorithm}\n"
        f"{timestamp}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(standardized_request).hexdigest()}"
    )

    # generate the signature
    signature_key = createSignatureKey(secret_key, datestamp, region, "s3")
    signature = hmac.new(
        signature_key, (sts).encode("utf-8"), hashlib.sha256
    ).hexdigest()

    # assemble all elements into the 'authorization' header
    v4auth_header = (
        f"{hashing_algorithm} "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    # create and send the request
    headers = {"x-amz-date": timestamp, "Authorization": v4auth_header}
    # the 'requests' package automatically adds the required 'host' header
    request_url = endpoint + standardized_resource + standardized_querystring

    pi_logger.info(
        f"Start: Checking if s3 credentials are correct and object exists in bucket. Sending requestURL = {request_url}"
    )
    response = requests.get(request_url, headers=headers)

    if response.status_code == 200:
        pi_logger.info(
            f"End: Checked s3 credentials are correct and object exists in bucket. Response code: {response.status_code}"
        )
    else:
        pi_logger.error(
            f"Error wrong s3 credentials or wrong image name or wrong bucket name. Status code: {response.status_code}"
        )
        sys.exit(1)
