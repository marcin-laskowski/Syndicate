#!/bin/bash


# get User credentials
#python ./aml_config/

# create workspace
python aml_service/00-WorkSpace.py

# register model
python aml_service/20-RegisterModel.py