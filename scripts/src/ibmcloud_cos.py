import boto3
from botocore.exceptions import ClientError
from src.log_utils import *
import sys

pi_logger = logging.getLogger("logger")


def object_exists_in_ibm_cos(access_key, secret_key, region, bucket, object_key):
    # Initialize the S3 client with HMAC credentials
    endpoint_url = f"https://s3.{region}.cloud-object-storage.appdomain.cloud"
    standardized_resource = f"/{bucket}/{object_key}"
    request_url = endpoint_url + standardized_resource
    s3 = boto3.client(
        "s3",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        endpoint_url=endpoint_url,
    )
    pi_logger.info(
        f"Start: Checking if s3 credentials are correct and object exists in bucket. Sending requestURL = {request_url}"
    )

    try:
        # Attempt to retrieve metadata for the object
        s3.head_object(Bucket=bucket, Key=object_key)
        pi_logger.info(
            f"End: Checked s3 credentials are correct and object exists in bucket."
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            pi_logger.error(
                f"Object '{object_key}' does not exist in bucket '{bucket}'. Status code: 404"
            )
            sys.exit(1)
        else:
            pi_logger.error(
                f"Error checking object in S3: {e.response['Error']['Message']}. Status code: {e.response['ResponseMetadata']['HTTPStatusCode']}"
            )
            sys.exit(1)
