import yaml
import os.path

CONFIG = {}
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Open and read the YAML file
with open(parent_dir + "/config.yaml") as file:
    CONFIG = yaml.safe_load(file)

