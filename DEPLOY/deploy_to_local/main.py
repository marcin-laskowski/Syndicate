# REGISTER MODEL AND DEPLOY LOCALLY
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.environment import Environment
from azureml.core.model import InferenceConfig
from azureml.core.webservice import LocalWebservice



# Initialize Workspace
ws = Workspace.from_config('aml_config')
print("--- WORKSPACE: {} - Initialized ---\n".format(ws.name))


# Register Model
model = Model.register(model_path="./DEPLOY/deploy_to_local/sklearn_regression_model.pkl",
                       model_name="sklearn_regression_model.pkl",
                       tags={'area': "diabetes", 'type': "regression"},
                       description="Ridge regression model to predict diabetes",
                       workspace=ws)
print("--- MODEL: {} - Registered ---\n".format(model.name))


# Environment
environment = Environment("LocalDeploy")
environment.python.conda_dependencies = CondaDependencies("./DEPLOY/deploy_to_local/myenv.yml")
print("--- ENVIRONMENT - Created ---\n")


# Inference Configuration
inference_config = InferenceConfig(entry_script="./DEPLOY/deploy_to_local/score.py",
                                   environment=environment)
print("--- INFERENCE CONFIG - Created ---\n")


# Webservice
# (This is optional, if not provided Docker will choose a random unused port)
deployment_config = LocalWebservice.deploy_configuration(port=6789)

local_service = Model.deploy(ws, "test", [model], inference_config, deployment_config)

local_service.wait_for_deployment()

print('Local service port: {}'.format(local_service.port))
print("--- WEBSERVICE - Created ---\n")


# Status and Container Logs
#print(local_service.get_logs())


# Test Serivce
import json

sample_input = json.dumps({
    'data': [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    ]
})

sample_input = bytes(sample_input, encoding='utf-8')
local_service.run(input_data=sample_input)
print("--- WEBSERVICE TESTED ---\n")


# Model Packaging
package = Model.package(ws, [model], inference_config, generate_dockerfile=True)
package.wait_for_creation(show_output=True)
package.save("./DEPLOY/deploy_to_local/local_context_dir")


