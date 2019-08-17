#!/bin/bash


# get User credentials
#python ./aml_config/

# create workspace
python3 aml_service/00-WorkSpace.py

# attach compute cluster
python3 aml_service/03-AttachAmlCluster.py

# register model
#python aml_service/20-RegisterModel.py

