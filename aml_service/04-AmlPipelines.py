import os, json, requests, datetime
import argparse
from azureml.core import Workspace, Experiment, Datastore
from azureml.core.runconfig import RunConfiguration, CondaDependencies
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import Pipeline, PipelineData, StepSequence
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import PublishedPipeline
from azureml.pipeline.core.graph import PipelineParameter
from azureml.core.compute import ComputeTarget

# from azureml.widgets import RunDetails
from azureml.core.authentication import AzureCliAuthentication

print("Pipeline SDK-specific imports completed")

cli_auth = AzureCliAuthentication()


parser = argparse.ArgumentParser("Pipeline")
parser.add_argument(
    "--pipeline_action",
    type=str,
    choices=["pipeline-test", "publish"],
    help="Determines if pipeline needs to run on small data set \
                                        or pipeline needs to be republished",
    #default="pipeline-test",
)

args = parser.parse_args()


# Get workspace
ws = Workspace.from_config(path="aml_config/config.json", auth=cli_auth)
def_blob_store = Datastore(ws, "workspaceblobstore")

# Get AML Compute name and Experiment Name
with open("aml_config/security_config.json") as f:
    config = json.load(f)

experiment_name = config["experiment_name"]
aml_cluster_name = config["aml_cluster_name"]
aml_pipeline_name = "training-pipeline"
#model_name = config["model_name"]
model_name = PipelineParameter(name="model_name", default_value="sklearn_regression_model.pkl")

source_directory = "code"

# Run Config
# Declare packages dependencies required in the pipeline (these can also be expressed as a YML file)
# cd = CondaDependencies.create(pip_packages=["azureml-defaults", 'tensorflow==1.8.0'])
cd = CondaDependencies("aml_config/conda_dependencies.yml")

run_config = RunConfiguration(conda_dependencies=cd)
aml_compute = ws.compute_targets[aml_cluster_name]
run_config.environment.docker.enabled = True
run_config.environment.spark.precache_packages = False

jsonconfigs = PipelineData("jsonconfigs", datastore=def_blob_store)

# Suffix for all the config files
config_suffix = datetime.datetime.now().strftime("%Y%m%d%H")
print("PipelineData object created")

# Create python script step to run the training/scoring main script
train = PythonScriptStep(
    name="Train New Model",
    script_name="training/train.py",
    compute_target=aml_compute,
    source_directory=source_directory,
    arguments=[
        "--config_suffix", config_suffix, 
        "--json_config", jsonconfigs, 
        "--model_name", model_name,
        ],
    runconfig=run_config,
    # inputs=[jsonconfigs],
    outputs=[jsonconfigs],
    allow_reuse=False,
)
print("Step Train created")

evaluate = PythonScriptStep(
    name="Evaluate New Model with Prod Model",
    script_name="evaluate/evaluate_model.py",
    compute_target=aml_compute,
    source_directory=source_directory,
    arguments=[
                "--config_suffix", config_suffix, 
                "--json_config", jsonconfigs,
                ],
    runconfig=run_config,
    inputs=[jsonconfigs],
    # outputs=[jsonconfigs],
    allow_reuse=False,
)
print("Step Evaluate created")

register_model = PythonScriptStep(
    name="Register New Trained Model",
    script_name="register/register_model.py",
    compute_target=aml_compute,
    source_directory=source_directory,
    arguments=[
        "--config_suffix", config_suffix, 
        "--json_config", jsonconfigs,
        "--model_name", model_name,
        ],
    runconfig=run_config,
    inputs=[jsonconfigs],
    # outputs=[jsonconfigs],
    allow_reuse=False,
)
print("Step register model created")

# Package model step is moved to Azure DevOps Release Pipeline
# package_model = PythonScriptStep(
#     name="Package Model as Scoring Image",
#     script_name="scoring/create_scoring_image.py",
#     compute_target=aml_compute,
#     source_directory=source_directory,
#     arguments=["--config_suffix", config_suffix, "--json_config", jsonconfigs],
#     runconfig=run_config,
#     inputs=[jsonconfigs],
#     # outputs=[jsonconfigs],
#     allow_reuse=False,
# )
# print("Packed the model into a Scoring Image")

# Create Steps dependency such that they run in sequence
evaluate.run_after(train)
register_model.run_after(evaluate)
#package_model.run_after(register_model)

steps = [register_model]


# Build Pipeline
pipeline1 = Pipeline(workspace=ws, steps=steps)
print("Pipeline is built")

# Validate Pipeline
pipeline1.validate()
print("Pipeline validation complete")


# Submit unpublished pipeline with small data set for test
if args.pipeline_action == "pipeline-test":
    pipeline_run1 = Experiment(ws, experiment_name).submit(
        pipeline1, regenerate_outputs=True
    )
    print("Pipeline is submitted for execution")
    pipeline_run1.wait_for_completion(show_output=True)


# RunDetails(pipeline_run1).show()


# Define pipeline parameters
# run_env = PipelineParameter(
#   name="dev_flag",
#   default_value=True)

# dbname = PipelineParameter(
#   name="dbname",
#   default_value='opex')


# Publish Pipeline
if args.pipeline_action == "publish":
    published_pipeline1 = pipeline1.publish(
        name=aml_pipeline_name, description="Model training/retraining pipeline"
    )
    print(
        "Pipeline is published as rest_endpoint {} ".format(
            published_pipeline1.endpoint
        )
    )
    # write published pipeline details as build artifact
    pipeline_config = {}
    pipeline_config["pipeline_name"] = published_pipeline1.name
    pipeline_config["rest_endpoint"] = published_pipeline1.endpoint
    pipeline_config["experiment_name"] = "published-pipeline-exp"  # experiment_name
    with open("aml_config/pipeline_config.json", "w") as outfile:
        json.dump(pipeline_config, outfile)
