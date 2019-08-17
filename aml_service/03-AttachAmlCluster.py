from azureml.core import Workspace
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core.authentication import AzureCliAuthentication
import os, json

cli_auth = AzureCliAuthentication()

# Get workspace
#ws = Workspace.from_config(auth=cli_auth)
ws = Workspace.from_config('aml_config')


# Read the New VM Config
with open("aml_config/config.json") as f:
    config = json.load(f)

aml_cluster_name = config["aml_cluster_name"]

# un-comment the below lines if you want to put AML Compute under Vnet. Also update /aml_config/security_config.json
# vnet_resourcegroup_name = config['vnet_resourcegroup_name']
# vnet_name = config['vnet_name']
# subnet_name = config['subnet_name']

# Verify that cluster does not exist already
try:
    cpu_cluster = ComputeTarget(workspace=ws, name=aml_cluster_name)
    print("Found existing cluster, use it.")
except ComputeTargetException:
    compute_config = AmlCompute.provisioning_configuration(
        vm_size="STANDARD_D2_V2",
        vm_priority="dedicated",
        min_nodes=1,
        max_nodes=3,
        idle_seconds_before_scaledown="300",
        #    #Uncomment the below lines for VNet support
        #    vnet_resourcegroup_name=vnet_resourcegroup_name,
        #    vnet_name=vnet_name,
        #    subnet_name=subnet_name
    )
    cpu_cluster = ComputeTarget.create(ws, aml_cluster_name, compute_config)

cpu_cluster.wait_for_completion(show_output=True)

print("----- AML COMPUTE CLUSTER ATTACHED ----- \n")
