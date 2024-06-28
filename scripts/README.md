# IBMCloud Power Virtual Server Image Sharing

This guide provides instruction on how to execute this Python module to import/delete custom OS images in Power Virtual Server Workspace

## Prerequisites

1. IBM cloud API key of service ID in the Enterprise account. 
2. Enterprise account ID.
3. Target IBM Cloud account linked to the enterprise account with 'Trusted Profiles'
4. Target account IDs or the name of an account group to which image must be shared.
5. Custom OS images loaded into a IBM Cloud Object Storage(COS) bucket
6. IBM Cloud COS Credentials
7. Python 3.x installed on your machine.
8. `config.yaml` file with the required configuration.

## Install Dependencies

```bash
pip3 install requests
pip3 install boto3
pip3 install pyyaml
pip3 install jsonschema
```

## Usage
1. Export environment variables:
    ```
    export IBMCLOUD_API_KEY=xxxxxxxx
    export COS_ACCESS_KEY=xxxxxxxxxx
    export COS_SECRET_KEY=xxxxxxxxxx
    ```
2. Edit the `config.yaml` file found in the folder according to your requirements.
3. Execute the script using command: `python3 main.py`
