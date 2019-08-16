import os, json, sys
from azureml.core import Workspace
from azureml.core.authentication import AzureCliAuthentication

cli_auth = AzureCliAuthentication()

# Get workspace
ws = Workspace.from_config(auth=cli_auth)

# Get the latest image details
latest_image = ws.images
name, version = latest_image.get(list(latest_image)[0]).id.split(':')

# Writing the image details to /aml_config/image.json
image_json = {}
image_json["image_name"] = name
image_json["image_version"] = int(version)
with open("aml_config/image.json", "w") as outfile:
    json.dump(image_json, outfile)
