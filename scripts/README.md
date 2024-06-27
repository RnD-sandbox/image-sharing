---

# IBMCloud Power Virtual Server Image Sharing

This guide provides instruction on how to execute this Python module to import/delete custom OS images in Power Virtual Server Workspace

## Prerequisites

- Custom OS images loaded into a COS bucket
- IBM cloud enterprise account
- Target IBM Cloud account linked to the enterprise account with 'Trusted Profiles'
- Trget account IDs or the name of an account group
- Python 3.x installed on your machine.
- `config.yaml` file with the required configuration.

## Install Dependencies

```bash
pip3 install requests
pip3 install boto3
pip3 install pyyaml
```

## Usage

```bash
$ python3 main.py
```
