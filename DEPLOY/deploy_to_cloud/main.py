# REGISTER MODEL AND DEPLOY AS WEBSERVICE
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice, Webservice
from azureml.exceptions import WebserviceException
import json


# Initialize Workspace
ws = Workspace.from_config('aml_config')
print("--- WORKSPACE: {} - Initialized ---\n".format(ws.name))


# Register Model
model = Model.register(model_path="./DEPLOY/deploy_to_cloud/sklearn_regression_model.pkl",
                       model_name="sklearn_regression_model.pkl",
                       tags={'area': "diabetes", 'type': "regression"},
                       description="Ridge regression model to predict diabetes",
                       workspace=ws)
print("--- MODEL: {} - Registered ---\n".format(model.name))


# Inference Configuration
inference_config = InferenceConfig(runtime= "python", 
                                   entry_script="./DEPLOY/deploy_to_cloud/score.py",
                                   conda_file="./DEPLOY/deploy_to_cloud/myenv.yml", 
                                   extra_docker_file_steps="./DEPLOY/deploy_to_cloud/helloworld.txt")
print("--- IMAGE CONFIG - Created ---\n")


# Deploy as a Webservice
deployment_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1)
aci_service_name = 'aciservice1'

try:
    # if you want to get existing service below is the command
    # since aci name needs to be unique in subscription deleting existing aci if any
    # we use aci_service_name to create azure aci
    service = Webservice(ws, name=aci_service_name)
    if service:
        service.delete()
except WebserviceException as e:
    print()

service = Model.deploy(ws, aci_service_name, [model], inference_config, deployment_config)

service.wait_for_deployment(True)
print(service.state)
print("--- WWEBSERVICE CREATED ---\n")


# Test webservice
test_sample = json.dumps({'data': [
    [1,2,3,4,5,6,7,8,9,10], 
    [10,9,8,7,6,5,4,3,2,1]
]})

test_sample_encoded = bytes(test_sample, encoding='utf8')
prediction = service.run(input_data=test_sample_encoded)
print(prediction)
print("--- WEBSERVICE TESTED ---\n")

"""
# Model Profiling

profile = Model.profile(ws, "profilename", [model], inference_config, test_sample)
profile.wait_for_profiling(True)
profiling_results = profile.get_results()
print(profiling_results)


# Model Packaging
package = Model.package(ws, [model], inference_config, generate_dockerfile=True)
package.wait_for_creation(show_output=True)
package.save("./DEPLOY/deploy_to_cloud/local_context_dir")

"""