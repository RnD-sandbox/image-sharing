import yaml
import os.path
from jsonschema import validate
from src.log_utils import pi_logger
import sys

CONFIG = {}
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Open and read the YAML file
with open(parent_dir + "/config.yaml") as file:
    CONFIG = yaml.safe_load(file)


def validate_config():

    # Open and read the YAML file
    with open(os.path.dirname(__file__) + "/config_schema.yaml") as file:
        schema = yaml.safe_load(file)
        validate(CONFIG, schema)

        licenseType = CONFIG.get("image_import_details")["license_type"]
        product = CONFIG.get("image_import_details")["product"]
        vendor = CONFIG.get("image_import_details")["vendor"]

        # Accepted values
        valid_licenseTypes = ["byol"]
        valid_products = ["Hana", "Netweaver"]
        valid_vendors = ["SAP"]

        # Check if all variables are not null or empty or all are null or empty
        if (licenseType and product and vendor) or (
            not licenseType and not product and not vendor
        ):
            # Check if the values are valid
            if (
                (licenseType in valid_licenseTypes or not licenseType)
                and (product in valid_products or not product)
                and (vendor in valid_vendors or not vendor)
            ):
                if licenseType and product and vendor:
                    valid_licenseType = licenseType
                    valid_product = product
                    valid_vendor = vendor
                    pi_logger.info(
                        f"License Type: {valid_licenseType}, Product: {valid_product}, Vendor: {valid_vendor}"
                    )
                else:
                    valid_licenseType = valid_product = valid_vendor = None
                    pi_logger.info("LicenseType, product and vendor are null or empty.")
            else:
                pi_logger.error("ERROR: LicenseType, product and vendor has invalid values. Supported values are license_type:byol, product:Hana,Netweaver, vendor:SAP")
                sys.exit(1)
        else:
            pi_logger.error(
                "Warning: All three variables must be set together or be null/empty together."
            )
            sys.exit(1)
