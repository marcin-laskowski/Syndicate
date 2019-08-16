import os, json, requests, datetime, sys
import argparse
from azureml.core.authentication import AzureCliAuthentication

try:
    with open("aml_config/pipeline_config.json") as f:
        config = json.load(f)
    with open("aml_config/security_config.json") as f:
        security_config = json.load(f)
except:
    print("No pipeline config found")
    sys.exit(0)

# Run a published pipeline
cli_auth = AzureCliAuthentication()
aad_token = cli_auth.get_authentication_header()
rest_endpoint1 = config["rest_endpoint"]
experiment_name = config["experiment_name"]
model_name = security_config["model_name"]

print(rest_endpoint1)

response = requests.post(
    rest_endpoint1, headers=aad_token, 
    json={"ExperimentName": experiment_name,
    "ParameterAssignments": {"model_name":model_name}}
)

run_id = response.json()["Id"]
print(run_id)
print("Pipeline run initiated")
